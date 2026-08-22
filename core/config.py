import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("POSTGRES_CONN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

BASE_DIR = Path(__file__).resolve().parent.parent

REPOSITORIES_ROOT = BASE_DIR / "storage" / "repositories"

JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 15
JWT_REFRESH_TOKEN_EXPIRE_DAYS = 7
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")

GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_REDIRECT_URI = os.getenv("GITHUB_REDIRECT_URI")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")

FRONTEND_URL = "https://chatgbr-omega.vercel.app/"
