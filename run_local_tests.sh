#!/bin/bash

# Verifica se o arquivo .env existe
if [ ! -f ".env" ]; then
    echo "ERRO: Arquivo .env não encontrado. Crie um arquivo .env com DATABASE_URL definida."
    exit 1
fi

# Ativa o ambiente virtual
# Ajuste o caminho 'venv/Scripts/activate' ou 'venv/bin/activate' conforme seu sistema
source venv/Scripts/activate

# --- CARREGA AS VARIÁVEIS DO .ENV PARA O AMBIENTE DO SHELL ---
# Isso fará com que DATABASE_URL (e outras do .env) fiquem disponíveis
# para comandos subsequentes do shell (como o pytest).
set -a # Ativa a exportação automática de variáveis para o ambiente
source .env # Carrega o arquivo .env no ambiente atual do shell
set +a # Desativa a exportação automática após carregar

# Verifica se DATABASE_URL foi carregada
if [ -z "$DATABASE_URL" ]; then
    echo "ERRO: DATABASE_URL não foi definida no arquivo .env"
    deactivate
    exit 1
fi

echo "DATABASE_URL carregada: $DATABASE_URL"

# --- Rodando testes Pytest e gerando relatório JUnit XML e Cobertura ---
echo "--- Rodando testes Pytest e gerando relatório JUnit XML e Cobertura ---"
pytest --cov=printqa --junitxml="junit-report.xml" "./tests"

# Verifica se os testes Pytest foram bem-sucedidos antes de tentar enviar para o TestRail
if [ $? -ne 0 ]; then
    echo "ERRO: Os testes Pytest falharam. Não será enviado para o TestRail."
    deactivate
    exit 1
fi

echo "--- Enviando resultados para o TestRail via TRCLI ---"
python scripts/run_trcli_local.py

# Verifica se o TRCLI foi bem-sucedido
if [ $? -ne 0 ]; then
    echo "ERRO: O envio para o TestRail falhou."
    deactivate
    exit 1
fi

echo "--- Processo concluído com sucesso ---"

# Desativa o ambiente virtual
deactivate