# run_trcli_local.py
import os
import subprocess
import sys
from dotenv import load_dotenv
import datetime
# Carrega as variáveis do arquivo .env na raiz do projeto
load_dotenv()

# Comando TRCLI
trcli_command = [
    "trcli",
    "-y",
    "-h", os.getenv("TESTRAIL_URL"), 
    "--project", "PrintQA", # Ou os.getenv("TESTRAIL_PROJECT_NAME") se tiver no .env
    "--username", os.getenv("TESTRAIL_USER"),
    "--password", os.getenv("TESTRAIL_KEY"), 
    "parse_junit",
    "--title", f"Pytest Run - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}",
    "-f", "junit-report.xml"
    ]



# Exibe o comando que será executado (para depuração)
print(f"Executando TRCLI: {' '.join(trcli_command)}")

# Executa o comando trcli como um subprocesso
try:
    
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