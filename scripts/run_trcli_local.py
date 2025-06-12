# run_trcli_local.py
import os
import subprocess
import sys
from dotenv import load_dotenv
import datetime
# Carrega as variáveis do arquivo .env na raiz do projeto
load_dotenv()

# Monta o comando trcli usando as variáveis de ambiente
# Lembre-se que trcli espera TESTRAIL_HOST, TESTRAIL_USERNAME, TESTRAIL_PASSWORD (ou TESTRAIL_API_KEY)
trcli_command = [
    "trcli",
    "-y",
    "-h", os.getenv("TESTRAIL_URL"), # TESTRAIL_URL do .env mapeado para -h
    "--project", "PrintQA", # Ou os.getenv("TESTRAIL_PROJECT_NAME") se tiver no .env
    "--username", os.getenv("TESTRAIL_USER"),
    "--password", os.getenv("TESTRAIL_KEY"), # Ou TESTRAIL_API_KEY se usar
    "parse_junit",
    "--title", f"Pytest Run - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}",
    "-f", "junit-report.xml"
    ]

# Adicione a lógica para usar TESTRAIL_PROJECT_ID/SUITE_ID se necessário,
# embora o trcli não os aceite diretamente na linha de comando para parse_junit.
# Ele usará o nome do projeto.

# Exibe o comando que será executado (para depuração)
print(f"Executando TRCLI: {' '.join(trcli_command)}")

# Executa o comando trcli como um subprocesso
try:
    # Use subprocess.run para executar o comando e capturar a saída
    result = subprocess.run(trcli_command, check=True, capture_output=True, text=True, shell=True)
    print("Saída do TRCLI:")
    print(result.stdout)
    if result.stderr:
        print("Erros do TRCLI:")
        print(result.stderr)
    print("TRCLI executado com sucesso.")
except subprocess.CalledProcessError as e:
    print(f"Erro ao executar TRCLI: {e}", file=sys.stderr)
    print(f"STDOUT: {e.stdout}", file=sys.stderr)
    print(f"STDERR: {e.stderr}", file=sys.stderr)
    sys.exit(e.returncode)
except FileNotFoundError:
    print("Erro: 'trcli' não encontrado. Certifique-se de que está instalado e no PATH do seu ambiente virtual.", file=sys.stderr)
    sys.exit(1)