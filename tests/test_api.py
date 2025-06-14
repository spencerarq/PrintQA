# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import os
import io 

from printqa.main import app
from printqa.schemas import AnalysisResult, ErrorResponse

client = TestClient(app)

# Teste 1: Verificar se o endpoint raiz retorna a mensagem esperada
def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Bem-vindo à API PrintQA! Acesse /docs para a documentação."}

# Teste 2: Lida com arquivo de formato inválido (espera 400 e ErrorResponse)
def test_analyze_model_endpoint_invalid_file_format():
    invalid_file_content = b"This is not a real STL file."
    
    response = client.post(
        "/analyze_model/",
        files={"file": ("invalid.stl", invalid_file_content, "text/plain")}
    )
    
    assert response.status_code == 400
    error_response = ErrorResponse(**response.json())
    assert "Falha ao carregar o arquivo" in error_response.detail


# Teste 3: Testar o endpoint de análise com um arquivo STL válido (CUBO ESTANQUE)
def test_analyze_model_endpoint_valid_stl_file():
    """ Verifica se a API analisa corretamente um arquivo STL válido (cubo estanque)
    e retorna o esquema e resultados esperados. """
    perfect_cube_stl_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'cube_perfect.stl')

    with open(perfect_cube_stl_path, "rb") as f:
        valid_stl_content = f.read()

    valid_file_stream = io.BytesIO(valid_stl_content)

    response = client.post(
        "/analyze_model/",
        files={"file": ("valid_cube.stl", valid_file_stream, "application/octet-stream")}
    )
    
    assert response.status_code == 200
    analysis_result = AnalysisResult(**response.json())
    assert isinstance(analysis_result.is_watertight, bool)
    assert isinstance(analysis_result.has_inverted_faces, bool)
    assert analysis_result.is_watertight is True
    assert analysis_result.has_inverted_faces is False

# Teste 4: Erro interno inesperado no upload/cópia
def test_analyze_model_endpoint_internal_server_error_on_upload_copy():
    with patch('builtins.open') as mock_open:
        mock_open.side_effect = Exception("Simulated disk write error during copy")
        dummy_file_content = b"dummy content"
        response = client.post(
            "/analyze_model/",
            files={"file": ("dummy.txt", dummy_file_content, "text/plain")}
        )
        assert response.status_code == 500
        assert "Ocorreu um erro interno no servidor" in response.json()["detail"]

# Teste 5: Erro interno inesperado na análise (mockando analyze_file)
def test_analyze_model_endpoint_internal_server_error_on_analysis_unexpected_exception():
    with patch('printqa.main.analyze_file') as mock_analyze_file:
        mock_analyze_file.side_effect = TypeError("Erro de tipo inesperado na análise")
        dummy_file_content = b"dummy content"
        response = client.post(
            "/analyze_model/",
            files={"file": ("dummy.txt", dummy_file_content, "text/plain")}
        )
        assert response.status_code == 500
        assert "Ocorreu um erro interno no servidor" in response.json()["detail"]

# Teste 6: Erro na limpeza do arquivo temporário
def test_analyze_model_endpoint_file_cleanup_error():
    with patch('os.remove') as mock_os_remove:
        mock_os_remove.side_effect = OSError("Permissão negada ao remover arquivo")
        valid_stl_content_for_cleanup = b"""
            solid model
              facet normal 0 0 1
                outer loop
                  vertex 0 0 0
                  vertex 1 0 0
                  vertex 0 1 0
                endloop
              endfacet
            endsolid model
        """
        response = client.post(
            "/analyze_model/",
            files={"file": ("valid.stl", io.BytesIO(valid_stl_content_for_cleanup), "application/octet-stream")}
        )
        assert response.status_code == 200 
        assert "is_watertight" in response.json()
        mock_os_remove.assert_called_once()

# Teste 7: FileNotFoundError no main.py 
def test_analyze_model_endpoint_file_not_found_error_on_upload_creation():
    with patch('builtins.open') as mock_open:
        mock_open.side_effect = FileNotFoundError("Simulated directory access error")
        dummy_file_content = b"dummy content"
        response = client.post(
            "/analyze_model/",
            files={"file": ("dummy.txt", dummy_file_content, "text/plain")}
        )
        assert response.status_code == 404
        assert "Arquivo não encontrado no servidor" in response.json()["detail"]
        mock_open.assert_called()

# Teste 8: Validação de MIME Type (retorna 415 Unsupported Media Type)
def test_analyze_model_endpoint_unsupported_mime_type():
    """
    Verifica se a API retorna 415 para tipos de arquivo (MIME Type) não suportados.
    """
    response = client.post(
        "/analyze_model/",
        files={"file": ("image.png", b"dummy_image_data", "image/png")}
    )
    assert response.status_code == 415
    assert "Tipo de arquivo" in response.json()["detail"]
    assert "não suportado" in response.json()["detail"]

# Teste 9: Validação de Tamanho do Arquivo (retorna 413 Payload Too Large)
def test_analyze_model_endpoint_payload_too_large():
    """
    Verifica se a API retorna 413 para arquivos que excedem o tamanho máximo permitido.
    """
    # Cria um conteúdo que simula um arquivo muito grande (ex: 25 MB, se o limite for 20 MB)
    large_file_content = b"a" * (25 * 1024 * 1024)  # 25 MB de bytes 'a'
    
    response = client.post(
        "/analyze_model/",
        files={"file": ("large_model.stl", large_file_content, "application/octet-stream")}
    )
    assert response.status_code == 413
    assert "Arquivo excede o tamanho máximo" in response.json()["detail"]

# Teste 10: Validação adicional - arquivo vazio
def test_analyze_model_endpoint_empty_file():
    """
    Testa o cenário onde um arquivo vazio é enviado.
    """
    response = client.post(
        "/analyze_model/",
        files={"file": ("empty.stl", b"", "application/octet-stream")}
    )
    
    # Arquivo vazio deve ser rejeitado na análise
    assert response.status_code == 400
    assert "Falha ao carregar o arquivo" in response.json()["detail"]
