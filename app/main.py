from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pathlib import Path
from app.api import auth, games, transactions, chat
from app.core.database import engine, Base
from app.models import user, game, transaction, chat as chat_model  # noqa: F401

# Auto-create tables di PostgreSQL saat aplikasi nyala
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="GamePay CS-AI Platform API",
    description="Backend Server untuk Platform Top Up Game dengan AI Customer Service",
    version="1.0.0"
)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrasi Semua Router API Modular
app.include_router(auth.router)
app.include_router(games.router)
app.include_router(transactions.router)
app.include_router(chat.router)

@app.get("/", response_class=HTMLResponse)
async def root():
    # Menggunakan pathlib untuk mengunci folder templates secara absolut dan aman
    # Path(__file__).resolve() -> .../AI CUSTOMER SERVICE/app/main.py
    # .parent.parent            -> .../AI CUSTOMER SERVICE/
    base_dir = Path(__file__).resolve().parent.parent
    html_path = base_dir / "templates" / "index.html"
    
    # Pengaman jika jalur file meleset, biar ga langsung Internal Server Error
    if not html_path.exists():
        return f"""
        <div style="font-family: sans-serif; text-align: center; margin-top: 50px;">
            <h1 style="color: #ea580c;">🎮 GamePay CS-AI Core API</h1>
            <p>Status: <span style="color: #ef4444;">File Not Found</span></p>
            <p style="color: #94a3b8;">Sistem gagal mendeteksi file HTML lu di jalur: <code>{html_path}</code></p>
            <p style="color: #64748b;">Pastikan folder <b>templates</b> berada di luar folder <b>app</b> ya, bro!</p>
            <a href="/docs" style="color: #38bdf8; text-decoration: none; font-weight: bold;">Buka Swagger UI Docs &rarr;</a>
        </div>
        """
        
    return html_path.read_text(encoding="utf-8")