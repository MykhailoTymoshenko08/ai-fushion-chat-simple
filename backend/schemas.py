from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ChatCreate(BaseModel):
    title: Optional[str] = "New Chat"

class ChatResponse(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime

class MessageSend(BaseModel):
    chat_id: Optional[str] = None
    message: str
    mode: Optional[str] = "aggregate"  # single, multiple, aggregate

class MessageResponse(BaseModel):
    id: str
    chat_id: str
    content: str
    is_user: bool
    created_at: datetime

class ProviderResponseSchema(BaseModel):
    provider: str
    content: str
    response_time: Optional[int]

class RatingCreate(BaseModel):
    chat_id: str
    message_id: str
    score: int  # 1 or -1

class ChatHistoryResponse(BaseModel):
    chat: ChatResponse
    messages: List[MessageResponse]
    provider_responses: List[ProviderResponseSchema]

class StreamEvent(BaseModel):
    type: str  # "provider" or "synth"
    provider: Optional[str] = None  # "openai", "groq", etc.
    token: str
    done: bool = False