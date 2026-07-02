from sqlalchemy.orm import Session
from app.models.transaction import Transaction
from app.models.chat import ChatSession, ChatMessage, SessionStatus, SenderType
from app.core import gemini_client

# Keyword sederhana buat deteksi frustrasi/kata kasar (bisa diperluas nanti)
FRUSTRATION_KEYWORDS = [
    "goblok", "bangsat", "anjing", "tolol", "bego", "kampret",
    "parah banget", "kzl", "kesel banget", "gaperna beres",
    "gak becus", "penipu", "scam", "laporin polisi",
]


def detect_escalation(message: str) -> tuple[bool, str | None]:
    """Cek apakah pesan user mengandung indikasi frustrasi/kata kasar."""
    lower_msg = message.lower()
    for keyword in FRUSTRATION_KEYWORDS:
        if keyword in lower_msg:
            return True, f"Terdeteksi kata kunci frustrasi: '{keyword}'"
    return False, None


def get_transaction_context(db: Session, user_id: int, invoice_id: str | None = None) -> str:
    """Ambil ringkasan status transaksi user buat dijadiin context AI."""
    query = db.query(Transaction).filter(Transaction.user_id == user_id)

    if invoice_id:
        transaction = query.filter(Transaction.invoice_id == invoice_id).first()
        transactions = [transaction] if transaction else []
    else:
        transactions = query.order_by(Transaction.created_at.desc()).limit(3).all()

    if not transactions:
        return "Tidak ada data transaksi yang ditemukan untuk user ini."

    lines = []
    for t in transactions:
        # KUNCI PERBAIKAN: Hapus '.value' setelah status_pembayaran karena tipe datanya str biasa
        status_pembayaran_str = t.status_pembayaran if isinstance(t.status_pembayaran, str) else t.status_pembayaran.value
        
        lines.append(
            f"- Invoice {t.invoice_id}: item_id={t.item_id}, "
            f"total=Rp{t.total_harga}, status={status_pembayaran_str}, "
            f"tanggal={t.created_at.strftime('%d-%m-%Y %H:%M')}"
        )
    return "Riwayat transaksi user:\n" + "\n".join(lines)


def build_system_prompt(context: str) -> str:
    return (
        "Kamu adalah AI Customer Service untuk platform top up game bernama GamePay CS-AI. "
        "Jawab pertanyaan user seputar status transaksi, cara top up, dan kebijakan platform "
        "secara ramah, singkat, dan jelas dalam Bahasa Indonesia. "
        "Jangan pernah mengarang status transaksi yang tidak ada di data berikut.\n\n"
        f"{context}"
    )


def process_message(db: Session, user_id: int, session_id: int | None, user_message: str) -> dict:
    # Ambil atau bikin sesi chat baru
    if session_id:
        session = db.query(ChatSession).filter(
            ChatSession.id == session_id, ChatSession.user_id == user_id
        ).first()
        if not session:
            session = ChatSession(user_id=user_id)
            db.add(session)
            db.commit()
            db.refresh(session)
    else:
        session = ChatSession(user_id=user_id)
        db.add(session)
        db.commit()
        db.refresh(session)

    # Simpan pesan user
    db.add(ChatMessage(session_id=session.id, sender=SenderType.USER, message=user_message))
    db.commit()

    # Cek eskalasi dulu sebelum manggil AI (biar hemat API call kalau udah jelas harus dialihkan)
    should_escalate, reason = detect_escalation(user_message)

    if should_escalate:
        session.status = SessionStatus.ESCALATED
        session.escalation_reason = reason
        db.commit()

        reply_text = (
            "Kami memahami kendala yang Anda alami. Percakapan ini akan segera "
            "dialihkan ke agen customer service kami untuk penanganan lebih lanjut."
        )
        db.add(ChatMessage(session_id=session.id, sender=SenderType.AI, message=reply_text))
        db.commit()

        return {
            "session_id": session.id,
            "reply": reply_text,
            "escalated": True,
            "status": session.status,
        }

    # Ambil histori percakapan buat context Gemini
    history_records = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session.id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )
    chat_history = [
        {"role": "user" if m.sender == SenderType.USER else "model", "text": m.message}
        for m in history_records[:-1]  # exclude pesan terakhir yang baru aja disimpan, dikirim terpisah
    ]

    transaction_context = get_transaction_context(db, user_id)
    system_prompt = build_system_prompt(transaction_context)

    reply_text = gemini_client.generate_reply(system_prompt, chat_history, user_message)

    db.add(ChatMessage(session_id=session.id, sender=SenderType.AI, message=reply_text))
    db.commit()

    return {
        "session_id": session.id,
        "reply": reply_text,
        "escalated": False,
        "status": session.status,
    }