import base64
import hashlib
import requests
from app.config import settings


def _get_base_url() -> str:
    return "https://app.midtrans.com" if settings.MIDTRANS_IS_PRODUCTION else "https://app.sandbox.midtrans.com"


def _get_auth_header() -> dict:
    # Server key di-encode base64 dengan format "server_key:" (password dikosongin)
    encoded = base64.b64encode(f"{settings.MIDTRANS_SERVER_KEY}:".encode()).decode()
    return {
        "Authorization": f"Basic {encoded}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def create_snap_transaction(invoice_id: str, gross_amount: int, user_email: str, user_phone: str) -> dict:
    """Nembak Midtrans Snap API buat generate snap_token & redirect_url."""
    url = f"{_get_base_url()}/snap/v1/transactions"
    payload = {
        "transaction_details": {
            "order_id": invoice_id,
            "gross_amount": gross_amount,
        },
        "customer_details": {
            "email": user_email,
            "phone": user_phone,
        },
    }
    response = requests.post(url, json=payload, headers=_get_auth_header(), timeout=15)
    response.raise_for_status()
    return response.json()  # {"token": "...", "redirect_url": "..."}


def verify_signature(order_id: str, status_code: str, gross_amount: str, signature_key: str) -> bool:
    """Verifikasi signature dari webhook Midtrans biar gak bisa dipalsuin pihak luar."""
    raw = f"{order_id}{status_code}{gross_amount}{settings.MIDTRANS_SERVER_KEY}"
    computed = hashlib.sha512(raw.encode()).hexdigest()
    return computed == signature_key