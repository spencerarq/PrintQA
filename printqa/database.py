import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Carrega a URL do banco de dados a partir das variáveis de ambiente
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

# --- CORREÇÃO FINAL ADICIONADA AQUI ---
# Esta importação faz com que os modelos sejam registrados no SQLAlchemy Base
# antes que a função create_tables seja chamada.
from . import models

def get_db():
    """Gerador de sessão de banco de dados para dependências do FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Cria todas as tabelas no banco de dados com base nos modelos."""
    Base.metadata.create_all(bind=engine)

def drop_tables():
    """Remove todas as tabelas do banco de dados (usado para testes)."""
    Base.metadata.drop_all(bind=engine)