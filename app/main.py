from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth  # Import router auth
from app.core.database import engine, Base

# Otomatis bikin tabel di PostgreSQL kalau belum ada saat server start
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="GamePay CS-AI Platform API",
    description="Backend Server untuk Platform Top Up Game dengan AI Customer Service",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Hubungkan route authentication ke aplikasi utama
app.include_router(auth.router)

@app.get("/")
async def root():
    return {
        "status": "success",
        "message": "Welcome to GamePay CS-AI Core API Services",
        "environment": "Development"
    }