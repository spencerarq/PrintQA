#!/bin/bash

set -e

echo "--- Verificando variáveis de ambiente... ---"
if [ -z "$DATABASE_URL" ]; then
    echo "ERRO: DATABASE_URL não foi definida. Verifique seu arquivo .env."
    exit 1
fi

echo "--- Aguardando o banco de dados ficar disponível... ---"

timeout=30
counter=0
while [ $counter -lt $timeout ]; do
    if python -c "
import mysql.connector, os, sys
from urllib.parse import urlparse
try:
    url = urlparse(os.environ['DATABASE_URL'])
    conn = mysql.connector.connect(
        host=url.hostname, port=url.port, user=url.username, 
        password=url.password, database=url.path[1:], connection_timeout=5
    )
    conn.close()
    sys.exit(0)
except Exception:
    sys.exit(1)
"; then
        echo "✓ Banco de dados está disponível!"
        break
    fi
    counter=$((counter + 1))
    echo "Tentativa $counter/$timeout - Aguardando banco..."
    sleep 2
done
if [ $counter -eq $timeout ]; then
    echo "ERRO: Timeout ao conectar com o banco de dados."
    exit 1
fi

echo "--- Rodando migrations Alembic no banco de teste... ---"
alembic upgrade head

echo "--- Rodando a suíte de testes e gerando relatórios... ---"

pytest --junitxml="./reports/junit-report.xml"

echo "--- Executando script de reporte para o TestRail... ---"

python scripts/testrail_reporter.py --file reports/junit-report.xml

echo ""
echo "--- Processo de teste concluído com sucesso! ---"