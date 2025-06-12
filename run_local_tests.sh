#!/bin/bash

# Ajuste o caminho 'venv/Scripts/activate' ou 'venv/bin/activate' conforme seu sistema
source venv/Scripts/activate

echo "--- Rodando testes Pytest e gerando relatório JUnit XML e Cobertura ---"
pytest --cov=printqa --junitxml="junit-report.xml" "./tests"

if [ $? -ne 0 ]; then
    echo "ERRO: Os testes Pytest falharam. Não será enviado para o TestRail."
    deactivate
    exit 1
fi

echo "--- Enviando resultados para o TestRail via TRCLI ---"
python scripts/run_trcli_local.py

if [ $? -ne 0 ]; then
    echo "ERRO: O envio para o TestRail falhou."
    deactivate
    exit 1
fi

echo "--- Processo concluído com sucesso ---"

# Desativa o ambiente virtual
deactivate