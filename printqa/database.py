# printqa/database.py
import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL is None:
    raise ValueError("DATABASE_URL não está definida nas variáveis de ambiente. Verifique o arquivo .env")

try:
    engine = create_engine(DATABASE_URL, echo=True)
except Exception as e:
    logger.error(f"Falha ao criar o engine do SQLAlchemy: {e}")
    raise

Base = declarative_base() # A ÚNICA Base do projeto

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Dependency que fornece uma sessão de banco de dados.
    Para ser usada com FastAPI Depends().
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Modificado para aceitar 'target_base' como argumento
def create_tables(target_base, engine_to_use=None):
    """Cria todas as tabelas no banco de dados para a Base fornecida."""
    current_engine = engine_to_use if engine_to_use is not None else engine
    from . import models # Garante que os modelos estejam carregados para popular target_base.metadata
    target_base.metadata.create_all(bind=current_engine)

# Modificado para aceitar 'target_base' como argumento
def drop_tables(target_base, engine_to_use=None):
    """Remove todas as tabelas do banco de dados para a Base fornecida."""
    current_engine = engine_to_use if engine_to_use is not None else engine
    from . import models # Garante que os modelos estejam carregados para popular target_base.metadata
    target_base.metadata.drop_all(bind=current_engine)