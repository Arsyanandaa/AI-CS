from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime, Enum as SqlEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.core.database import Base


class StatusPembayaran(str, enum.Enum):
    PENDING = "Pending"
    SUCCESS = "Success"
    FAILED = "Failed"


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(String, unique=True, nullable=False, index=True)

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)

    target_id = Column(String, nullable=False)  # ID akun game, wajib di semua game
    zone_id = Column(String, nullable=True)      # server/region, opsional tergantung game

    total_harga = Column(Numeric(12, 2), nullable=False)
    status_pembayaran = Column(
        SqlEnum(StatusPembayaran, name="status_pembayaran_enum"),
        default=StatusPembayaran.PENDING,
        nullable=False,
    )

    payment_method = Column(String, nullable=True)           # keisi dari webhook, misal "qris"/"bank_transfer"
    midtrans_transaction_id = Column(String, nullable=True)   # transaction_id dari Midtrans

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User")
    item = relationship("Item")