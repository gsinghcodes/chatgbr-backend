import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from core.config import DATABASE_URL

if DATABASE_URL is None:
    raise RuntimeError("POSTGRES_CONN environment variable is not set.")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)

ScopedSession = scoped_session(SessionLocal)
