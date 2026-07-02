import uuid
from typing import List
from app.schemas.transaction import TransactionResponse
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user
from app.core import midtrans_client
from app.models.user import User
from app.models.game import Item
from app.models.transaction import Transaction, StatusPembayaran
from app.schemas.transaction import CheckoutRequest, CheckoutResponse

router = APIRouter(prefix="/transactions", tags=["Transaksi"])


def _generate_invoice_id() -> str:
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    unique = uuid.uuid4().hex[:6].upper()
    return f"INV-{timestamp}-{unique}"


@router.post("/checkout", response_model=CheckoutResponse, status_code=status.HTTP_201_CREATED)
def checkout(
    data: CheckoutRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    item = db.query(Item).filter(Item.id == data.item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item tidak ditemukan")

    invoice_id = _generate_invoice_id()

    new_transaction = Transaction(
        invoice_id=invoice_id,
        user_id=current_user.id,
        item_id=item.id,
        target_id=data.target_id,
        zone_id=data.zone_id,
        total_harga=item.harga,
        status_pembayaran=StatusPembayaran.PENDING,
    )
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    try:
        midtrans_response = midtrans_client.create_snap_transaction(
            invoice_id=invoice_id,
            gross_amount=int(item.harga),
            user_email=current_user.email,
            user_phone=current_user.phone_number,
        )
    except Exception:
        # Transaksi tetap kesimpen sebagai Pending biar bisa di-retry,
        # tapi user langsung dikasih tau gagal generate pembayaran
        raise HTTPException(status_code=502, detail="Gagal menghubungi payment gateway, coba lagi")

    return CheckoutResponse(
        invoice_id=invoice_id,
        snap_token=midtrans_response["token"],
        redirect_url=midtrans_response["redirect_url"],
        total_harga=item.harga,
    )


@router.post("/notification", status_code=status.HTTP_200_OK)
async def midtrans_notification(request: Request, db: Session = Depends(get_db)):
    """Webhook yang ditembak Midtrans otomatis pas status pembayaran berubah."""
    payload = await request.json()

    order_id = payload.get("order_id")
    status_code = payload.get("status_code")
    gross_amount = payload.get("gross_amount")
    signature_key = payload.get("signature_key")
    transaction_status = payload.get("transaction_status")
    fraud_status = payload.get("fraud_status")
    payment_type = payload.get("payment_type")
    midtrans_transaction_id = payload.get("transaction_id")

    if not all([order_id, status_code, gross_amount, signature_key, transaction_status]):
        raise HTTPException(status_code=400, detail="Payload notifikasi tidak lengkap")

    # Validasi signature dulu biar gak ada yang bisa palsuin notifikasi
    if not midtrans_client.verify_signature(order_id, status_code, gross_amount, signature_key):
        raise HTTPException(status_code=403, detail="Signature tidak valid")

    transaction = db.query(Transaction).filter(Transaction.invoice_id == order_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaksi tidak ditemukan")

    # Mapping status Midtrans -> status internal kita
    if transaction_status == "capture":
        transaction.status_pembayaran = (
            StatusPembayaran.SUCCESS if fraud_status == "accept" else StatusPembayaran.PENDING
        )
    elif transaction_status == "settlement":
        transaction.status_pembayaran = StatusPembayaran.SUCCESS
    elif transaction_status in ("deny", "cancel", "expire", "failure"):
        transaction.status_pembayaran = StatusPembayaran.FAILED
    # kalau "pending", biarin tetep Pending, gak usah diubah

    transaction.payment_method = payment_type
    transaction.midtrans_transaction_id = midtrans_transaction_id
    transaction.updated_at = datetime.utcnow()

    db.commit()

    return {"status": "ok"}

@router.get("/history", response_model=List[TransactionResponse])
def get_transaction_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Menampilkan seluruh riwayat transaksi milik user yang sedang login."""
    transactions = (
        db.query(Transaction)
        .filter(Transaction.user_id == current_user.id)
        .order_by(Transaction.created_at.desc())
        .all()
    )
    return transactions