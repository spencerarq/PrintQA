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

RUN addgroup --system app && adduser --system --group app

COPY --from=builder /opt/venv /opt/venv

COPY --chown=app:app ./printqa ./printqa

USER app

ENV PATH="/opt/venv/bin:$PATH"
EXPOSE 8000

CMD ["uvicorn", "printqa.main:app", "--host", "0.0.0.0", "--port", "8000"]