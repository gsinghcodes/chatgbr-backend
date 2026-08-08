import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("POSTGRES_CONN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

BASE_DIR = Path(__file__).resolve().parent.parent

REPOSITORIES_ROOT = BASE_DIR / "storage" / "repositories"

JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 60
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
