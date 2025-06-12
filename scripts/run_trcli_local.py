# run_trcli_local.py
import os
import subprocess
import sys
import datetime 
from dotenv import load_dotenv

load_dotenv()

trcli_command = [
    "trcli",
    "-y",
    "-h", os.getenv("TESTRAIL_URL"),
    "--project", "PrintQA",
    "--username", os.getenv("TESTRAIL_USER"),
    "--password", os.getenv("TESTRAIL_KEY"),
    "parse_junit",
    "--title", f"Pytest Run - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}",
    "-f", "junit-report.xml"
]

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