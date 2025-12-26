import logging
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database configuration
NEON_DATABASE_URL = os.getenv("NEON_DATABASE_URL", "")
if not NEON_DATABASE_URL:
    # Fallback to local SQLite for development if no Neon URL is provided
    NEON_DATABASE_URL = "sqlite:///./book_chatbot.db"

engine = create_engine(NEON_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Auth configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production-please-make-it-long-and-random")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_DAYS = int(os.getenv("ACCESS_TOKEN_EXPIRE_DAYS", "7"))

# Configure basic logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

def get_logger(name: str):
    return logging.getLogger(name)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
