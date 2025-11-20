from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.streaming.websocket import websocket_manager

router = APIRouter()

@router.websocket("/ws/chat/{chat_id}")
async def websocket_endpoint(websocket: WebSocket, chat_id: str):
    await websocket_manager.connect(websocket, chat_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming messages if needed
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, chat_id)