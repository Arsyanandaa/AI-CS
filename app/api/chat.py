from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.chat import ChatSession
from app.schemas.chat import ChatRequest, ChatResponse, ChatSessionResponse
from app.services import ai_service

router = APIRouter(prefix="/chat", tags=["AI Customer Service"])


@router.post("/send", response_model=ChatResponse)
def send_message(
    data: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = ai_service.process_message(
        db=db,
        user_id=current_user.id,
        session_id=data.session_id,
        user_message=data.message,
    )
    return ChatResponse(**result)


@router.get("/history/{session_id}", response_model=ChatSessionResponse)
def get_chat_history(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    session = (
        db.query(ChatSession)
        .filter(ChatSession.id == session_id, ChatSession.user_id == current_user.id)
        .first()
    )
    if not session:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Sesi chat tidak ditemukan")
    return session