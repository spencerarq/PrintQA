# tests/test_analysis.py

import pytest
import os # Importar os para os.path.basename
import logging # Para usar caplog.at_level
from unittest.mock import patch, MagicMock # Necessário para simular trimesh e suas classes

import trimesh # Importar trimesh para usar seus tipos e exceções
from printqa.analysis import analyze_file # Importa a função a ser testada

pytestmark = pytest.mark.unit

# Seus testes existentes:
def test_analyze_file_identifies_watertight_mesh(cube_perfect_path: str):
    """Verifica se a análise identifica corretamente uma malha fechada."""
    result = analyze_file(cube_perfect_path)
    assert result["is_watertight"] is True
    assert result["has_inverted_faces"] is False
    assert result["vertices_count"] > 0
    assert result["faces_count"] > 0

def test_analyze_file_identifies_non_watertight_mesh(cube_open_path: str):
    """Verifica se a análise identifica corretamente uma malha aberta."""
    result = analyze_file(cube_open_path)
    assert result["is_watertight"] is False
    # A malha aberta pode ou não ter faces invertidas dependendo do modelo,
    # mas para este teste, geralmente esperamos que não haja explicitamente.
    # Se o fixture `cubo_aberto.stl` não tem faces invertidas, isso é correto.
    assert result["has_inverted_faces"] is False 

def test_analyze_file_identifies_inverted_faces(cube_inverted_path: str):
    """Verifica se a análise identifica faces com normais invertidas."""
    result = analyze_file(cube_inverted_path)
    assert result["has_inverted_faces"] is True

def test_analyze_file_raises_value_error_for_invalid_file(file_load_fail_path: str):
    """
    Verifica se a função levanta ValueError para um arquivo de formato inválido
    ou que não contém uma malha 3D válida (cobre a linha 35).
    """
    with pytest.raises(ValueError, match="não contém uma malha 3D válida"):
        analyze_file(file_load_fail_path)

# NOVO TESTE: Cobre as linhas 18-22 (except Exception as e:)
def test_analyze_file_raises_value_error_on_load_exception_non_existent_file(caplog):
    """
    Testa se analyze_file levanta ValueError em caso de erro ao carregar um arquivo inexistente.
    Cobre o bloco `except Exception as e:` na linha 20 e 21.
    Não usa mock para trimesh.load_mesh, mas confia que ela levantará FileNotFoundError.
    """
    non_existent_path = "nonexistent_file.stl"
    with caplog.at_level(logging.ERROR, logger='printqa.analysis'):
        with pytest.raises(ValueError, match=f"Falha ao carregar o arquivo: O arquivo '{os.path.basename(non_existent_path)}' é inválido ou está vazio."):
            analyze_file(non_existent_path)
        assert f"Falha ao carregar o arquivo '{non_existent_path}': [Errno 2] No such file or directory" in caplog.text


# NOVO TESTE: Cobre a linha 39 (if not mesh.geometry) para cenas vazias
def test_analyze_file_handles_empty_trimesh_scene_mocked():
    """
    Testa se analyze_file lida com cenas Trimesh vazias, levantando ValueError.
    Cobre 'if isinstance(mesh, trimesh.Scene)' e 'if not mesh.geometry'.
    
    COMENTANDO O USO DE MOCK: Necessário para criar um objeto `trimesh.Scene` artificial
    que `trimesh.load_mesh` retornaria, sem precisar de um arquivo real no disco
    para simular este cenário específico. Também mocka `os.path.getsize` para evitar `FileNotFoundError`.
    """
    mock_scene = MagicMock(spec=trimesh.Scene)
    mock_scene.geometry = {} # Simula uma cena sem geometria

    with patch('os.path.getsize', return_value=100): # Mock os.path.getsize para evitar FileNotFoundError
        with patch('trimesh.load_mesh', return_value=mock_scene): # Mock trimesh.load_mesh para retornar cena vazia
            with pytest.raises(ValueError, match="Cena 3D vazia, nenhum modelo para analisar."):
                analyze_file("dummy_empty_scene.stl")


# NOVO TESTE: Cobre a linha 41 (trimesh.util.concatenate) para cenas com geometria
def test_analyze_file_concatenates_trimesh_scene_with_geometry_mocked(cube_perfect_path: str):
    """
    Testa se analyze_file concatena cenas Trimesh com geometria.
    Cobre 'mesh = trimesh.util.concatenate(list(mesh.geometry.values()))'.
    
    COMENTANDO O USO DE MOCK: Necessário para simular uma `trimesh.Scene` com geometria
    e verificar que `trimesh.util.concatenate` é chamado. Mocka `os.path.getsize`
    e o comportamento da malha resultante da concatenação.
    """
    # Mock de uma malha que estaria dentro da cena
    mock_sub_mesh = MagicMock(spec=trimesh.Trimesh)
    mock_sub_mesh.is_watertight = True
    mock_sub_mesh.is_winding_consistent = True
    mock_sub_mesh.vertices = [0, 0, 0, 1, 1, 1] # Dados dummy para vértices
    mock_sub_mesh.faces = [[0, 1, 2], [1, 2, 3]] # Dados dummy para faces

    # Mock da cena Trimesh
    mock_scene = MagicMock(spec=trimesh.Scene)
    mock_scene.geometry = {'mesh_part_1': mock_sub_mesh} # Simula uma cena com uma malha

    # Mock da função trimesh.load_mesh para retornar a mock_scene
    with patch('os.path.getsize', return_value=1000): # Mock os.path.getsize
        with patch('trimesh.load_mesh', return_value=mock_scene):
            # Mock da função trimesh.util.concatenate para verificar sua chamada
            # e retornar uma malha válida (o mock_sub_mesh neste caso, pois a concatenação "resulta" em uma malha)
            with patch('trimesh.util.concatenate', return_value=mock_sub_mesh) as mock_concatenate:
                result = analyze_file(cube_perfect_path)

                # Verifica se trimesh.util.concatenate foi chamado com os valores corretos
                mock_concatenate.assert_called_once_with([mock_sub_mesh])
                
                # Verifica as propriedades da malha resultante (que vem do mock_sub_mesh)
                assert result["is_watertight"] is True
                assert result["has_inverted_faces"] is False
                assert result["vertices_count"] == len(mock_sub_mesh.vertices)
                assert result["faces_count"] == len(mock_sub_mesh.faces)
                assert result["analysis_duration"] >= 0 # Tempo de análise deve ser não negativo