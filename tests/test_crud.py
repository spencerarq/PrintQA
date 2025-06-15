# tests/test_crud.py
import os
import pytest
import time
from pathlib import Path
from datetime import datetime
from sqlalchemy.orm import Session # Engine é usado como type hint
from sqlalchemy import Engine # desc e models não são usados neste arquivo

def load_env_variables():
    """Carrega variáveis de ambiente do arquivo .env"""
    try:
        from dotenv import load_dotenv
        project_root = Path(__file__).parent.parent
        env_path = project_root / ".env"
        load_dotenv(env_path)
        return True
    except ImportError:
        # Fallback manual se python-dotenv não estiver disponível
        project_root = Path(__file__).parent.parent
        env_file = project_root / ".env"
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip().strip('"\'')
            return True
        return False

# Carrega as variáveis ANTES de importar qualquer módulo
load_env_variables()

@pytest.fixture(scope="module")
def test_db():
    """Fixture que prepara o banco para testes."""
    database_url = os.getenv("DATABASE_URL")
    
    if database_url is None:
        pytest.skip("DATABASE_URL não está definida")
    
    try:
        # Importa após carregar as variáveis de ambiente
        from printqa.database import Base, engine
        
        # Cria as tabelas
        Base.metadata.create_all(bind=engine)
        yield engine
        
    except Exception as e:
        pytest.skip(f"Não foi possível conectar ao banco: {str(e)}")

@pytest.fixture
def db_session(test_db: Engine):
    """Fixture que fornece uma sessão de banco para cada teste."""
    from sqlalchemy.orm import sessionmaker
    
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_db)
    
    connection = test_db.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()

def test_create_analysis_result_basic(db_session: Session):
    """Testa criação básica de resultado de análise."""
    from printqa.crud import create_analysis_result
    
    result = create_analysis_result(
        db=db_session,
        file_name="test_basic.stl",
        is_watertight=True,
        has_inverted_faces=False
    )
    
    assert result.id is not None
    assert result.file_name == "test_basic.stl"
    assert result.is_watertight is True
    assert result.has_inverted_faces is False
    assert result.timestamp is not None

def test_create_analysis_result_with_all_fields(db_session: Session):
    """Testa criação de resultado com todos os campos opcionais."""
    from printqa.crud import create_analysis_result
    
    result = create_analysis_result(
        db=db_session,
        file_name="test_complete.stl",
        is_watertight=False,
        has_inverted_faces=True,
        file_size=2048,
        vertices_count=150,
        faces_count=300,
        analysis_duration=750
    )
    
    assert result.file_name == "test_complete.stl"
    assert result.is_watertight is False
    assert result.has_inverted_faces is True
    assert result.file_size == 2048
    assert result.vertices_count == 150
    assert result.faces_count == 300
    assert result.analysis_duration == 750

def test_get_analysis_result(db_session: Session):
    """Testa busca de resultado por ID."""
    from printqa.crud import create_analysis_result, get_analysis_result
    
    # Cria um resultado
    created_result = create_analysis_result(
        db=db_session,
        file_name="test_get.stl",
        is_watertight=True,
        has_inverted_faces=False
    )
    
    # Busca o resultado
    found_result = get_analysis_result(db_session, created_result.id)
    
    assert found_result is not None
    assert found_result.id == created_result.id
    assert found_result.file_name == "test_get.stl"

def test_get_analysis_result_not_found(db_session: Session):
    """Testa busca de resultado inexistente."""
    from printqa.crud import get_analysis_result
    
    result = get_analysis_result(db_session, 99999)  # ID inexistente
    assert result is None

def test_get_analysis_result_by_filename(db_session: Session):
    """Testa busca de resultado por nome do arquivo."""
    from printqa.crud import create_analysis_result, get_analysis_result_by_filename
    
    # Cria o primeiro resultado
    result1 = create_analysis_result(
        db=db_session,
        file_name="test_filename.stl",
        is_watertight=True,
        has_inverted_faces=False,
        vertices_count=100  # Valor único para identificar este resultado
    )
    
    # Pequena pausa para garantir timestamps diferentes
    time.sleep(0.1)
    
    # Cria o segundo resultado (mais recente)
    result2 = create_analysis_result(
        db=db_session,
        file_name="test_filename.stl",
        is_watertight=False,
        has_inverted_faces=True,
        vertices_count=200  # Valor único para identificar este resultado
    )
    
    # Busca pelo nome do arquivo (deve retornar o mais recente)
    found_result = get_analysis_result_by_filename(db_session, "test_filename.stl")
    
    assert found_result is not None
    assert found_result.file_name == "test_filename.stl"
    
    # Verifica se é o resultado mais recente pelos valores únicos
    # ao invés de comparar pelo ID
    assert found_result.is_watertight is False
    assert found_result.has_inverted_faces is True
    assert found_result.vertices_count == 200

def test_get_analysis_result_by_filename_not_found(db_session: Session):
    """Testa busca por nome de arquivo inexistente."""
    from printqa.crud import get_analysis_result_by_filename
    
    result = get_analysis_result_by_filename(db_session, "inexistente.stl")
    assert result is None

def test_get_analysis_results_no_filters(db_session: Session):
    """Testa listagem de resultados sem filtros."""
    from printqa.crud import create_analysis_result, get_analysis_results
    
    # Cria alguns resultados
    results = []
    for i in range(5):
        result = create_analysis_result(
            db=db_session,
            file_name=f"test_{i}.stl",
            is_watertight=i % 2 == 0,
            has_inverted_faces=i % 3 == 0
        )
        results.append(result)
    
    # Lista todos os resultados
    all_results = get_analysis_results(db_session)
    
    assert len(all_results) >= 5
    # Verifica se estão ordenados por timestamp decrescente
    timestamps = [r.timestamp for r in all_results]
    assert timestamps == sorted(timestamps, reverse=True)

def test_get_analysis_results_with_pagination(db_session: Session):
    """Testa listagem com paginação."""
    from printqa.crud import create_analysis_result, get_analysis_results
    
    # Cria alguns resultados
    for i in range(10):
        create_analysis_result(
            db=db_session,
            file_name=f"paginate_{i}.stl",
            is_watertight=True,
            has_inverted_faces=False
        )
    
    # Testa paginação
    page1 = get_analysis_results(db_session, skip=0, limit=3)
    page2 = get_analysis_results(db_session, skip=3, limit=3)
    
    assert len(page1) == 3
    assert len(page2) == 3
    
    # Verifica que são resultados diferentes
    page1_ids = {r.id for r in page1}
    page2_ids = {r.id for r in page2}
    assert len(page1_ids.intersection(page2_ids)) == 0

def test_get_analysis_results_watertight_filter(db_session: Session):
    """Testa filtro por watertight."""
    from printqa.crud import create_analysis_result, get_analysis_results
    
    # Cria resultados watertight e não-watertight
    create_analysis_result(db_session, "watertight1.stl", True, False)
    create_analysis_result(db_session, "watertight2.stl", True, False)
    create_analysis_result(db_session, "not_watertight.stl", False, False)
    
    # Filtra apenas watertight
    watertight_results = get_analysis_results(db_session, watertight_only=True)
    non_watertight_results = get_analysis_results(db_session, watertight_only=False)
    
    # Verifica filtros
    for result in watertight_results:
        if result.file_name in ["watertight1.stl", "watertight2.stl", "not_watertight.stl"]:
            assert result.is_watertight is True
    
    for result in non_watertight_results:
        if result.file_name in ["watertight1.stl", "watertight2.stl", "not_watertight.stl"]:
            assert result.is_watertight is False

def test_get_analysis_results_inverted_faces_filter(db_session: Session):
    """Testa filtro por faces invertidas."""
    from printqa.crud import create_analysis_result, get_analysis_results
    
    # Cria resultados com e sem faces invertidas
    create_analysis_result(db_session, "clean1.stl", True, False)
    create_analysis_result(db_session, "clean2.stl", True, False)
    create_analysis_result(db_session, "inverted.stl", True, True)
    
    # Filtra apenas sem faces invertidas
    clean_results = get_analysis_results(db_session, no_inverted_faces_only=True)
    
    # Verifica filtro
    for result in clean_results:
        if result.file_name in ["clean1.stl", "clean2.stl", "inverted.stl"]:
            assert result.has_inverted_faces is False

def test_get_analysis_statistics_empty_db(db_session: Session):
    """Testa estatísticas com banco vazio."""
    from printqa.crud import get_analysis_statistics
    
    # Remove todos os dados para garantir banco vazio para este teste
    from printqa.models import AnalysisResultDB
    db_session.query(AnalysisResultDB).delete()
    db_session.commit()
    
    stats = get_analysis_statistics(db_session)
    
    assert stats['total_analyses'] == 0
    assert stats['watertight_models'] == 0
    assert stats['models_with_inverted_faces'] == 0
    assert stats['watertight_percentage'] == 0
    assert stats['clean_models'] == 0

def test_get_analysis_statistics_with_data(db_session: Session):
    """Testa estatísticas com dados."""
    from printqa.crud import create_analysis_result, get_analysis_statistics
    
    # Cria dados de teste
    test_data = [
        ("model1.stl", True, False),   # Watertight, sem faces invertidas (clean)
        ("model2.stl", True, True),    # Watertight, com faces invertidas
        ("model3.stl", False, False),  # Não watertight, sem faces invertidas
        ("model4.stl", False, True),   # Não watertight, com faces invertidas
        ("model5.stl", True, False),   # Watertight, sem faces invertidas (clean)
    ]
    
    for file_name, is_watertight, has_inverted_faces in test_data:
        create_analysis_result(
            db=db_session,
            file_name=file_name,
            is_watertight=is_watertight,
            has_inverted_faces=has_inverted_faces
        )
    
    stats = get_analysis_statistics(db_session)
    
    assert stats['total_analyses'] >= 5
    assert stats['watertight_models'] >= 3  # model1, model2, model5
    assert stats['models_with_inverted_faces'] >= 2  # model2, model4
    assert stats['clean_models'] >= 2  # model1, model5
    assert 0 <= stats['watertight_percentage'] <= 100

def test_delete_analysis_result_success(db_session: Session):
    """Testa remoção bem-sucedida de resultado."""
    from printqa.crud import create_analysis_result, delete_analysis_result, get_analysis_result
    
    # Cria um resultado
    result = create_analysis_result(
        db=db_session,
        file_name="to_delete.stl",
        is_watertight=True,
        has_inverted_faces=False
    )
    
    result_id = result.id
    
    # Remove o resultado
    success = delete_analysis_result(db_session, result_id)
    
    assert success is True
    
    # Verifica se foi removido
    deleted_result = get_analysis_result(db_session, result_id)
    assert deleted_result is None

def test_delete_analysis_result_not_found(db_session: Session):
    """Testa remoção de resultado inexistente."""
    from printqa.crud import delete_analysis_result
    
    success = delete_analysis_result(db_session, 99999)  # ID inexistente
    assert success is False

def test_update_analysis_result_success(db_session: Session):
    """Testa atualização bem-sucedida de resultado."""
    from printqa.crud import create_analysis_result, update_analysis_result
    
    # Cria um resultado
    result = create_analysis_result(
        db=db_session,
        file_name="to_update.stl",
        is_watertight=True,
        has_inverted_faces=False,
        file_size=1024
    )
    
    # Atualiza o resultado
    updated_result = update_analysis_result(
        db_session,
        result.id,
        is_watertight=False,
        file_size=2048,
        vertices_count=100
    )
    
    assert updated_result is not None
    assert updated_result.id == result.id
    assert updated_result.is_watertight is False
    assert updated_result.file_size == 2048
    assert updated_result.vertices_count == 100
    assert updated_result.file_name == "to_update.stl"  # Não alterado

def test_update_analysis_result_not_found(db_session: Session):
    """Testa atualização de resultado inexistente."""
    from printqa.crud import update_analysis_result
    
    updated_result = update_analysis_result(
        db_session,
        99999,  # ID inexistente
        is_watertight=False
    )
    
    assert updated_result is None

def test_update_analysis_result_invalid_field(db_session: Session):
    """Testa atualização com campo inválido."""
    from printqa.crud import create_analysis_result, update_analysis_result
    
    # Cria um resultado
    result = create_analysis_result(
        db=db_session,
        file_name="invalid_field.stl",
        is_watertight=True,
        has_inverted_faces=False
    )
    
    # Tenta atualizar com campo que não existe
    updated_result = update_analysis_result(
        db_session,
        result.id,
        invalid_field="some_value",  # Campo inexistente
        file_size=1024  # Campo válido
    )
    
    # Deve ter atualizado apenas os campos válidos
    assert updated_result is not None
    assert updated_result.file_size == 1024
    assert not hasattr(updated_result, 'invalid_field')