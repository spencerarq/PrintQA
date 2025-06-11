# printqa/analysis.py
import os
import trimesh

def analyze_file(file_path: str) -> dict:
    """ Analisa um único arquivo de modelo 3D e retorna um dicionário com os resultados. """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Arquivo não encontrado em: {file_path}")
    
    try:
        mesh = trimesh.load(file_path, force='mesh')
    except Exception as e:
        return {"error": f"Falha ao carregar o arquivo: {e}"}

    report = {
        "is_watertight": bool(mesh.is_watertight),
        "has_inverted_faces": not bool(mesh.is_winding_consistent)
    }
    
    return report