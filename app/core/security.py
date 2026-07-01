import bcrypt
from datetime import datetime, timedelta
from jose import jwt
from app.config import settings

def hash_password(password: str) -> str:
    # Mengubah password string menjadi bytes
    pwd_bytes = password.encode('utf-8')
    # Generate salt dan hash password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(pwd_bytes, salt)
    # Mengembalikan dalam bentuk string agar bisa disimpan di database VARCHAR
    return hashed_password.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Mengubah plain password dan hashed password dari DB ke bentuk bytes
    pwd_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    # Validasi kecocokan password
    return bcrypt.checkpw(pwd_bytes, hashed_bytes)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt