import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL não está definida no ambiente.")

try:
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()
except Exception as e:
    logging.getLogger(__name__).exception(f"Falha ao criar o engine do SQLAlchemy: {e}")
    raise


from . import models

def get_db():
    """Gerador de sessão de banco de dados para dependências do FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
