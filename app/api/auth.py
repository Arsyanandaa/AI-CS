from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, Token, UserResponse
from app.core.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # 1. Cek apakah email sudah terdaftar
    db_user_email = db.query(User).filter(User.email == user_data.email).first()
    if db_user_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Email sudah digunakan, Bro!"
        )
    
    # 2. Cek apakah nomor HP sudah terdaftar (Biar ga memicu error 500 PostgreSQL)
    db_user_phone = db.query(User).filter(User.phone_number == user_data.phone_number).first()
    if db_user_phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Nomor HP ini sudah terdaftar, pakai nomor lain ya!"
        )
    
    # 3. Hash password sebelum disimpan ke database
    hashed = hash_password(user_data.password)
    
    new_user = User(
        email=user_data.email,
        phone_number=user_data.phone_number,
        hashed_password=hashed
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # OAuth2PasswordRequestForm secara otomatis membaca input 'username' (isi dengan email) dan 'password'
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Email atau password salah"
        )
    
    # Bikin JWT Token (Sesuaikan parameter subject dengan file security.py)
    # Payload role bisa lu masukkan ke dalam sub jika diperlukan, atau jadikan claims tersendiri
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}