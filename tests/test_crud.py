# tests/test_crud.py (versão final)

import pytest
from sqlalchemy.orm import Session
from printqa import crud, schemas

pytestmark = pytest.mark.integration

def test_create_and_get_analysis_result(db_session: Session):
    """Testa a criação e a recuperação de um único resultado."""
    analysis_data = schemas.AnalysisResultCreate(
        file_name="test_cube.stl", is_watertight=True, has_inverted_faces=False
    )
    db_analysis = crud.create_analysis_result(db=db_session, analysis=analysis_data)
    retrieved = crud.get_analysis_result(db=db_session, result_id=db_analysis.id)
    assert retrieved is not None
    assert retrieved.file_name == "test_cube.stl"
    assert retrieved.is_watertight is True

def test_get_analysis_results_with_filters(db_session: Session):
    """Testa a listagem e filtros de resultados."""
    crud.create_analysis_result(db_session, schemas.AnalysisResultCreate(file_name="p1.stl", is_watertight=True, has_inverted_faces=False))
    crud.create_analysis_result(db_session, schemas.AnalysisResultCreate(file_name="p2.stl", is_watertight=True, has_inverted_faces=True))
    crud.create_analysis_result(db_session, schemas.AnalysisResultCreate(file_name="p3.stl", is_watertight=False, has_inverted_faces=False))
    
    # Testa o filtro watertight_only
    results_watertight = crud.get_analysis_results(db=db_session, watertight_only=True)
    assert len(results_watertight) >= 2
    assert all(r.is_watertight for r in results_watertight)

    # Testa no_inverted_faces_only=True (queremos has_inverted_faces=False)
    results_no_inverted = crud.get_analysis_results(db=db_session, no_inverted_faces_only=True)
    assert len(results_no_inverted) >= 2
    assert all(r.has_inverted_faces is False for r in results_no_inverted)

    # Testa no_inverted_faces_only=False (queremos has_inverted_faces=True)
    results_with_inverted = crud.get_analysis_results(db=db_session, no_inverted_faces_only=False)
    assert len(results_with_inverted) >= 1
    assert all(r.has_inverted_faces is True for r in results_with_inverted)
    # FIM DA ALTERAÇÃO

def test_get_analysis_result_by_filename(db_session: Session):
    """Testa a busca de resultado pelo nome do arquivo."""
    crud.create_analysis_result(db_session, schemas.AnalysisResultCreate(file_name="specific_name.stl", is_watertight=True, has_inverted_faces=False))
    retrieved = crud.get_analysis_result_by_filename(db=db_session, file_name="specific_name.stl")
    assert retrieved is not None
    assert retrieved.file_name == "specific_name.stl"

def test_get_statistics(db_session: Session):
    """Testa a função de estatísticas."""
    initial_stats = crud.get_analysis_statistics(db=db_session)
    
    crud.create_analysis_result(db_session, schemas.AnalysisResultCreate(file_name="stats_test_1.stl", is_watertight=True, has_inverted_faces=False))
    crud.create_analysis_result(db_session, schemas.AnalysisResultCreate(file_name="stats_test_2.stl", is_watertight=False, has_inverted_faces=True))

    new_stats = crud.get_analysis_statistics(db=db_session)
    assert new_stats['total_analyses'] == initial_stats['total_analyses'] + 2
    assert new_stats['watertight_models'] == initial_stats['watertight_models'] + 1
    assert new_stats['models_with_inverted_faces'] == initial_stats['models_with_inverted_faces'] + 1
    assert new_stats['clean_models_count'] == initial_stats['clean_models_count'] + 1

def test_delete_analysis_result(db_session: Session):
    """Testa a remoção de um resultado."""
    item = crud.create_analysis_result(db_session, schemas.AnalysisResultCreate(file_name="to_delete.stl", is_watertight=True, has_inverted_faces=False))
    deleted = crud.delete_analysis_result(db=db_session, result_id=item.id)
    assert deleted is True
    assert crud.get_analysis_result(db=db_session, result_id=item.id) is None

def test_update_analysis_result(db_session: Session):
    """Testa a atualização de um resultado."""
    item = crud.create_analysis_result(db_session, schemas.AnalysisResultCreate(file_name="to_update.stl", is_watertight=False, has_inverted_faces=True))
    updated = crud.update_analysis_result(db=db_session, result_id=item.id, is_watertight=True, has_inverted_faces=False)
    assert updated is not None
    assert updated.is_watertight is True
    assert updated.has_inverted_faces is False

def test_delete_nonexistent_result(db_session: Session):
    """
    Testa a tentativa de remoção de um resultado que não existe.
    Cobre a linha `return False` em `delete_analysis_result`.
    """
    deleted = crud.delete_analysis_result(db=db_session, result_id=999999)
    assert deleted is False

def test_update_nonexistent_result(db_session: Session):
    """
    Testa a tentativa de atualização de um resultado que não existe.
    Cobre a linha `return None` em `update_analysis_result`.
    """
    updated = crud.update_analysis_result(db=db_session, result_id=999999, is_watertight=True)
    assert updated is None
