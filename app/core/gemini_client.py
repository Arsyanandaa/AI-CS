import requests
from app.config import settings


def _get_endpoint() -> str:
    return (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{settings.GEMINI_MODEL}:generateContent?key={settings.GEMINI_API_KEY}"
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

    response = requests.post(_get_endpoint(), json=payload, timeout=20)
    response.raise_for_status()
    data = response.json()

    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        return "Maaf, sistem AI CS sedang mengalami gangguan. Pesan Anda akan dialihkan ke agen manusia."