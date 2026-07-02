from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum as SqlEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base


class SessionStatus(str, enum.Enum):
    ACTIVE = "active"
    ESCALATED = "escalated"
    CLOSED = "closed"


class SenderType(str, enum.Enum):
    USER = "user"
    AI = "ai"
    AGENT = "agent"


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(SqlEnum(SessionStatus, name="session_status_enum"), default=SessionStatus.ACTIVE, nullable=False)
    escalation_reason = Column(String, nullable=True)  # kesimpen alasan kenapa dieskalasi
    started_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    sender = Column(SqlEnum(SenderType, name="sender_type_enum"), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("ChatSession", back_populates="messages")