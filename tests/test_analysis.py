# tests/test_analysis.py
import pytest
import os
from printqa.analysis import analyze_file
@pytest.mark.testrail(ids=['C2'])
def test_analyze_file_returns_a_dictionary():
    result = analyze_file("tests/fixtures/cube.stl") 
    assert isinstance(result, dict)

def test_analyze_file_raises_error_for_nonexistent_file():
    """ Garante que uma exceção FileNotFoundError é levantada se o arquivo não existir. """
    with pytest.raises(FileNotFoundError):
        analyze_file("nonexistent_file.stl")

def test_analyze_file_identifies_watertight_mesh():
    """ Verifica se a análise identifica corretamente uma malha fechada (watertight). """
    result = analyze_file("tests/fixtures/cube.stl")
    assert result["is_watertight"] is True

def test_analyze_file_identifies_non_watertight_mesh():
    """ Verifica se a análise identifica corretamente uma malha aberta."""
    result = analyze_file("tests/fixtures/cubo_aberto.stl")
    assert result["is_watertight"] is False

def test_analyze_file_identifies_inverted_faces():
    """ Verifica se a análise identifica faces com normais invertidas."""
    result = analyze_file("tests/fixtures/cubo_invertido.stl")
    assert result["has_inverted_faces"] is True

INVALID_FILE_PATH = os.path.join(os.path.dirname(__file__), 'fixtures', 'arquivoFalhaCarregamento.stl')

def test_analyze_file_handles_invalid_file_format():
    """ Verifica se a função analyze_file lida corretamente com arquivos de formato inválido,
    acionando o bloco de exceção genérico. """
    assert os.path.exists(INVALID_FILE_PATH), f"Arquivo de teste inválido não encontrado: {INVALID_FILE_PATH}"
    result = analyze_file(INVALID_FILE_PATH)
    assert isinstance(result, dict)
    assert "error" in result
    assert "Falha ao carregar o arquivo:" in result["error"]