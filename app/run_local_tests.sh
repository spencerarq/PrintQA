#!/bin/bash


if [ -z "$DATABASE_URL" ]; then
    echo "ERRO: DATABASE_URL não foi definida nas variáveis de ambiente"
    exit 1
fi

echo "--- Configuração do ambiente ---"

echo "--- Aguardando banco de dados ficar disponível ---"

timeout=30
counter=0
while [ $counter -lt $timeout ]; do
    if python -c "
import mysql.connector
import os
from urllib.parse import urlparse

try:
    url = urlparse(os.environ['DATABASE_URL'])
    connection = mysql.connector.connect(
        host=url.hostname,
        port=url.port,
        user=url.username,
        password=url.password,
        database=url.path[1:]  # Remove the leading '/'
    )
    connection.close()
    print('Banco conectado com sucesso!')
    exit(0)
except Exception as e:
    print(f'Tentativa {counter + 1}: {e}')
    exit(1)
" 2>/dev/null; then
        echo "Banco de dados está disponível!"
        break
    fi
    
    counter=$((counter + 1))
    echo "Tentativa $counter/$timeout - Aguardando banco..."
    sleep 2
done

if [ $counter -eq $timeout ]; then
    echo "ERRO: Timeout ao conectar com o banco de dados"
    exit 1
fi

echo "--- Rodando testes Pytest e gerando relatório JUnit XML e Cobertura ---"
pytest --cov=printqa --junitxml="./reports/junit-report.xml" "./tests"

if [ $? -ne 0 ]; then
    echo "ERRO: Os testes Pytest falharam. Não será enviado para o TestRail."
    exit 1
fi

echo "--- Enviando resultados para o TestRail via TRCLI ---"

# Deixe o script Python run_trcli_local.py lidar com a verificação das variáveis de ambiente
# e a criação/leitura do arquivo .env.
python scripts/run_trcli_local.py

if [ $? -ne 0 ]; then
    echo "AVISO: O envio para o TestRail não foi bem-sucedido (ou foi pulado devido à falta de configuração)."
    echo "Verifique a saída do script run_trcli_local.py acima para mais detalhes e as configurações do TestRail."
else
    echo "--- Script de envio para TestRail executado. Verifique a saída acima para o status do envio. ---"
fi

echo "--- Processo concluído com sucesso ---"
echo "Relatórios salvos em: ./reports/"