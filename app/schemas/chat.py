from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.models.chat import SessionStatus, SenderType


class ChatRequest(BaseModel):
    session_id: Optional[int] = None  # kalau None, bikin sesi baru
    message: str


class ChatMessageResponse(BaseModel):
    sender: SenderType
    message: str
    created_at: datetime

    class Config:
        from_attributes = True


class ChatResponse(BaseModel):
    session_id: int
    reply: str
    escalated: bool
    status: SessionStatus


class ChatSessionResponse(BaseModel):
    id: int
    status: SessionStatus
    started_at: datetime
    messages: List[ChatMessageResponse] = []

    class Config:
        from_attributes = True