from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from contextlib import asynccontextmanager

from config import settings
from backend.db import init_db
from backend.routers import chat, rating
from backend.streaming.websocket import ConnectionManager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database on startup
    await init_db()
    yield
    # Clean up on shutdown
    pass

app = FastAPI(
    title="Multi-AI Chat Platform",
    description="Chat platform that queries multiple AI models in parallel",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket manager
websocket_manager = ConnectionManager()

# Include routers
app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(rating.router, prefix="/api", tags=["rating"])

# Serve frontend files
if os.path.exists("frontend"):
    app.mount("/static", StaticFiles(directory="frontend"), name="static")
    
    @app.get("/")
    async def read_index():
        return FileResponse("frontend/index.html")
    
    @app.get("/{path:path}")
    async def serve_frontend(path: str):
        frontend_path = f"frontend/{path}"
        if os.path.exists(frontend_path):
            return FileResponse(frontend_path)
        return FileResponse("frontend/index.html")

# WebSocket endpoint
@app.websocket("/ws/chat/{chat_id}")
async def websocket_endpoint(websocket: WebSocket, chat_id: str):
    await websocket_manager.connect(websocket, chat_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming messages if needed
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, chat_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)