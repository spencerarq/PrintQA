# printqa/main.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from .analysis import analyze_file
import shutil
import os
import logging
from .schemas import AnalysisResult, ErrorResponse

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

app = FastAPI(
    title="PrintQA Backend API",
    description="API para análise de qualidade de modelos 3D para impressão.",
    version="0.1.0"
)

@app.get("/")
async def read_root():
    return {"message": "Bem-vindo à API PrintQA! Acesse /docs para a documentação."}

@app.post(
    "/analyze_model/",
    response_model=AnalysisResult,
    responses={
        400: {"model": ErrorResponse, "description": "Erro de requisição inválida ou arquivo não processável."},
        500: {"model": ErrorResponse, "description": "Erro interno do servidor."}
    }
)
async def analyze_model(file: UploadFile = File(...)):
    upload_dir = "temp_uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, file.filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        analysis_result = analyze_file(file_path)

        if "error" in analysis_result:
            logger.warning(f"Erro na análise de arquivo: {analysis_result['error']}")
            raise HTTPException(status_code=400, detail=analysis_result["error"])
            
        return JSONResponse(content=analysis_result, status_code=200)

    except HTTPException:
        raise

    except FileNotFoundError as e:
        logger.error(f"Erro de arquivo não encontrado inesperado: {e}")
        raise HTTPException(status_code=404, detail=f"Arquivo não encontrado no servidor: {e}")

    except Exception as e:
        logger.exception(f"Ocorreu um erro interno inesperado no servidor: {e}")
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro interno no servidor: {e}")
    finally:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError as e:
                logger.error(f"Erro ao remover arquivo temporário {file_path}: {e}")