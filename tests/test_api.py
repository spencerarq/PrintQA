# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock # <<<< ADICIONAR MagicMock
import os # <<<< ADICIONAR OS se ainda não estiver

# Importa a instância 'app' do seu arquivo main.py
from printqa.main import app

# Cria um cliente de teste para sua aplicação FastAPI
client = TestClient(app)

# Teste 1: Verificar se o endpoint raiz retorna a mensagem esperada
def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Bem-vindo à API PrintQA! Acesse /docs para a documentação."}

# Teste 2: Lida com arquivo de formato inválido (já deve estar passando)
def test_analyze_model_endpoint_invalid_file_format():
    invalid_file_content = b"This is not a real STL file."
    
    response = client.post(
        "/analyze_model/",
        files={"file": ("invalid.stl", invalid_file_content, "text/plain")}
    )
    
    assert response.status_code == 400
    assert "detail" in response.json()
    assert "Falha ao carregar o arquivo" in response.json()["detail"]

# --- NOVOS TESTES PARA COBERTURA 100% DO main.py ---

def test_analyze_model_endpoint_internal_server_error_on_upload_copy():
    """
    Testa se a API retorna 500 para erros internos inesperados durante o upload/cópia do arquivo.
    Cobre o 'except Exception as e:' geral no main.py.
    """
    # Mocka shutil.copyfileobj para levantar uma exceção inesperada
    with patch('shutil.copyfileobj') as mock_copyfileobj:
        mock_copyfileobj.side_effect = Exception("Simulated disk write error")
        
        # O arquivo em si não importa, pois a cópia falhará
        dummy_file_content = b"dummy content"
        response = client.post(
            "/analyze_model/",
            files={"file": ("dummy.txt", dummy_file_content, "text/plain")}
        )
        
        assert response.status_code == 500
        assert "Ocorreu um erro interno no servidor" in response.json()["detail"]

def test_analyze_model_endpoint_internal_server_error_on_analysis_unexpected_exception():
    """
    Testa se a API retorna 500 para erros inesperados vindos da função analyze_file,
    que não são capturados pelo retorno de 'error' (ex: um erro de tipo inesperado).
    Cobre o 'except Exception as e:' geral no main.py.
    """
    # Mocka a função analyze_file para levantar uma exceção que não é um dicionário {"error": ...}
    with patch('printqa.main.analyze_file') as mock_analyze_file:
        mock_analyze_file.side_effect = TypeError("Erro de tipo inesperado na análise")
        
        # O arquivo em si não importa, pois analyze_file será mockado
        dummy_file_content = b"dummy content"
        response = client.post(
            "/analyze_model/",
            files={"file": ("dummy.txt", dummy_file_content, "text/plain")}
        )
        
        assert response.status_code == 500
        assert "Ocorreu um erro interno no servidor" in response.json()["detail"]


def test_analyze_model_endpoint_file_cleanup_error():
    """
    Testa o tratamento de erro no bloco 'finally' ao remover o arquivo temporário.
    Cobre o 'except OSError as e:' dentro do 'finally'.
    """
    # Cria um mock para a função os.remove
    with patch('os.remove') as mock_os_remove:
        # Faz com que os.remove levante um OSError
        mock_os_remove.side_effect = OSError("Permissão negada ao remover arquivo")
        
        # Usa um arquivo válido para que a análise e o retorno 200 aconteçam
        # Conteúdo STL mínimo válido (para que analyze_file não levante ValueError)
        valid_stl_content = b"""
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
            files={"file": ("valid.stl", valid_stl_content, "application/octet-stream")}
        )
        
        # A análise deve passar (retorna 200), mas o erro de limpeza será logado.
        assert response.status_code == 200 
        assert "is_watertight" in response.json() # Verifica que a análise ocorreu
        
        # O importante aqui é que mock_os_remove.called seja True, indicando que o os.remove foi tentado
        mock_os_remove.assert_called_once()
        # O erro de limpeza é capturado pelo logger, não alterando o status HTTP da resposta principal.