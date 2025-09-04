from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import os
import httpx
import asyncio
from jose import jwt

API_KEY = os.getenv("TWELVE_DATA_API_KEY")

class ConnectionManager:
    def __init__(self):
        self.active_connections = {}  
        self.symbol_subscriptions = {} 

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

async def get_twelve_price(symbol):
    url = f"https://api.twelvedata.com/price?symbol={symbol}&apikey={API_KEY}"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        data = resp.json()
        if "price" in data:
            return float(data["price"])
        else:
            return None

manager = ConnectionManager()
        
async def polling_twelve_data():
    while True:
        symbols = list(manager.symbol_subscriptions.keys())
        for symbol in symbols:
            price = await get_twelve_price(symbol)
            if price is not None:
                await manager.broadcast(symbol, {
                    "type": "market_data",
                    "symbol": symbol,
                    "price": price,
                })
            else:
                await manager.broadcast(ValueError,{
                    "Error": ValueError
                })
        await asyncio.sleep(5) 


def register_websocket(app):
    @app.websocket("/ws/getlivedata")
    async def websocket_endpoint(websocket: WebSocket):
        # Try header first; browsers can't set custom headers for WS, so support query param too
        token = websocket.headers.get("Authorization") or websocket.query_params.get("token")
        try:
            userId = jwt.decode(token, os.getenv("JWT_SECRET"), algorithms=["HS256"]) ["id"]
        except Exception:
            await websocket.close()
            return
        await manager.connect(websocket, userId)
        try:
            while True:
                message = await websocket.receive_json()
                if message['type'] == "subscribe":
                    symbol = message["symbol"].upper()
                    manager.symbol_subscriptions.setdefault(symbol, set()).add(userId)
                    await websocket.send_json({"status": "subscribed", "symbol": symbol})
                elif message['type'] == "unsubscribe":
                    symbol = message["symbol"].upper()
                    manager.symbol_subscriptions.get(symbol, set()).discard(userId)
                    await websocket.send_json({"status": "unsubscribed", "symbol": symbol})
        except WebSocketDisconnect:
            manager.disconnect(userId)





