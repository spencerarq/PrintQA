# printqa/main.py

import os
import logging
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.orm import Session
from . import crud, models, schemas, database
from .analysis import analyze_file

# models.Base.metadata.create_all(bind=database.engine) # <-- ESTA LINHA FOI REMOVIDA/COMENTADA

logger = logging.getLogger(__name__)
app = FastAPI(title="PrintQA Mesh Analysis API", version="1.1.0")

@app.post("/analyze_mesh/", response_model=schemas.AnalysisResult)
async def analyze_mesh_and_save(
    db: Session = Depends(database.get_db),
    file: UploadFile = File(...)
):
    
    file_contents = await file.read()
    if not file_contents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="O arquivo enviado está vazio."
        )
    upload_dir = "temp_uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)

    try:
        with open(file_path, "wb") as buffer:
            buffer.write(file_contents)
        
        analysis_data = analyze_file(file_path)
        analysis_data['file_name'] = file.filename
        
        analysis_to_create = schemas.AnalysisResultCreate(**analysis_data)
        db_result = crud.create_analysis_result(db=db, analysis=analysis_to_create)
        
        return db_result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.exception(f"Erro inesperado ao processar '{file.filename}': {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Erro interno inesperado.")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)