# Dockerfile

# --- Estágio 1: Builder ---
FROM python:3.12-slim-bookworm AS builder
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# --- Estágio 2: Imagem Final de Produção ---
FROM python:3.12-slim-bookworm
WORKDIR /app

RUN groupadd --gid 1001 app && \
    useradd --uid 1001 --gid 1001 --create-home --shell /bin/bash app

RUN chown -R app:app /app


COPY --from=builder /opt/venv /opt/venv

COPY --chown=app:app ./printqa ./printqa
COPY --chown=app:app ./app ./app
COPY --chown=app:app ./alembic.ini .
COPY --chown=app:app ./alembic ./alembic

RUN chmod +x ./app/*.sh 2>/dev/null || true

ENV PATH="/opt/venv/bin:$PATH"
USER app
EXPOSE 8000

CMD ["uvicorn", "printqa.main:app", "--host", "0.0.0.0", "--port", "8000"]
