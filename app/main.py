from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Inisialisasi aplikasi FastAPI sesuai spesifikasi dokumen GamePay CS-AI
app = FastAPI(
    title="GamePay CS-AI Platform API",
    description="Backend Server untuk Platform Top Up Game dengan AI Customer Service",
    version="1.0.0"
)

# Setup CORS agar frontend (React.js) nanti bisa nge-hit backend ini dengan lancar
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Nanti bisa diganti dengan domain frontend spesifik
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "status": "success",
        "message": "Welcome to GamePay CS-AI Core API Services",
        "environment": "Development"
    }