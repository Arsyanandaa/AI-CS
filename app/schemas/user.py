from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    email: EmailStr
    phone_number: str
    password: str = Field(..., min_length=8, description="Minimal 8 karakter kombinasi huruf/angka")

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    phone_number: str
    role: str
    is_active: bool

    class Config:
        from_attributes = True