# printqa/models.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime

from .database import Base

class AnalysisResultDB(Base):
    """ Modelo para armazenar resultados de análise de arquivos 3D. """
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String(255), index=True, nullable=False)
    is_watertight = Column(Boolean, nullable=False)
    has_inverted_faces = Column(Boolean, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    file_size = Column(Integer, nullable=True)
    vertices_count = Column(Integer, nullable=True)
    faces_count = Column(Integer, nullable=True)
    analysis_duration = Column(Integer, nullable=True)

    def __repr__(self):
        return f"<AnalysisResultDB(id={self.id}, file_name='{self.file_name}', is_watertight={self.is_watertight})>"

    def to_dict(self):
        """Converte o modelo para dicionário."""
        return {
            'id': self.id,
            'file_name': self.file_name,
            'is_watertight': self.is_watertight,
            'has_inverted_faces': self.has_inverted_faces,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'file_size': self.file_size,
            'vertices_count': self.vertices_count,
            'faces_count': self.faces_count,
            'analysis_duration': self.analysis_duration
        }