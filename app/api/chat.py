import traceback
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.chat import ChatSession
from app.schemas.chat import ChatRequest, ChatResponse, ChatSessionResponse
from app.services import ai_service

router = APIRouter(prefix="/chat", tags=["AI Customer Service"])


@router.post("/send", response_model=ChatResponse)
@router.post("/send/", response_model=ChatResponse) # <-- Tambahkan baris ini di bawahnya!
def send_message(
    data: ChatRequest,
    db: Session = Depends(get_db),
):
    try:
        # Kita hardcode user_id dummy bernilai 1 biar database PostgreSQL lu ga bingung pas nyimpen data chat
        dummy_user_id = 1
        
        result = ai_service.process_message(
            db=db,
            user_id=dummy_user_id,
            session_id=data.session_id,
            user_message=data.message,
        )
        return ChatResponse(**result)
        
    except Exception as e:
        # Cetak error asli di terminal Uvicorn biar kelihatan baris mana yang crash
        error_details = traceback.format_exc()
        print("\n=== !!! BACKEND CRASH ERROR !!! ===")
        print(error_details)
        print("====================================\n")
        
        # Lempar detail error ke frontend browser agar tidak stuck di tulisan "Internal Server Error"
        raise HTTPException(
            status_code=500,
            detail=f"Crash di Backend Bro! Error: {str(e)}. Detail: {error_details}"
        )


@router.get("/history/{session_id}", response_model=ChatSessionResponse)
def get_chat_history(
    session_id: int,
    db: Session = Depends(get_db),
):
    try:
        dummy_user_id = 1
        session = (
            db.query(ChatSession)
            .filter(ChatSession.id == session_id, ChatSession.user_id == dummy_user_id)
            .first()
        )
        if not session:
            raise HTTPException(status_code=404, detail="Sesi chat tidak ditemukan")
        return session
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))