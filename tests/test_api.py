# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import os
import io
from fastapi import UploadFile
from printqa.main import app
from printqa.schemas import AnalysisResult, ErrorResponse

client = TestClient(app)

# Teste 1: Verificar se o endpoint raiz retorna a mensagem esperada
def test_read_root():
    """
    Testa o endpoint raiz para garantir que ele retorna a mensagem de boas-vindas esperada.
    """
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Bem-vindo à API PrintQA! Acesse /docs para a documentação."}

# Teste 2: Lida com arquivo de formato inválido (espera 400 e ErrorResponse)
def test_analyze_model_endpoint_invalid_file_format():
    """
    Testa o endpoint de análise com um arquivo de formato inválido,
    esperando um status 400 (Bad Request) e uma resposta de erro apropriada.
    """
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
    """
    Verifica se a API analisa corretamente um arquivo STL válido (cubo estanque)
    e retorna o esquema e resultados esperados.
    """

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

# Teste 4: Erro interno inesperado durante a gravação do arquivo temporário
def test_analyze_model_endpoint_internal_server_error_on_file_save():
    """
    Testa se a API retorna 500 para erros internos inesperados durante
    a gravação do arquivo temporário no disco.
    Cobre o 'except Exception as e:' geral no main.py após a leitura do conteúdo.
    """
    # Mocka 'builtins.open' para levantar uma exceção ao tentar abrir/escrever o arquivo
    with patch('builtins.open', side_effect=Exception("Simulated disk write error")) as mock_open:
        
        dummy_file_content = b"solid test\nfacet normal 0 0 1\nouter loop\nvertex 0 0 0\nvertex 1 0 0\nvertex 0 1 0\nendloop\nendfacet\nendsolid test"
        
        response = client.post(
            "/analyze_model/",
            files={"file": ("test.stl", dummy_file_content, "application/octet-stream")}
        )
        assert response.status_code == 500
        assert "ocorreu um erro interno no servidor" in response.json()["detail"].lower()
        mock_open.assert_called_once() 


# Teste 5: Erro interno inesperado na análise (mockando analyze_file)
def test_analyze_model_endpoint_internal_server_error_on_analysis_unexpected_exception():
    """
    Testa se a API retorna 500 para erros inesperados vindos da função analyze_file,
    que não são capturados pelo retorno de 'error' (ex: um erro de tipo inesperado).
    Cobre o 'except Exception as e:' geral no main.py.
    """
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
    """
    Testa o tratamento de erro no bloco 'finally' ao remover o arquivo temporário.
    Cobre o 'except OSError as e:' dentro do 'finally'.
    """
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

# Teste 7: FileNotFoundError no main.py (cobre a exceção FileNotFoundError)
def test_analyze_model_endpoint_file_not_found_error_on_upload_creation():
    """
    Verifica se a API retorna 404 para FileNotFoundError que ocorrem
    durante a criação/escrita do arquivo temporário no main.py.
    Cobre o 'except FileNotFoundError as e:' no main.py.
    """
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
    
    large_file_content = b"a" * (25 * 1024 * 1024)
    
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
    
    assert response.status_code == 400
    assert "Falha ao carregar o arquivo" in response.json()["detail"]

def test_analyze_model_internal_error_on_file_read():
    """
    Testa se a API retorna 500 se ocorrer um erro inesperado durante file.read().
    Cobre o bloco 'except Exception as e:' em main.py que envolve file.read().
    """
    
    with patch('starlette.datastructures.UploadFile.read', new_callable=AsyncMock) as mock_async_uploadfile_read:
        mock_async_uploadfile_read.side_effect = IOError("Simulated file read I/O error")
        
        dummy_content = b"solid test\nendsolid test" 
        
        response = client.post(
            "/analyze_model/",
            files={"file": ("error_file.stl", io.BytesIO(dummy_content), "application/octet-stream")}
        )

    assert response.status_code == 500
    error_response = ErrorResponse(**response.json())
    assert "Ocorreu um erro interno no servidor: Simulated file read I/O error" in error_response.detail
    
    