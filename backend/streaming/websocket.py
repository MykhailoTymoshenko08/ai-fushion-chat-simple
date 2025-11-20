from fastapi import WebSocket
from typing import Dict, List
import json
import asyncio

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, chat_id: str):
        await websocket.accept()
        if chat_id not in self.active_connections:
            self.active_connections[chat_id] = []
        self.active_connections[chat_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, chat_id: str):
        if chat_id in self.active_connections:
            self.active_connections[chat_id].remove(websocket)
            if not self.active_connections[chat_id]:
                del self.active_connections[chat_id]
    
    async def send_provider_token(self, chat_id: str, provider: str, token: str, done: bool = False):
        if chat_id in self.active_connections:
            message = {
                "type": "provider",
                "provider": provider,
                "token": token,
                "done": done
            }
            await self._broadcast(chat_id, message)
    
    async def send_synth_token(self, chat_id: str, token: str, done: bool = False):
        if chat_id in self.active_connections:
            message = {
                "type": "synth",
                "token": token,
                "done": done
            }
            await self._broadcast(chat_id, message)
    
    async def _broadcast(self, chat_id: str, message: dict):
        if chat_id in self.active_connections:
            disconnected = []
            for websocket in self.active_connections[chat_id]:
                try:
                    await websocket.send_text(json.dumps(message))
                except:
                    disconnected.append(websocket)
            
            for websocket in disconnected:
                self.disconnect(websocket, chat_id)

websocket_manager = ConnectionManager()