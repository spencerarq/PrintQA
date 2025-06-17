# conftest.py

import pytest
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from pathlib import Path

from printqa.database import Base
from printqa.main import app
from fastapi.testclient import TestClient

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL não definida!")

engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(test_db):
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

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