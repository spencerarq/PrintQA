# conftest.py 

import pytest
import os
import logging
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from pathlib import Path

# Importações da aplicação
from printqa.database import Base
from printqa import models  # Garante que os modelos sejam registrados
from printqa.main import app
from fastapi.testclient import TestClient

load_dotenv()

@pytest.fixture(scope="session")
def db_engine():
    """
    Cria uma instância do SQLAlchemy Engine que dura por toda a sessão de testes.
    """
    test_db_url = os.getenv("DATABASE_URL")
    if not test_db_url:
        raise ValueError("DATABASE_URL não definida para o engine de teste!")
    
    engine = create_engine(test_db_url, echo=False)
    yield engine
    engine.dispose()

@pytest.fixture(scope="module")
def setup_database(db_engine):
    """
    Fixture com escopo de MÓDULO.
    Cria todas as tabelas antes do primeiro teste de um arquivo ser executado
    e apaga todas as tabelas depois que o último teste do arquivo terminar.
    Isso garante isolamento entre os arquivos de teste.
    """
    try:
        import printqa.models
        Base.metadata.create_all(bind=db_engine)
        logging.info(f"Tabelas criadas para o módulo.")
        yield
    finally:
        Base.metadata.drop_all(bind=db_engine)
        logging.info(f"Tabelas apagadas para o módulo.")

@pytest.fixture(scope="function")
def db_session(db_engine, setup_database) -> Generator[Session, None, None]:
    """
    Fixture com escopo de FUNÇÃO que fornece uma sessão de banco de dados.
    - Depende de `setup_database` para garantir que as tabelas do módulo existam.
    - Usa uma transação que é revertida ao final de cada teste para isolar os dados.
    """
    connection = db_engine.connect()
    transaction = connection.begin()
    
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()

# As fixtures abaixo permanecem as mesmas
@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture(scope="session")
def fixtures_path() -> Path:
    return Path("/app/tests/fixtures")

@pytest.fixture
def cube_perfect_path(fixtures_path: Path) -> str:
    return str(fixtures_path / "cube_perfect.stl")

@pytest.fixture
def cube_open_path(fixtures_path: Path) -> str:
    return str(fixtures_path / "cubo_aberto.stl")

@pytest.fixture
def cube_inverted_path(fixtures_path: Path) -> str:
    return str(fixtures_path / "cubo_invertido.stl")

@pytest.fixture
def file_load_fail_path(fixtures_path: Path) -> str:
    return str(fixtures_path / "arquivoFalhaCarregamento.stl")

@pytest.fixture(autouse=True)
def cap_log_error(caplog):
    with caplog.at_level(logging.ERROR):
        yield