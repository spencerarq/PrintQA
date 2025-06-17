# printqa/crud.py

from sqlalchemy.orm import Session
from typing import List, Optional
from . import models, schemas

def create_analysis_result(db: Session, analysis: schemas.AnalysisResultCreate) -> models.AnalysisResultDB:
    db_analysis = models.AnalysisResultDB(**analysis.model_dump())
    
    db.add(db_analysis)
    db.commit()
    db.refresh(db_analysis)
    
    return db_analysis

def get_analysis_result(db: Session, result_id: int) -> Optional[models.AnalysisResultDB]:
    return db.query(models.AnalysisResultDB).filter(models.AnalysisResultDB.id == result_id).first()

def get_analysis_result_by_filename(db: Session, file_name: str) -> Optional[models.AnalysisResultDB]:
   
    return (db.query(models.AnalysisResultDB)
              .filter(models.AnalysisResultDB.file_name == file_name)
              .order_by(models.AnalysisResultDB.timestamp.desc(), models.AnalysisResultDB.id.desc())
              .first())

def get_analysis_results(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    watertight_only: Optional[bool] = None,
    no_inverted_faces_only: Optional[bool] = None
) -> List[models.AnalysisResultDB]:
    query = db.query(models.AnalysisResultDB)
    
    if watertight_only is not None:
        query = query.filter(models.AnalysisResultDB.is_watertight == watertight_only)
    
    if no_inverted_faces_only is not None:
        
        query = query.filter(models.AnalysisResultDB.has_inverted_faces != no_inverted_faces_only)
    
    return query.order_by(models.AnalysisResultDB.timestamp.desc()).offset(skip).limit(limit).all()

def get_analysis_statistics(db: Session) -> dict:
    total_count = db.query(models.AnalysisResultDB).count()
    watertight_count = db.query(models.AnalysisResultDB).filter(models.AnalysisResultDB.is_watertight == True).count()
    inverted_faces_count = db.query(models.AnalysisResultDB).filter(models.AnalysisResultDB.has_inverted_faces == True).count()
    
    return {
        'total_analyses': total_count,
        'watertight_models': watertight_count,
        'models_with_inverted_faces': inverted_faces_count,
        'watertight_percentage': (watertight_count / total_count * 100) if total_count > 0 else 0,
        'clean_models_count': db.query(models.AnalysisResultDB).filter(
            models.AnalysisResultDB.is_watertight == True,
            models.AnalysisResultDB.has_inverted_faces == False
        ).count()
    }

def delete_analysis_result(db: Session, result_id: int) -> bool:
    result = db.query(models.AnalysisResultDB).get(result_id)
    if result:
        db.delete(result)
        db.commit()
        return True
    return False

def update_analysis_result(db: Session, result_id: int, **kwargs) -> Optional[models.AnalysisResultDB]:
    result = db.query(models.AnalysisResultDB).get(result_id)
    if result:
        for key, value in kwargs.items():
            if hasattr(result, key):
                setattr(result, key, value)
        db.commit()
        db.refresh(result)
        return result
    return None
