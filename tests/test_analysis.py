# tests/test_analysis.py
import pytest
from printqa.analysis import analyze_file

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