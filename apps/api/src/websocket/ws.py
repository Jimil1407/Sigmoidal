from fastapi import FastAPI, WebSocket, WebSocketDisconnect
app = FastAPI()

def register_websocket(app):
    @app.websocket("/ws/{user_id}")
    async def websocket_endpoint(websocket: WebSocket, user_id: str):
        await websocket.accept()
        try:
            while True:
                data = await websocket.receive_text()
                # Echo or custom logic here
                await websocket.send_text(f"Hello {user_id}, you said: {data}")
        except WebSocketDisconnect:
            print(f"User {user_id} has disconnected.")
