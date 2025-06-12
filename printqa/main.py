# printqa/main.py
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from .analysis import analyze_file # Importa sua função de análise
import shutil
import os
import logging # Para logging, útil em produção

# Configura o logger (opcional, mas boa prática)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializa a aplicação FastAPI
app = FastAPI(
    title="PrintQA Backend API",
    description="API para análise de qualidade de modelos 3D para impressão.",
    version="0.1.0"
)

# Endpoint de teste básico
@app.get("/")
async def read_root():
    return {"message": "Bem-vindo à API PrintQA! Acesse /docs para a documentação."}

# Endpoint para análise de arquivo STL
# Recebe um arquivo UploadFile que representa o modelo 3D
@app.post("/analyze_model/")
async def analyze_model(file: UploadFile = File(...)):
    """
    Recebe um arquivo de modelo 3D (ex: STL) e retorna um relatório de análise de qualidade.
    """
    upload_dir = "temp_uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, file.filename)
    
    try:
        # 1. Salvar o arquivo temporariamente
        # file.file é um SpooledTemporaryFile, shutil.copyfileobj é eficiente para ele
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 2. Chamar sua função de análise
        analysis_result = analyze_file(file_path) # analyze_file AGORA SEMPRE RETORNA DICIONÁRIO

        # 3. Lidar com erros de análise retornados pela sua função analyze_file
        # Se analysis_file retorna {"error": ...}, levante uma HTTPException 400 aqui
        if "error" in analysis_result:
            logger.warning(f"Erro na análise de arquivo: {analysis_result['error']}")
            raise HTTPException(status_code=400, detail=analysis_result["error"])
            
        # 4. Retornar os resultados da análise (se não houve erro)
        return JSONResponse(content=analysis_result, status_code=200)

    except HTTPException: # Captura HTTPExceptions já levantadas (como a de 400 acima)
        raise # Re-levanta a HTTPException original para o FastAPI lidar

    except FileNotFoundError as e:
        # Embora analyze_file já trate isso, é bom ter aqui para outros FileNotFoundError
        logger.error(f"Erro de arquivo não encontrado inesperado: {e}")
        raise HTTPException(status_code=404, detail=f"Arquivo não encontrado no servidor: {e}")

    except Exception as e:
        # Esta é a sua 'rede de segurança' para qualquer outra exceção inesperada
        # que possa ocorrer durante o upload ou o processo de análise ANTES de analyze_file,
        # ou se analyze_file levantar algo que não retorne um dicionário 'error'.
        logger.exception(f"Ocorreu um erro interno inesperado no servidor: {e}")
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro interno no servidor: {e}")
    finally:
        # 5. Limpar o arquivo temporário
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError as e:
                logger.error(f"Erro ao remover arquivo temporário {file_path}: {e}")