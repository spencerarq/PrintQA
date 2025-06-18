# printqa/analysis.py

import trimesh
import logging
import os
import time

logger = logging.getLogger(__name__)

def analyze_file(file_path: str) -> dict:
    """
    Carrega um modelo 3D, analisa suas propriedades e retorna um dicionário com os resultados.
    """
    logger.info(f"Iniciando análise para o arquivo: {file_path}")
    start_time = time.monotonic()

    try:
        file_size = os.path.getsize(file_path)
        mesh = trimesh.load_mesh(file_path, force='mesh')
    except Exception as e:
        logger.error(f"Falha ao carregar o arquivo '{file_path}': {e}")
        raise ValueError(f"Falha ao carregar o arquivo: O arquivo '{os.path.basename(file_path)}' é inválido ou está vazio.")

    if isinstance(mesh, trimesh.Scene):
        if not mesh.geometry:
            raise ValueError("Cena 3D vazia, nenhum modelo para analisar.")
        mesh = trimesh.util.concatenate(list(mesh.geometry.values()))

    if not hasattr(mesh, 'faces') or len(mesh.faces) == 0:
        raise ValueError(f"O arquivo '{os.path.basename(file_path)}' não contém uma malha 3D válida.")

    has_inverted_faces = not bool(mesh.is_winding_consistent)
    end_time = time.monotonic()
    analysis_duration = int((end_time - start_time) * 1000)

    logger.info(f"Análise de '{file_path}' concluída em {analysis_duration}ms.")

    return {
        "is_watertight": bool(mesh.is_watertight),
        "has_inverted_faces": has_inverted_faces,
        "vertices_count": len(mesh.vertices),
        "faces_count": len(mesh.faces),
        "file_size": file_size,
        "analysis_duration": analysis_duration,
    }