# Dockerfile - Versão refatorada

# --- Estágio 1: Builder ---
FROM python:3.12-slim-bookworm AS builder
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip --root-user-action=ignore && \
    pip install --no-cache-dir -r requirements.txt --root-user-action=ignore

# --- Estágio 2: Imagem Final de Produção ---
FROM python:3.12-slim-bookworm
WORKDIR /app

# Criar usuário com UID/GID consistentes
RUN groupadd --gid 1001 app && \
    useradd --uid 1001 --gid 1001 --create-home --shell /bin/bash app

COPY --from=builder /opt/venv /opt/venv

# Copiar todos os arquivos da aplicação
COPY --chown=app:app ./printqa ./printqa
COPY --chown=app:app ./app ./app

# Dar permissões de execução aos scripts
RUN chmod +x ./app/*.sh 2>/dev/null || true

USER app

ENV PATH="/opt/venv/bin:$PATH"
EXPOSE 8000

CMD ["uvicorn", "printqa.main:app", "--host", "0.0.0.0", "--port", "8000"]