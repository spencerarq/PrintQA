# Dockerfile para a aplicação PrintQA FastAPI

# Estágio 1: Base com Python
FROM python:3.11-slim AS builder

# Define o diretório de trabalho
WORKDIR /app

# Variáveis de ambiente para Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instala dependências do sistema se necessário (ex: para compilar algumas libs Python)
# RUN apt-get update && apt-get install -y --no-install-recommends gcc

# Copia o arquivo de dependências e instala
COPY requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt && rm -rf /root/.cache/pip

# Estágio 2: Imagem final
FROM python:3.11-slim

WORKDIR /app

# Copia as wheels pré-compiladas do estágio builder e instala
COPY --from=builder /app/wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels && rm -rf /root/.cache/pip

# Copia o código da aplicação
COPY ./printqa ./printqa

# Expõe a porta que o Uvicorn usará
EXPOSE 8000

# Comando para rodar a aplicação (ajuste o host e porta conforme necessário)
CMD ["uvicorn", "printqa.main:app", "--host", "0.0.0.0", "--port", "8000"]