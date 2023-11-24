import json

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.cors import CORSMiddleware

from backend.db import get_db
from backend.models.models import ChatMessage

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)


manager = ConnectionManager()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int, db: AsyncSession = Depends(get_db)):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            data_dict = json.loads(data)  # Make sure to import json
            message = data_dict["message"]
            message_dict = {
                "sender": f"User{client_id}",
                "message": message,
                "isOwnMessage": False  # Since this is a broadcast, it's not the own message of the receiver.
            }
            await manager.broadcast(message_dict)  # Send the dictionary

            # Save message to database
            chat_message = ChatMessage(content=message, user_id=client_id)
            db.add(chat_message)
            await db.commit()

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        disconnect_message_dict = {
            "sender": f"User{client_id}",
            "message": f"Client #{client_id} left the chat",
            "isOwnMessage": False
        }
        await manager.broadcast(disconnect_message_dict)

        # Save disconnect message to database
        chat_message = ChatMessage(content=disconnect_message_dict["message"], user_id=client_id)
        db.add(chat_message)
        await db.commit()



@app.get("/last_messages")
async def get_last_messages(db: AsyncSession = Depends(get_db)):
    try:
        # Assuming 'left the chat' messages have a specific pattern in content
        query = (
            select(ChatMessage)
            .where(ChatMessage.content.not_like('%left the chat%'))
            .order_by(ChatMessage.created_at.desc())
            .limit(10)
        )
        result = await db.execute(query)
        messages = result.scalars().all()
        return [message.as_dict() for message in messages[::-1]]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))