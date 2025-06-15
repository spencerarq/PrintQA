# tests/test_database.py
import os
import pytest
from pathlib import Path
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker, Session
from unittest.mock import patch
import sys
from io import StringIO

from dotenv import load_dotenv
load_dotenv()

from printqa.database import Base, engine, SessionLocal, get_db, create_tables, drop_tables
from printqa.models import AnalysisResultDB
from printqa import init_database, check_config, __version__

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    pytest.skip("DATABASE_URL não está definida no .env. Pule os testes de banco de dados.")

@pytest.fixture(scope="module")
def test_db_engine():
    """Fixture que prepara o banco para testes.
    Cria e dropa as tabelas uma vez por módulo de teste.
    Cobre as funções create_tables e drop_tables em printqa/database.py.
    """
    try:
        drop_tables()
        create_tables()
        yield engine
    except Exception as e:
        pytest.skip(f"Não foi possível configurar o banco de dados para testes: {e}")
    finally:
        try:
            drop_tables()
        except Exception as e:
            print(f"Erro no cleanup do DB: {e}")

@pytest.fixture
def db_session_fixture(test_db_engine):
    """Fornece uma sessão de banco de dados transacional para cada teste."""
    connection = test_db_engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()

def test_env_loading():
    database_url = os.getenv("DATABASE_URL")
    assert database_url is not None, "DATABASE_URL não está definida. Verifique o arquivo .env"
    assert "mysql" in database_url.lower(), "DATABASE_URL deve ser uma URL do MySQL/MariaDB"

def test_database_connection(test_db_engine):
    try:
        with test_db_engine.connect() as connection:
            result = connection.execute(text("SELECT 1 as test"))
            value = result.scalar()
            assert value == 1, "Falha na query de teste básica"
    except Exception as e:
        pytest.fail(f"Falha na conexão com o banco de dados: {str(e)}")

def test_database_import():
    try:
        assert Base is not None
        assert engine is not None
        assert SessionLocal is not None
        assert get_db is not None
        assert AnalysisResultDB is not None
    except Exception as e:
        pytest.fail(f"Falha ao importar módulos do database: {str(e)}")

def test_create_tables_function_coverage(test_db_engine):
    inspector = inspect(test_db_engine)
    assert 'analysis_results' in inspector.get_table_names()


def test_create_analysis_result(db_session_fixture):
    analysis_result = AnalysisResultDB(
        file_name="test_model_db_insert.stl",
        is_watertight=True,
        has_inverted_faces=False,
        file_size=1024,
        vertices_count=100,
        faces_count=200,
        analysis_duration=500
    )
    
    db_session_fixture.add(analysis_result)
    db_session_fixture.commit()
    db_session_fixture.refresh(analysis_result)

    assert analysis_result.id is not None
    saved_result = db_session_fixture.query(AnalysisResultDB).filter_by(file_name="test_model_db_insert.stl").first()
    assert saved_result is not None
    assert saved_result.file_name == "test_model_db_insert.stl"
    assert saved_result.is_watertight is True
    assert saved_result.has_inverted_faces is False
    assert saved_result.file_size == 1024
    assert saved_result.vertices_count == 100
    assert saved_result.faces_count == 200
    assert saved_result.analysis_duration == 500

def test_query_analysis_results(db_session_fixture):
    results_to_add = [
        AnalysisResultDB(file_name="model1.stl", is_watertight=True, has_inverted_faces=False, file_size=2048),
        AnalysisResultDB(file_name="model2.stl", is_watertight=False, has_inverted_faces=True, file_size=4096),
        AnalysisResultDB(file_name="model3.stl", is_watertight=True, has_inverted_faces=True, file_size=8192)
    ]
    db_session_fixture.add_all(results_to_add)
    db_session_fixture.commit()
    
    all_results = db_session_fixture.query(AnalysisResultDB).all()
    assert len(all_results) >= 3

    watertight_results = db_session_fixture.query(AnalysisResultDB).filter_by(is_watertight=True).all()
    assert len(watertight_results) >= 2

    non_watertight_results = db_session_fixture.query(AnalysisResultDB).filter_by(is_watertight=False).all()
    assert len(non_watertight_results) >= 1

def test_model_methods(db_session_fixture):
    result = AnalysisResultDB(
        file_name="test_methods.stl",
        is_watertight=True,
        has_inverted_faces=False,
        file_size=1024,
        vertices_count=100,
        faces_count=200,
        analysis_duration=500
    )
    
    db_session_fixture.add(result)
    db_session_fixture.commit()
    db_session_fixture.refresh(result)

    result_dict = result.to_dict()
    assert isinstance(result_dict, dict)
    assert result_dict['file_name'] == "test_methods.stl"
    assert result_dict['is_watertight'] is True
    assert result_dict['has_inverted_faces'] is False
    assert result_dict['file_size'] == 1024
    assert result_dict['vertices_count'] == 100
    assert result_dict['faces_count'] == 200
    assert result_dict['analysis_duration'] == 500

    repr_str = repr(result)
    assert "AnalysisResultDB" in repr_str
    assert "test_methods.stl" in repr_str

def test_database_url_not_defined_raises_error():
    original_db_url = os.getenv("DATABASE_URL")
    
    # Mock os.getenv para retornar None quando DATABASE_URL é solicitado
    with patch('printqa.database.os.getenv', side_effect=lambda key, default=None: None if key == "DATABASE_URL" else os.environ.get(key, default)):
        if 'printqa.database' in sys.modules:
            del sys.modules['printqa.database']
        
        with pytest.raises(ValueError, match="DATABASE_URL não está definida"):
            from printqa.database import engine as temp_engine
            _ = temp_engine 

    if original_db_url is not None:
        os.environ["DATABASE_URL"] = original_db_url
    if 'printqa.database' in sys.modules:
        del sys.modules['printqa.database']

def test_get_db_yields_session_and_closes():
    from printqa.database import get_db
    from sqlalchemy.orm import Session

    db_generator = get_db()
    session_instance = next(db_generator)

    assert isinstance(session_instance, Session)
    assert session_instance.is_active is True

    with patch.object(session_instance, 'close') as mock_session_close_method:
        try:
            next(db_generator)
        except StopIteration:
            pass

        mock_session_close_method.assert_called_once()