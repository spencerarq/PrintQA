# tests/test_database.py (versão corrigida)

import pytest
import os
import importlib
import logging
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from sqlalchemy import text, inspect

# Importações da aplicação
from printqa.database import get_db, create_tables, drop_tables, Base
from printqa import models
from printqa import database as database_module

def test_database_connection(db_session: Session):
    """
    Testa se a conexão com o banco de dados pode ser estabelecida.
    """
    assert db_session is not None
    result = db_session.execute(text("SELECT 1"))
    assert result.scalar() == 1

# ... (os testes com mock permanecem os mesmos, não precisam de alteração) ...

def test_get_db_closes_session():
    mock_session = MagicMock(spec=Session)
    with patch('printqa.database.SessionLocal', return_value=mock_session):
        db_generator = get_db()
        db = next(db_generator)
        assert db is mock_session
        try:
            db_generator.send(None)
        except StopIteration:
            pass
        mock_session.close.assert_called_once()


def test_get_db_closes_session_on_exception():
    mock_session = MagicMock(spec=Session)
    with patch('printqa.database.SessionLocal', return_value=mock_session):
        db_generator = get_db()
        db = next(db_generator)
        assert db is mock_session
        with pytest.raises(ValueError, match="Simulated error"):
            try:
                db_generator.throw(ValueError("Simulated error"))
            finally:
                pass
        mock_session.close.assert_called_once()


def test_database_url_is_none_raises_error(monkeypatch):
    with monkeypatch.context() as m:
        m.delenv("DATABASE_URL", raising=False)
        with pytest.raises(ValueError, match="DATABASE_URL não está definida"):
            importlib.reload(database_module)
    importlib.reload(database_module)


def test_invalid_database_url_raises_error_and_logs(caplog, monkeypatch):
    with monkeypatch.context() as m:
        m.setenv("DATABASE_URL", "invalid_url_scheme://user:pass@host:port/db")
        caplog.clear()
        with patch('sqlalchemy.create_engine', side_effect=Exception("Simulated engine creation error")):
            with pytest.raises(Exception):
                importlib.reload(database_module)
            assert "Falha ao criar o engine do SQLAlchemy" in caplog.text
            assert "Simulated engine creation error" in caplog.text
    importlib.reload(database_module)

# ALTERAÇÕES ABAIXO
def test_create_tables(db_engine, setup_database): # Pede a fixture 'db_engine' e 'setup_database'
    """
    Testa se a função create_tables cria as tabelas no banco de dados.
    """
    # Garante que as tabelas não existem antes de criar
    Base.metadata.drop_all(bind=db_engine)
    
    create_tables(target_base=Base, engine_to_use=db_engine)

    inspector = inspect(db_engine)
    assert 'analysis_results' in inspector.get_table_names()


def test_drop_tables(db_engine, setup_database): # Pede a fixture 'db_engine' e 'setup_database'
    """
    Testa se a função drop_tables remove as tabelas do banco de dados.
    """
    # Garante que as tabelas existam para serem removidas
    Base.metadata.create_all(bind=db_engine)

    inspector = inspect(db_engine)
    assert 'analysis_results' in inspector.get_table_names()

    drop_tables(target_base=Base, engine_to_use=db_engine)

    inspector = inspect(db_engine)
    assert 'analysis_results' not in inspector.get_table_names()