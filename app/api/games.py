from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from typing import List
from app.core.database import get_db
from app.core.deps import get_current_admin
from app.models.game import Game, Item
from app.schemas.game import (
    GameCreate, GameUpdate, GameResponse, GameWithItemsResponse,
    ItemCreate, ItemUpdate, ItemResponse,
)

router = APIRouter(prefix="/games", tags=["Katalog Game"])


# ===== PUBLIC ENDPOINTS =====

@router.get("", response_model=List[GameResponse])
def list_games(db: Session = Depends(get_db)):
    """Menampilkan daftar semua game untuk homepage."""
    return db.query(Game).all()


@router.get("/{game_id}/items", response_model=GameWithItemsResponse)
def get_game_items(game_id: int, db: Session = Depends(get_db)):
    """Menampilkan detail game beserta pilihan nominal top up (items)."""
    game = (
        db.query(Game)
        .options(joinedload(Game.items))
        .filter(Game.id == game_id)
        .first()
    )
    if not game:
        raise HTTPException(status_code=404, detail="Game tidak ditemukan")
    return game


# ===== ADMIN ENDPOINTS: GAME =====

@router.post("", response_model=GameResponse, status_code=status.HTTP_201_CREATED)
def create_game(
    game_data: GameCreate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    new_game = Game(**game_data.model_dump())
    db.add(new_game)
    db.commit()
    db.refresh(new_game)
    return new_game


@router.put("/{game_id}", response_model=GameResponse)
def update_game(
    game_id: int,
    game_data: GameUpdate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game tidak ditemukan")

    update_data = game_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(game, key, value)

    db.commit()
    db.refresh(game)
    return game


@router.delete("/{game_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_game(
    game_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game tidak ditemukan")
    db.delete(game)
    db.commit()
    return None


# ===== ADMIN ENDPOINTS: ITEM (NOMINAL TOP UP) =====

@router.post("/{game_id}/items", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(
    game_id: int,
    item_data: ItemCreate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    game = db.query(Game).filter(Game.id == game_id).first()
    if not game:
        raise HTTPException(status_code=404, detail="Game tidak ditemukan")

    # Cek duplikasi SKU code biar gak bentrok antar item
    existing_sku = db.query(Item).filter(Item.sku_code == item_data.sku_code).first()
    if existing_sku:
        raise HTTPException(status_code=400, detail="SKU code sudah digunakan")

    new_item = Item(**item_data.model_dump(), game_id=game_id)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item


@router.put("/items/{item_id}", response_model=ItemResponse)
def update_item(
    item_id: int,
    item_data: ItemUpdate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item tidak ditemukan")

    update_data = item_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(item, key, value)

    db.commit()
    db.refresh(item)
    return item


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin),
):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item tidak ditemukan")
    db.delete(item)
    db.commit()
    return None