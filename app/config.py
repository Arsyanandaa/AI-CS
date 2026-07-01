import os
from pathlib import Path
from dotenv import load_dotenv

# Ambil base directory dari project (folder paling luar)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
env_path = BASE_DIR / ".env"

# Load .env berdasarkan path absolutnya
load_dotenv(dotenv_path=env_path)

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    # Kita kasih default value string acak kalau seandainya os.getenv nyasar/None
    JWT_SECRET: str = os.getenv("JWT_SECRET", "supersecretkeyyangsangatpanjangdanaman1234567890")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 1440))

settings = Settings()