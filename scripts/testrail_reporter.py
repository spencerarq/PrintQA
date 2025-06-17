# scripts/testrail_reporter.py

import os
import sys
import subprocess
import argparse
from typing import Dict, Any
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

IS_DRY_RUN = os.getenv('TESTRAIL_DRY_RUN', 'false').lower() in ['true', '1', 'yes']

def _get_testrail_credentials() -> Dict[str, Any]:
    """Busca as credenciais do TestRail do ambiente."""
    creds = {
        "url": os.getenv('TESTRAIL_URL'), "user": os.getenv('TESTRAIL_USER'),
        "key": os.getenv('TESTRAIL_KEY'), "project": os.getenv('TESTRAIL_PROJECT', 'PrintQA')
    }
    if not all([creds['url'], creds['user'], creds['key']]):
        print("AVISO: Credenciais do TestRail não configuradas. O envio será pulado.")
        return {}
    return creds

def send_individual_result(analysis_result: dict, test_case_id: int):
    """Envia um resultado de um único caso de teste."""
    creds = _get_testrail_credentials()
    if not creds: return

    is_success = analysis_result.get("is_watertight", False) and not analysis_result.get("has_inverted_faces", True)
    status_id = 1 if is_success else 5
    comment = f"Análise automática: Watertight={analysis_result.get('is_watertight')}, InvertedFaces={analysis_result.get('has_inverted_faces')}"
    
    print(f"--- Reportando para o Test Case C{test_case_id} ---")
    if IS_DRY_RUN:
        print(f"[DRY RUN] Status: {status_id}, Comentário: {comment}")
        return

    try:
        command = ["trcli", "-y", "-h", creds['url'], "--project", creds['project'], "--username", creds['user'], "--password", creds['key'],
                   "add_result", str(test_case_id), "--status-id", str(status_id), "--comment", comment]
        subprocess.run(command, check=True, capture_output=True, text=True, timeout=120)
        print(f"-> Resultado para C{test_case_id} enviado com sucesso!")
    except Exception as e:
        print(f"ERRO ao enviar resultado para C{test_case_id}: {e}")

def send_junit_report(file_path: str):
    """Envia um relatório JUnit XML completo para o TestRail."""
    creds = _get_testrail_credentials()
    if not creds: return

    print(f"--- Enviando relatório JUnit completo: {file_path} ---")
    if IS_DRY_RUN:
        print(f"[DRY RUN] Enviaria o arquivo {file_path} para o projeto {creds['project']}.")
        print("  - Nenhuma chamada real ao TestRail foi feita.")
        return
        
    try:
        title = f"Execução de Testes Automatizados - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        command = ["trcli", "-y", "-h", creds['url'], "--project", creds['project'], "--username", creds['user'], "--password", creds['key'],
                   "parse_junit", "--title", title, "-f", file_path]
        subprocess.run(command, check=True, capture_output=True, text=True, timeout=180)
        print("-> Relatório JUnit enviado com sucesso!")
    except Exception as e:
        print(f"ERRO ao enviar relatório JUnit: {e}")

def main():
    """Função principal que decide o que fazer com base nos argumentos."""
    parser = argparse.ArgumentParser(description="Script de reporte para o TestRail.")
    parser.add_argument('--file', type=str, help="Caminho para o arquivo de relatório JUnit XML a ser enviado.")
    args = parser.parse_args()

    if args.file:
        if not os.path.exists(args.file):
            print(f"ERRO: Arquivo de relatório não encontrado em '{args.file}'")
            sys.exit(1)
        send_junit_report(args.file)
    else:
        print("AVISO: Nenhum arquivo de relatório especificado. O script não fará nada.")
        print("Use --file <caminho_do_relatorio.xml> para enviar um relatório.")

if __name__ == "__main__":
    main()