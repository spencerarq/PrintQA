# printqa/crud.py
"""
Operações CRUD (Create, Read, Update, Delete) para o banco de dados.
"""

from sqlalchemy.orm import Session
from typing import List, Optional
from .models import AnalysisResultDB

def create_analysis_result(
    db: Session, 
    file_name: str,
    is_watertight: bool,
    has_inverted_faces: bool,
    file_size: Optional[int] = None,
    vertices_count: Optional[int] = None,
    faces_count: Optional[int] = None,
    analysis_duration: Optional[int] = None
) -> AnalysisResultDB:
    """
    Cria um novo resultado de análise no banco de dados.
    
    Args:
        db: Sessão do banco de dados
        file_name: Nome do arquivo analisado
        is_watertight: Se a malha é estanque
        has_inverted_faces: Se tem faces invertidas
        file_size: Tamanho do arquivo em bytes (opcional)
        vertices_count: Número de vértices (opcional)
        faces_count: Número de faces (opcional)
        analysis_duration: Duração da análise em ms (opcional)
    
    Returns:
        O resultado criado
    """
    db_result = AnalysisResultDB(
        file_name=file_name,
        is_watertight=is_watertight,
        has_inverted_faces=has_inverted_faces,
        file_size=file_size,
        vertices_count=vertices_count,
        faces_count=faces_count,
        analysis_duration=analysis_duration
    )
    
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    
    return db_result

def get_analysis_result(db: Session, result_id: int) -> Optional[AnalysisResultDB]:
    """
    Busca um resultado de análise por ID.
    
    Args:
        db: Sessão do banco de dados
        result_id: ID do resultado
    
    Returns:
        O resultado encontrado ou None
    """
    return db.query(AnalysisResultDB).filter(AnalysisResultDB.id == result_id).first()

def get_analysis_result_by_filename(db: Session, file_name: str) -> Optional[AnalysisResultDB]:
    """
    Busca um resultado de análise por nome do arquivo.
    
    Args:
        db: Sessão do banco de dados
        file_name: Nome do arquivo
    
    Returns:
        O resultado mais recente para o arquivo ou None
    """
    return (db.query(AnalysisResultDB)
            .filter(AnalysisResultDB.file_name == file_name)
            .order_by(AnalysisResultDB.timestamp.desc(), AnalysisResultDB.id.desc()) # Adiciona id.desc() como desempate
            .first())

def get_analysis_results(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    watertight_only: Optional[bool] = None,
    no_inverted_faces_only: Optional[bool] = None
) -> List[AnalysisResultDB]:
    """
    Lista resultados de análise com filtros opcionais.
    
    Args:
        db: Sessão do banco de dados
        skip: Número de registros para pular
        limit: Número máximo de registros para retornar
        watertight_only: Se True, retorna apenas resultados watertight
        no_inverted_faces_only: Se True, retorna apenas sem faces invertidas
    
    Returns:
        Lista de resultados
    """
    query = db.query(AnalysisResultDB)
    
    if watertight_only is not None:
        query = query.filter(AnalysisResultDB.is_watertight == watertight_only)
    
    if no_inverted_faces_only is not None:
        query = query.filter(AnalysisResultDB.has_inverted_faces == (not no_inverted_faces_only))
    
    return query.order_by(AnalysisResultDB.timestamp.desc()).offset(skip).limit(limit).all()

def get_analysis_statistics(db: Session) -> dict:
    """
    Retorna estatísticas dos resultados de análise.
    
    Args:
        db: Sessão do banco de dados
    
    Returns:
        Dicionário com estatísticas
    """
    total_count = db.query(AnalysisResultDB).count()
    watertight_count = db.query(AnalysisResultDB).filter(AnalysisResultDB.is_watertight == True).count()
    inverted_faces_count = db.query(AnalysisResultDB).filter(AnalysisResultDB.has_inverted_faces == True).count()
    
    return {
        'total_analyses': total_count,
        'watertight_models': watertight_count,
        'models_with_inverted_faces': inverted_faces_count,
        'watertight_percentage': (watertight_count / total_count * 100) if total_count > 0 else 0,
        'clean_models': db.query(AnalysisResultDB).filter(
            AnalysisResultDB.is_watertight == True,
            AnalysisResultDB.has_inverted_faces == False
        ).count()
    }

def delete_analysis_result(db: Session, result_id: int) -> bool:
    """
    Remove um resultado de análise.
    
    Args:
        db: Sessão do banco de dados
        result_id: ID do resultado a ser removido
    
    Returns:
        True se removido com sucesso, False se não encontrado
    """
    result = db.query(AnalysisResultDB).filter(AnalysisResultDB.id == result_id).first()
    
    if result:
        db.delete(result)
        db.commit()
        return True
    
    return False

def update_analysis_result(
    db: Session, 
    result_id: int,
    **kwargs
) -> Optional[AnalysisResultDB]:
    """
    Atualiza um resultado de análise.
    
    Args:
        db: Sessão do banco de dados
        result_id: ID do resultado a ser atualizado
        **kwargs: Campos a serem atualizados
    
    Returns:
        O resultado atualizado ou None se não encontrado
    """
    result = db.query(AnalysisResultDB).filter(AnalysisResultDB.id == result_id).first()
    
    if result:
        for key, value in kwargs.items():
            if hasattr(result, key):
                setattr(result, key, value)
        
        db.commit()
        db.refresh(result)
        return result
    
    return None