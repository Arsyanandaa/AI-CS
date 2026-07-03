import os
import requests
# PERBAIKAN: Pakai load_dotenv, bukan load_model
from dotenv import load_dotenv

# Panggil fungsi ini di paling atas biar file .env kebaca sama sistem os
load_dotenv()

# Ambil langsung dari environment variable sistem / file .env
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")


def _get_endpoint() -> str:
    return (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    )


def generate_reply(system_prompt: str, chat_history: list[dict], user_message: str) -> str:
    """
    chat_history format: [{"role": "user"/"model", "text": "..."}]
    Gemini butuh format 'contents' dengan role user/model bergantian.
    """
    contents = []
    for turn in chat_history:
        contents.append({
            "role": turn["role"],
            "parts": [{"text": turn["text"]}]
        })
    contents.append({"role": "user", "parts": [{"text": user_message}]})

    payload = {
        "system_instruction": {"parts": [{"text": system_prompt}]},
        "contents": contents,
        "generationConfig": {
            "temperature": 0.4,
            "maxOutputTokens": 512,
        },
    }

    try:
        response = requests.post(_get_endpoint(), json=payload, timeout=20)
        response.raise_for_status()
        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except requests.exceptions.HTTPError as http_err:
        # Pengaman ekstra jika kuota gratisan 429 habis di kemudian hari
        if response.status_code == 429:
            return "Maaf kak, server AI kami sedang padat banget nih. Coba kirim pesan lagi dalam 1 menit ya!"
        return "Maaf kak, layanan otomatis kami sedang sibuk. Mohon tunggu sebentar ya."
    except (KeyError, IndexError, Exception):
        return "Maaf, sistem AI CS sedang mengalami gangguan. Pesan Anda akan dialihkan ke agen manusia."