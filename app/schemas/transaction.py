from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime
from typing import Optional
from app.models.transaction import StatusPembayaran


class CheckoutRequest(BaseModel):
    item_id: int
    target_id: str = Field(..., description="ID akun game user, misal User ID Mobile Legends")
    zone_id: Optional[str] = Field(None, description="Server/region ID, opsional tergantung game")


class CheckoutResponse(BaseModel):
    invoice_id: str
    snap_token: str
    redirect_url: str
    total_harga: Decimal


class TransactionResponse(BaseModel):
    id: int
    invoice_id: str
    item_id: int
    target_id: str
    zone_id: Optional[str]
    total_harga: Decimal
    status_pembayaran: StatusPembayaran
    payment_method: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True