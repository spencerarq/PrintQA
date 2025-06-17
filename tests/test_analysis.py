# tests/test_analysis.py

import pytest
from printqa.analysis import analyze_file

pytestmark = pytest.mark.unit

def test_analyze_file_identifies_watertight_mesh(cube_perfect_path: str):
    """Verifica se a análise identifica corretamente uma malha fechada."""
    result = analyze_file(cube_perfect_path)
    assert result["is_watertight"] is True
    assert result["has_inverted_faces"] is False

def test_analyze_file_identifies_non_watertight_mesh(cube_open_path: str):
    """Verifica se a análise identifica corretamente uma malha aberta."""
    result = analyze_file(cube_open_path)
    assert result["is_watertight"] is False

def test_analyze_file_identifies_inverted_faces(cube_inverted_path: str):
    """Verifica se a análise identifica faces com normais invertidas."""
    result = analyze_file(cube_inverted_path)
    assert result["has_inverted_faces"] is True

def test_analyze_file_raises_value_error_for_invalid_file(file_load_fail_path: str):
    """Verifica se a função levanta ValueError para um arquivo de formato inválido."""
    with pytest.raises(ValueError, match="não contém uma malha 3D válida"):
        analyze_file(file_load_fail_path)

def test_analyze_file_raises_error_for_nonexistent_file():
    """Garante que uma exceção é levantada se o arquivo não existir."""
    with pytest.raises(ValueError, match="Falha ao carregar o arquivo"):
        analyze_file("nonexistent_file.stl")