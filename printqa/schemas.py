# printqa/schemas.py

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class ErrorResponse(BaseModel):
    detail: str

class AnalysisResultBase(BaseModel):
    file_name: str
    is_watertight: bool
    has_inverted_faces: bool
    file_size: Optional[int] = None
    vertices_count: Optional[int] = None
    faces_count: Optional[int] = None
    analysis_duration: Optional[int] = None

class AnalysisResultCreate(AnalysisResultBase):
    pass

class AnalysisResult(AnalysisResultBase):
    id: int
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)