# dockerfile

FROM python:3.12-slim-bookworm

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY ./printqa ./printqa

EXPOSE 8000
CMD ["uvicorn", "printqa.main:app", "--host", "0.0.0.0", "--port", "8000"]
