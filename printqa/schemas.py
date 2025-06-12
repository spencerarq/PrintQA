# printqa/schemas.py
from pydantic import BaseModel, Field, ConfigDict 

class AnalysisResult(BaseModel):
    is_watertight: bool = Field(..., description="Indica se a malha do modelo é estanque (fechada).")
    has_inverted_faces: bool = Field(..., description="Indica se a malha do modelo possui faces com normais invertidas.")
    
    model_config = ConfigDict(json_schema_extra={ 
        "example": {
            "is_watertight": True,
            "has_inverted_faces": False
        }
    })

class ErrorResponse(BaseModel):
    detail: str = Field(..., description="Mensagem de erro detalhada.")
    
    model_config = ConfigDict(json_schema_extra={ 
        "example": {"detail": "Falha ao carregar o arquivo: O arquivo 'arquivo_invalido.stl' não pode ser carregado como um modelo 3D válido ou está vazio."}
    })
