from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Optional, List


# ===== ITEM SCHEMAS =====

class ItemBase(BaseModel):
    nama_item: str
    harga: Decimal
    sku_code: str


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    nama_item: Optional[str] = None
    harga: Optional[Decimal] = None
    sku_code: Optional[str] = None


class ItemResponse(ItemBase):
    id: int
    game_id: int

    class Config:
        from_attributes = True


# ===== GAME SCHEMAS =====

class GameBase(BaseModel):
    nama_game: str
    kategori: Optional[str] = None
    gambar: Optional[str] = None


class GameCreate(GameBase):
    pass


class GameUpdate(BaseModel):
    nama_game: Optional[str] = None
    kategori: Optional[str] = None
    gambar: Optional[str] = None


class GameResponse(GameBase):
    id: int

    class Config:
        from_attributes = True


# Dipakai buat endpoint GET /games/{game_id}/items -> sekalian nampilin info game-nya
class GameWithItemsResponse(GameBase):
    id: int
    items: List[ItemResponse] = []

    class Config:
        from_attributes = True