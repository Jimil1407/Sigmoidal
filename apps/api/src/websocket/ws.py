from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
import os
import asyncio
import websockets
import json
import httpx
from jose import jwt

API_KEY = os.getenv("TWELVE_DATA_API_KEY")

class ConnectionManager:
    def __init__(self):
        self.active_connections = {}  
        self.symbol_subscriptions = {} 
        self.twelve_data_ws = None
        self.subscribed_symbols = set()
        self.quote_data = {}  # Store comprehensive quote data for each symbol

    async def connect(self, websocket, userId):
        await websocket.accept()
        self.active_connections[userId] = websocket 

    def disconnect(self, userId):
        self.active_connections.pop(userId, None)
        for s in list(self.symbol_subscriptions):
            self.symbol_subscriptions[s].discard(userId)
            if not self.symbol_subscriptions[s]:
                del self.symbol_subscriptions[s]

    async def broadcast(self, symbol, data):
        users = self.symbol_subscriptions.get(symbol, set())
        stale_users = []
        for userId in list(users):
            ws = self.active_connections.get(userId)
            if not ws:
                stale_users.append(userId)
                continue
            try:
                await ws.send_json(data)
            except Exception:
                # Drop failing connections and clean up subscriptions
                stale_users.append(userId)
        for uid in stale_users:
            self.disconnect(uid)

    async def connect_to_twelve_data(self):
        """Connect to Twelve Data WebSocket"""
        if self.twelve_data_ws:
            return
            
        if not API_KEY:
            print("TWELVE_DATA_API_KEY not configured")
            return
            
        try:
            uri = f"wss://ws.twelvedata.com/v1/quotes/price?apikey={API_KEY}"
            print(f"Connecting to Twelve Data WebSocket: {uri[:50]}...")
            self.twelve_data_ws = await websockets.connect(uri)
            print("Successfully connected to Twelve Data WebSocket")
            
            # Start listening for messages
            asyncio.create_task(self.listen_to_twelve_data())
            
            # Start periodic quote data refresh
            asyncio.create_task(self.refresh_quote_data_periodically())
            
        except Exception as e:
            print(f"Failed to connect to Twelve Data WebSocket: {e}")
            self.twelve_data_ws = None

    async def listen_to_twelve_data(self):
        """Listen for messages from Twelve Data WebSocket"""
        try:
            async for message in self.twelve_data_ws:
                try:
                    data = json.loads(message)
                    print(f"Received from Twelve Data: {data}")
                    
                    if data.get('event') == 'price':
                        symbol = data.get('symbol')
                        current_price = float(data.get('price', 0))
                        print(f"Price update for {symbol}: ${current_price}")
                        
                        # Get comprehensive quote data if we don't have it or it's stale
                        quote_data = self.quote_data.get(symbol)
                        if not quote_data:
                            quote_data = await get_comprehensive_quote(symbol)
                            if quote_data:
                                self.quote_data[symbol] = quote_data
                        
                        # Use comprehensive data if available, otherwise use real-time price
                        if quote_data:
                            # Update current price with real-time data
                            quote_data['current'] = current_price
                            
                            # Broadcast comprehensive data
                            broadcast_data = {
                                "type": "market_data",
                                "symbol": symbol,
                                "current": current_price,
                                "high": quote_data['high'],
                                "low": quote_data['low'],
                                "change": quote_data['change'],
                                "percent_change": quote_data['percent_change']
                            }
                            print(f"Broadcasting data for {symbol}: {broadcast_data}")
                            await self.broadcast(symbol, broadcast_data)
                        else:
                            # Fallback to basic price data
                            broadcast_data = {
                                "type": "market_data",
                                "symbol": symbol,
                                "current": current_price,
                                "high": current_price,
                                "low": current_price,
                                "change": 0,
                                "percent_change": 0
                            }
                            print(f"Broadcasting fallback data for {symbol}: {broadcast_data}")
                            await self.broadcast(symbol, broadcast_data)
                        
                except json.JSONDecodeError as e:
                    print(f"JSON decode error: {e}")
                except Exception as e:
                    print(f"Error processing message: {e}")
                    
        except websockets.exceptions.ConnectionClosed:
            self.twelve_data_ws = None
        except Exception:
            self.twelve_data_ws = None

    async def refresh_quote_data_periodically(self):
        """Periodically refresh quote data to keep high/low/change current"""
        while True:
            try:
                await asyncio.sleep(30)  # Refresh every 30 seconds
                symbols_to_refresh = list(self.quote_data.keys())
                
                for symbol in symbols_to_refresh:
                    try:
                        new_quote_data = await get_comprehensive_quote(symbol)
                        if new_quote_data:
                            # Keep the current real-time price, update other data
                            current_price = self.quote_data[symbol].get('current', new_quote_data['current'])
                            new_quote_data['current'] = current_price
                            self.quote_data[symbol] = new_quote_data
                    except Exception:
                        pass
                        
            except Exception:
                pass

    async def subscribe_to_symbol(self, symbol):
        """Subscribe to a symbol on Twelve Data WebSocket"""
        print(f"Attempting to subscribe to symbol: {symbol}")
        
        if not self.twelve_data_ws:
            print("No Twelve Data WebSocket connection, attempting to connect...")
            await self.connect_to_twelve_data()
            
        if self.twelve_data_ws and symbol not in self.subscribed_symbols:
            print(f"Subscribing to {symbol} on Twelve Data WebSocket")
            
            # Fetch comprehensive quote data first
            quote_data = await get_comprehensive_quote(symbol)
            if quote_data:
                self.quote_data[symbol] = quote_data
                print(f"Fetched initial quote data for {symbol}: {quote_data}")
            else:
                print(f"Failed to fetch initial quote data for {symbol}")
            
            # Subscribe to real-time price updates
            subscribe_message = {
                "action": "subscribe",
                "params": {
                    "symbols": symbol
                }
            }
            print(f"Sending subscribe message: {subscribe_message}")
            await self.twelve_data_ws.send(json.dumps(subscribe_message))
            self.subscribed_symbols.add(symbol)
            print(f"Successfully subscribed to {symbol}")
        else:
            if not self.twelve_data_ws:
                print(f"Failed to establish Twelve Data WebSocket connection for {symbol}")
            else:
                print(f"Already subscribed to {symbol}")

    async def unsubscribe_from_symbol(self, symbol):
        """Unsubscribe from a symbol on Twelve Data WebSocket"""
        if self.twelve_data_ws and symbol in self.subscribed_symbols:
            unsubscribe_message = {
                "action": "unsubscribe",
                "params": {
                    "symbols": symbol
                }
            }
            await self.twelve_data_ws.send(json.dumps(unsubscribe_message))
            self.subscribed_symbols.discard(symbol)

async def get_comprehensive_quote(symbol):
    """Get comprehensive quote data including high, low, change, etc."""
    try:
        url = f"https://api.twelvedata.com/quote?symbol={symbol}&apikey={API_KEY}"
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                if "close" in data and "high" in data and "low" in data:
                    return {
                        "current": float(data.get("close", 0)),
                        "high": float(data.get("high", 0)),
                        "low": float(data.get("low", 0)),
                        "change": float(data.get("change", 0)),
                        "percent_change": float(data.get("percent_change", 0)),
                        "open": float(data.get("open", 0)),
                        "volume": int(float(data.get("volume", 0))) if data.get("volume") else 0
                    }
    except Exception:
        pass
    return None

manager = ConnectionManager() 


def register_websocket(app):
    @app.websocket("/ws/getlivedata")
    async def websocket_endpoint(websocket: WebSocket, token: str = Query(None)):
        # Try query param first, then header
        if not token:
            auth_header = websocket.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header[7:]  # Remove "Bearer " prefix
            else:
                token = auth_header
        
        if not token:
            print("No token provided")
            await websocket.close(code=1008, reason="No authentication token")
            return
            
        jwt_secret = os.getenv("JWT_SECRET")
        if not jwt_secret:
            print("JWT_SECRET not configured")
            await websocket.close(code=1011, reason="Server configuration error")
            return
            
        try:
            payload = jwt.decode(token, jwt_secret, algorithms=["HS256"])
            userId = payload.get("id")
            if not userId:
                print("No user ID in token")
                await websocket.close(code=1008, reason="Invalid token")
                return
        except Exception as e:
            print(f"JWT decode error: {e}")
            await websocket.close(code=1008, reason="Invalid token")
            return
        await manager.connect(websocket, userId)
        
        # Connect to Twelve Data WebSocket if not already connected
        await manager.connect_to_twelve_data()
        
        try:
            while True:
                message = await websocket.receive_json()
                print(f"Received WebSocket message from user {userId}: {message}")
                
                if message['type'] == "subscribe":
                    symbol = message["symbol"].upper()
                    print(f"User {userId} subscribing to {symbol}")
                    manager.symbol_subscriptions.setdefault(symbol, set()).add(userId)
                    
                    # Subscribe to symbol on Twelve Data WebSocket
                    await manager.subscribe_to_symbol(symbol)
                    
                    response = {"status": "subscribed", "symbol": symbol}
                    print(f"Sending response: {response}")
                    await websocket.send_json(response)
                    
                elif message['type'] == "unsubscribe":
                    symbol = message["symbol"].upper()
                    print(f"User {userId} unsubscribing from {symbol}")
                    manager.symbol_subscriptions.get(symbol, set()).discard(userId)
                    
                    # Unsubscribe from symbol on Twelve Data WebSocket if no other users are subscribed
                    if not manager.symbol_subscriptions.get(symbol, set()):
                        await manager.unsubscribe_from_symbol(symbol)
                    
                    response = {"status": "unsubscribed", "symbol": symbol}
                    print(f"Sending response: {response}")
                    await websocket.send_json(response)
                else:
                    print(f"Unknown message type: {message.get('type')}")
                    
        except WebSocketDisconnect:
            print(f"WebSocket disconnected for user {userId}")
            manager.disconnect(userId)
        except Exception as e:
            print(f"WebSocket error for user {userId}: {e}")
            manager.disconnect(userId)




