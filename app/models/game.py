from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    nama_game = Column(String, nullable=False, index=True)
    kategori = Column(String, nullable=True)  # contoh: MOBA, Battle Royale, RPG
    gambar = Column(String, nullable=True)    # URL/path gambar thumbnail
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relasi ke tabel items, cascade biar item ikut kehapus kalau game dihapus
    items = relationship("Item", back_populates="game", cascade="all, delete-orphan")


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    nama_item = Column(String, nullable=False)   # contoh: "86 Diamonds", "Weekly Pass"
    harga = Column(Numeric(12, 2), nullable=False)
    sku_code = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    game = relationship("Game", back_populates="items")