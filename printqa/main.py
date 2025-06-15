# printqa/main.py
from fastapi import FastAPI, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Annotated
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

# --- Constantes de validação ---
MAX_FILE_SIZE_MB = 20  
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024  

ALLOWED_MIME_TYPES = [
    "application/octet-stream",
    "model/stl",
    "text/plain",
]

@app.post(
    "/analyze_model/",
    response_model=AnalysisResult,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ErrorResponse, "description": "Erro de requisição inválida ou arquivo não processável."},
        413: {"model": ErrorResponse, "description": "Arquivo muito grande."},
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: {"model": ErrorResponse, "description": "Tipo de arquivo não suportado."},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse, "description": "Erro interno do servidor."}
    }
)
async def analyze_model(
    file: Annotated[
        UploadFile,
        File(..., description="Arquivo de modelo 3D (e.g., STL) para análise.")
    ]
):
    """ Recebe um arquivo de modelo 3D (e.g., STL) e retorna um relatório de análise de qualidade.
    Realiza validações de MIME Type e Tamanho antes da análise. """
    # --- 1. Validação de MIME Type ---
    if file.content_type not in ALLOWED_MIME_TYPES:
        logger.warning(f"Upload de arquivo com tipo MIME não permitido: {file.content_type}")
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Tipo de arquivo '{file.content_type}' não suportado. Apenas tipos {', '.join(ALLOWED_MIME_TYPES)} são permitidos."
        )

    try:
        file_contents = await file.read()
    except Exception as e:
        logger.debug("Debug: Entrou no bloco de exceção geral do main.py.")
        logger.exception(f"Ocorreu um erro interno inesperado no servidor: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ocorreu um erro interno no servidor: {e}")

    # --- 2. Validação de Tamanho do Arquivo ---
    if len(file_contents) > MAX_FILE_SIZE_BYTES:
        logger.warning(f"Upload de arquivo muito grande: {len(file_contents)} bytes (limite: {MAX_FILE_SIZE_BYTES} bytes)")
        raise HTTPException(
            status_code=413,
            detail=f"Arquivo excede o tamanho máximo permitido de {MAX_FILE_SIZE_MB} MB."
        )

    # --- 3. Salvar o arquivo temporariamente ---
    upload_dir = "temp_uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, file.filename)
    
    try:
        
        with open(file_path, "wb") as buffer:
            buffer.write(file_contents)
        
        analysis_result = analyze_file(file_path)

        if "error" in analysis_result:
            logger.warning(f"Erro na análise de arquivo: {analysis_result['error']}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=analysis_result["error"])
            
        return JSONResponse(content=analysis_result, status_code=status.HTTP_200_OK)

    except HTTPException:
        raise

    except FileNotFoundError as e:
        logger.error(f"Erro de arquivo não encontrado inesperado: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Arquivo não encontrado no servidor: {e}")

    except Exception as e:
        logger.exception(f"Ocorreu um erro interno inesperado no servidor: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ocorreu um erro interno no servidor: {e}")
    finally:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError as e:
                logger.error(f"Erro ao remover arquivo temporário {file_path}: {e}")