from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import os
import httpx
import asyncio

API_KEY = os.getenv("TWELVE_DATA_API_KEY")

class ConnectionManager:
    def __init__(self):
        self.active_connections = {}  
        self.symbol_subscriptions = {} 

    async def connect(self, user_id, websocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id):
        self.active_connections.pop(user_id, None)
        for s in list(self.symbol_subscriptions):
            self.symbol_subscriptions[s].discard(user_id)
            if not self.symbol_subscriptions[s]:
                del self.symbol_subscriptions[s]

    async def broadcast(self, symbol, data):
        users = self.symbol_subscriptions.get(symbol, set())
        for user_id in users:
            ws = self.active_connections.get(user_id)
            if ws:
                await ws.send_json(data)

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
        await asyncio.sleep(5) 


def register_websocket(app):
    @app.websocket("/ws/{user_id}")
    async def websocket_endpoint(websocket: WebSocket, user_id: str):
        await manager.connect(user_id, websocket)
        try:
            while True:
                message = await websocket.receive_json()
                if message['type'] == "subscribe":
                    symbol = message["symbol"].upper()
                    manager.symbol_subscriptions.setdefault(symbol, set()).add(user_id)
                    await websocket.send_json({"status": "subscribed", "symbol": symbol})
                elif message['type'] == "unsubscribe":
                    symbol = message["symbol"].upper()
                    manager.symbol_subscriptions.get(symbol, set()).discard(user_id)
                    await websocket.send_json({"status": "unsubscribed", "symbol": symbol})
        except WebSocketDisconnect:
            manager.disconnect(user_id)





