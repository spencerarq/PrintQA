# Dockerfile 

# --- Estágio 1: Builder ---
# Cria um ambiente temporário para instalar as dependências de forma limpa
FROM python:3.12-slim-bookworm AS builder
WORKDIR /app

# Instala pacotes do sistema necessários para compilar algumas dependências Python
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Cria e ativa um ambiente virtual dentro da imagem, uma excelente prática
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copia e instala as dependências de forma otimizada para o cache do Docker
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# --- Estágio 2: Imagem Final de Produção ---
# Inicia com uma imagem Python limpa e leve
FROM python:3.12-slim-bookworm
WORKDIR /app

# Cria um usuário não-root 'app' por motivos de segurança
RUN groupadd --gid 1001 app && \
    useradd --uid 1001 --gid 1001 --create-home --shell /bin/bash app

# --- LINHA DE CORREÇÃO ADICIONADA AQUI ---
# Dá ao usuário 'app' a propriedade do diretório de trabalho /app.
# Isso corrige o erro de 'Permission Denied' ao tentar criar a pasta 'temp_uploads'.
RUN chown -R app:app /app

# Copia o ambiente virtual com as dependências já instaladas do estágio 'builder'
COPY --from=builder /opt/venv /opt/venv

# Copia os arquivos da aplicação, já definindo o usuário 'app' como proprietário
COPY --chown=app:app ./printqa ./printqa
COPY --chown=app:app ./app ./app

# Garante que os scripts sejam executáveis
RUN chmod +x ./app/*.sh 2>/dev/null || true

# Alterna para o usuário não-root para executar a aplicação
USER app

# Adiciona o ambiente virtual ao PATH do sistema
ENV PATH="/opt/venv/bin:$PATH"
EXPOSE 8000

# Comando que inicia o servidor da API
CMD ["uvicorn", "printqa.main:app", "--host", "0.0.0.0", "--port", "8000"]