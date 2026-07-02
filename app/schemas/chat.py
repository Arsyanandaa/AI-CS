from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, List
from app.models.chat import SessionStatus, SenderType


class ChatRequest(BaseModel):
    session_id: Optional[int] = None  # kalau None, bikin sesi baru
    message: str


class ChatMessageResponse(BaseModel):
    # Menggunakan ConfigDict untuk Pydantic v2 tanpa nested class lawas
    model_config = ConfigDict(from_attributes=True)
    
    sender: SenderType
    message: str
    created_at: datetime


class ChatResponse(BaseModel):
    session_id: int
    reply: str
    escalated: bool
    status: SessionStatus


class ChatSessionResponse(BaseModel):
    # Menggunakan ConfigDict untuk Pydantic v2 tanpa nested class lawas
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    status: SessionStatus
    started_at: datetime
    messages: List[ChatMessageResponse] = []