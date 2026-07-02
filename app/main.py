from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, games, transactions, chat
from app.core.database import engine, Base
from app.models import user, game, transaction, chat as chat_model  # noqa: F401

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

app.include_router(auth.router)
app.include_router(games.router)
app.include_router(transactions.router)
app.include_router(chat.router)

@app.get("/")
async def root():
    return {
        "status": "success",
        "message": "Welcome to GamePay CS-AI Core API Services",
        "environment": "Development"
    }