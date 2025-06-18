import pytest
import importlib
import logging
import os
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, Session

from printqa.database import get_db, Base
from printqa import database as database_module
from printqa import models

@pytest.fixture(scope="function")
def db_engine():
    """Cria um engine de banco de dados em memória para os testes."""
    engine = create_engine("sqlite:///:memory:")
    yield engine
    engine.dispose()

@pytest.fixture(scope="function")
def db_session(db_engine):
    """Cria uma sessão de banco de dados e as tabelas para cada teste."""
    
    import printqa.models 
    Base.metadata.create_all(bind=db_engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=db_engine)

def test_database_connection(db_session: Session):
    assert db_session.is_active
    result = db_session.execute(text("SELECT 1"))
    assert result.scalar() == 1

def test_get_db_closes_session():
    mock_session = MagicMock(spec=Session)
    with patch("printqa.database.SessionLocal", return_value=mock_session):
        list(get_db())
    mock_session.close.assert_called_once()

def test_create_and_drop_tables(db_engine):
    """ Testa a criação e remoção de tabelas diretamente via Base.metadata,
    agora que create_tables/drop_tables não são funções utilitárias no database.py."""
    
    import printqa.models 

    Base.metadata.drop_all(bind=db_engine)
    inspector = inspect(db_engine)
    assert "analysis_results" not in inspector.get_table_names()

    Base.metadata.create_all(bind=db_engine)
    inspector = inspect(db_engine)
    assert "analysis_results" in inspector.get_table_names()

    
    Base.metadata.drop_all(bind=db_engine)
    inspector = inspect(db_engine)
    assert "analysis_results" not in inspector.get_table_names()


def test_database_url_is_none_raises_error(monkeypatch):
    """Testa se um ValueError é levantado quando DATABASE_URL não está definida."""
    original_url = os.getenv("DATABASE_URL")
    
    monkeypatch.delenv("DATABASE_URL", raising=False)
    
    with pytest.raises(ValueError, match="DATABASE_URL não está definida no ambiente."):
       
        importlib.reload(database_module)
    
    if original_url:
        monkeypatch.setenv("DATABASE_URL", original_url)
    

    importlib.reload(database_module)


def test_create_engine_fails_logs_and_raises_exception(monkeypatch, caplog):
    """Testa o log e a exceção quando create_engine falha."""
    original_url = os.getenv("DATABASE_URL")
    
    monkeypatch.setenv("DATABASE_URL", "mysql+mysqlconnector://invalid_user:invalid_pass@localhost:3306/invalid_db")

    with patch("sqlalchemy.create_engine", side_effect=Exception("Falha na conexão simulada")):
        with pytest.raises(Exception, match="Falha na conexão simulada"):
            with caplog.at_level(logging.ERROR):
                importlib.reload(database_module)
    
    assert "Falha ao criar o engine do SQLAlchemy" in caplog.text

    if original_url:
        monkeypatch.setenv("DATABASE_URL", original_url)
    

    importlib.reload(database_module)