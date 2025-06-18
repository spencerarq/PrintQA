# tests/test_api.py

import pytest
import io
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from printqa import crud
from unittest.mock import patch

pytestmark = [pytest.mark.api, pytest.mark.integration]

def test_analyze_mesh_success_and_persistence(client: TestClient, db_session: Session, cube_perfect_path: str):
    """Testa o fluxo completo e bem-sucedido para o endpoint /analyze_mesh/."""
    with open(cube_perfect_path, "rb") as f:
        response = client.post("/analyze_mesh/", files={"file": ("cube_perfect.stl", f, "model/stl")})

    assert response.status_code == 200
    data = response.json()
    assert data["file_name"] == "cube_perfect.stl"
    
    db_record = crud.get_analysis_result(db=db_session, result_id=data["id"])
    assert db_record is not None
    assert db_record.file_name == "cube_perfect.stl"

def test_upload_empty_file_returns_400(client: TestClient):
    """Testa o cenário de upload de um arquivo completamente vazio."""
    file_data = ("empty_file.txt", io.BytesIO(b""), "application/octet-stream")
    response = client.post("/analyze_mesh/", files={"file": file_data})

    assert response.status_code == 400
    assert response.json()["detail"] == "O arquivo enviado está vazio."

def test_upload_invalid_content_file_returns_400(client: TestClient, file_load_fail_path: str):
    """Testa se o upload de um arquivo com conteúdo inválido retorna um erro 400."""
    with open(file_load_fail_path, "rb") as f:
        response = client.post("/analyze_mesh/", files={"file": ("invalid.stl", f, "model/stl")})

    assert response.status_code == 400
    assert "não contém uma malha 3D válida" in response.json()["detail"]

def test_analyze_mesh_internal_server_error(client, cube_perfect_path):
    """ Testa se um erro 500 é retornado quando uma exceção inesperada ocorre. Isso cobre o bloco 'except Exception' em main.py."""
    # Usamos patch para forçar a função 'analyze_file' a levantar um erro genérico
    with patch("printqa.main.analyze_file", side_effect=Exception("Crash inesperado!")):
        with open(cube_perfect_path, "rb") as f:
            response = client.post("/analyze_mesh/", files={"file": ("cube.stl", f, "model/stl")})
            
    assert response.status_code == 500
    assert response.json() == {"detail": "Ocorreu um erro interno inesperado ao processar o arquivo."}