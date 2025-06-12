# printqa/analysis.py
import os
import trimesh

def analyze_file(file_path: str) -> dict:
    """ Analisa um único arquivo de modelo 3D e retorna um dicionário com os resultados. """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Arquivo não encontrado em: {file_path}")
    
    try:
        # Tenta carregar a malha. 'force="mesh"' tenta garantir um objeto de malha.
        mesh = trimesh.load(file_path, force='mesh')

        if mesh is None or not hasattr(mesh, 'vertices') or len(mesh.vertices) == 0:
            raise ValueError(f"O arquivo '{file_path}' não pode ser carregado como um modelo 3D válido ou está vazio.")

        report = {
            "is_watertight": bool(mesh.is_watertight),
            "has_inverted_faces": not bool(mesh.is_winding_consistent) 
        }
        
        return report

    except Exception as e: 
        return {"error": f"Falha ao carregar o arquivo: {e}"} 