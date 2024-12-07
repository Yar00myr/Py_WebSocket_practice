from contextlib import asynccontextmanager
from collections import defaultdict
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect


connected_users = {}
votes = defaultdict(int)


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except WebSocketDisconnect:
            self.disconnect(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except WebSocketDisconnect:
                self.disconnect(connection)


manager = ConnectionManager()


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.connection_manager = ConnectionManager()
    yield


app = FastAPI(lifespan=lifespan)


@app.websocket("/vote")
async def vote_ws_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while 1:
            data = await websocket.receive_text()
            if data in ["photo 1", "photo 2", "photo 3"]:
                votes[data] += 1
                await websocket.send_text(f"Your vote for '{data}' has been counted.")
                await websocket.send_json(dict(votes))
            else:
                await websocket.send_text(
                    "Invalid option. Please vote for 'photo 1', 'photo 2', or 'photo 3'."
                )
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast("A user has disconnected from voting.")


@app.websocket("/chat/{user_id}")
async def chat_ws_endpoint(user_id: str, websocket: WebSocket):
    await manager.connect(websocket)

    connected_users[user_id] = websocket
    try:
        while 1:
            data = await websocket.receive_text()
            for user, user_ws in connected_users.items():
                if user != user_id:
                    await user_ws.send_text(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast("A user has disconnected from the chat.")


if __name__ == "__main__":
    uvicorn.run(app=app)
