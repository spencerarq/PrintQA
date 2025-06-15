# printqa/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base 
from dotenv import load_dotenv 

load_dotenv() 

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL is None:
    
    raise ValueError("DATABASE_URL não está definida nas variáveis de ambiente. Verifique o arquivo .env")
    
engine = create_engine(DATABASE_URL, echo=True)

Base = declarative_base() 

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

def create_tables():
    """Cria todas as tabelas no banco de dados."""
    from . import models 
    Base.metadata.create_all(bind=engine)

def drop_tables():
    """Remove todas as tabelas do banco de dados. Use com cuidado!"""
    from . import models 
    Base.metadata.drop_all(bind=engine)