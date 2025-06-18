# tests/test_models.py

import pytest
from datetime import datetime
from printqa.models import AnalysisResultDB
from printqa.crud import create_analysis_result
from printqa.schemas import AnalysisResultCreate
from sqlalchemy.orm import Session

def test_analysis_result_db_repr():
    """
    Testa o método __repr__ (representação em string) do modelo AnalysisResultDB.
    Isso garante que a representação legível do objeto esteja funcionando como esperado.
    """
    analysis_data = {
        "file_name": "test_repr_model.stl",
        "is_watertight": True,
        "has_inverted_faces": False,
        "timestamp": datetime(2023, 1, 1, 12, 0, 0),
        "file_size": 1024,
        "vertices_count": 100,
        "faces_count": 50,
        "analysis_duration": 150
    }
    result = AnalysisResultDB(**analysis_data)
    
    expected_repr = f"<AnalysisResultDB(id=None, file_name='{result.file_name}', is_watertight={result.is_watertight})>"
    assert repr(result) == expected_repr

def test_analysis_result_db_to_dict_full_fields(db_session: Session):
    """
    Testa o método to_dict do modelo AnalysisResultDB quando todos os campos
    (incluindo os opcionais) estão preenchidos com valores válidos.
    """
    file_name = "test_to_dict_full.stl"
    analysis_data_dict = {
        "file_name": file_name,
        "is_watertight": True,
        "has_inverted_faces": False,
        "timestamp": datetime(2023, 1, 1, 12, 30, 0),
        "file_size": 2048,
        "vertices_count": 200,
        "faces_count": 100,
        "analysis_duration": 250
    }

    analysis_create_schema = AnalysisResultCreate(**analysis_data_dict)
    created_result = create_analysis_result(db_session, analysis_create_schema)

    expected_dict = {
        'id': created_result.id,
        'file_name': file_name,
        'is_watertight': True,
        'has_inverted_faces': False,
        'timestamp': created_result.timestamp.isoformat(),
        'file_size': 2048,
        'vertices_count': 200,
        'faces_count': 100,
        'analysis_duration': 250
    }
    assert created_result.to_dict() == expected_dict

def test_analysis_result_db_to_dict_nullable_fields(db_session: Session):
    """
    Testa o método to_dict do modelo AnalysisResultDB quando os campos opcionais
    (file_size, vertices_count, faces_count, analysis_duration) são None.
    Isso garante que a serialização funcione corretamente para dados incompletos.
    """
    file_name = "test_to_dict_nullable.stl"
    analysis_data_dict = {
        "file_name": file_name,
        "is_watertight": False,
        "has_inverted_faces": True,
        "file_size": None,
        "vertices_count": None,
        "faces_count": None,
        "analysis_duration": None
    }
    
    analysis_create_schema = AnalysisResultCreate(**analysis_data_dict)
    created_result = create_analysis_result(db_session, analysis_create_schema)

    expected_dict = {
        'id': created_result.id,
        'file_name': file_name,
        'is_watertight': False,
        'has_inverted_faces': True,
        'timestamp': created_result.timestamp.isoformat(),
        'file_size': None,
        'vertices_count': None,
        'faces_count': None,
        'analysis_duration': None
    }
    assert created_result.to_dict() == expected_dict