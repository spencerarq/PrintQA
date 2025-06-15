#!/usr/bin/env python3
"""
Script completo para resolver problemas de envio ao TestRail
Inclui validação, configuração automática e fallbacks
"""

import os
import subprocess
import sys
import datetime
import json
from pathlib import Path
from dotenv import load_dotenv

class TestRailConfig:
    """Classe para gerenciar configurações do TestRail"""
    
    def __init__(self):
        self.config_file = Path('.testrail_config.json')
        self.env_file = Path('.env')
        self.env_var_names = ['TESTRAIL_URL', 'TESTRAIL_USER', 'TESTRAIL_KEY']
        self.placeholders = {
            'TESTRAIL_URL': 'https://sua-empresa.testrail.io',
            'TESTRAIL_USER': 'seu-email@empresa.com',
            'TESTRAIL_KEY': 'sua-chave-api-aqui'
        }

    def prepare_env_file(self):
        """
        Garante que o arquivo .env exista.
        Se não existir, cria-o usando variáveis de ambiente do SO, se disponíveis,
        caso contrário, usa placeholders e indica a necessidade de configuração manual.
        Retorna um dict: {'created': bool, 'needs_manual_config': bool}
        """
        if not self.env_file.exists():
            env_values_from_os = {var: os.getenv(var) for var in self.env_var_names}
            all_required_vars_found_in_os_env = all(env_values_from_os.values())

            lines = ["# Configurações do TestRail"]
            for var_name in self.env_var_names:
                value = env_values_from_os[var_name]
                if value:
                    lines.append(f"{var_name}={value}")
                else:
                    lines.append(f"{var_name}={self.placeholders[var_name]}")
            
            if not all_required_vars_found_in_os_env:
                lines.append("\n# Exemplo de formato (se precisar editar/completar manualmente):")
                lines.append(f"# {self.env_var_names[0]}={self.placeholders[self.env_var_names[0]]}")
                lines.append(f"# {self.env_var_names[1]}={self.placeholders[self.env_var_names[1]]}")
                lines.append(f"# {self.env_var_names[2]}={self.placeholders[self.env_var_names[2]]}")

            try:
                with open(self.env_file, 'w', encoding='utf-8') as f:
                    f.write("\n".join(lines) + "\n")
                
                if all_required_vars_found_in_os_env:
                    # Se todas as variáveis foram encontradas no SO, o .env foi criado silenciosamente.
                    pass
                else:
                    print(f"Arquivo .env criado em: {self.env_file.absolute()}")
                    print(f"  -> ATENÇÃO: O arquivo contém exemplos. Verifique e complete o .env se necessário.")
                
                return {
                    'created': True, 
                    'needs_manual_config': not all_required_vars_found_in_os_env
                }
            except IOError as e:
                print(f"ERRO: Não foi possível criar o arquivo .env em {self.env_file.absolute()}: {e}")
                return {'created': False, 'needs_manual_config': True}
        return {'created': False, 'needs_manual_config': False}
    
    def validate_env_vars(self):
        """Valida se as variáveis de ambiente estão definidas"""
        load_dotenv(self.env_file)
        
        required_vars = {
            'TESTRAIL_URL': 'URL do TestRail (ex: https://empresa.testrail.io)',
            'TESTRAIL_USER': 'Email do usuário do TestRail',
            'TESTRAIL_KEY': 'Chave da API do TestRail'
        }
        
        missing_vars = []
        invalid_vars = []
        
        for var, description in required_vars.items():
            value = os.getenv(var)
            if not value:
                missing_vars.append(f"  {var}: {description}")
            elif var == 'TESTRAIL_URL' and not value.startswith('https://'):
                invalid_vars.append(f"  {var}: Deve começar com https://")
            elif var == 'TESTRAIL_USER' and '@' not in value:
                invalid_vars.append(f"  {var}: Deve ser um email válido")
            elif var == 'TESTRAIL_KEY' and len(value) < 10:
                invalid_vars.append(f"  {var}: Parece muito curta")
        
        if missing_vars or invalid_vars:
            print("ERRO: Problemas com as variáveis do TestRail:")
            print()
            
            if missing_vars:
                print("Variáveis ausentes:")
                print('\n'.join(missing_vars))
                print()
            
            if invalid_vars:
                print("Variáveis com problemas:")
                print('\n'.join(invalid_vars))
                print()
            
            print(f"Edite o arquivo: {self.env_file.absolute()}")
            print("Ou defina as variáveis no seu sistema operacional")
            return False
        # A ausência de erro indica que as variáveis estão configuradas.
        return True
    
    def get_testrail_credentials(self):
        """Obtém credenciais do TestRail de várias fontes"""
        load_dotenv(self.env_file)
        
        url = os.getenv('TESTRAIL_URL')
        user = os.getenv('TESTRAIL_USER') 
        key = os.getenv('TESTRAIL_KEY')
        
        if all([url, user, key]):
            return url, user, key
        
        # Tentar carregar de arquivo de configuração JSON
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    return config.get('url'), config.get('user'), config.get('key')
            except:
                pass
        
        return None, None, None

def check_trcli_installation():
    """Verifica se o TRCLI está instalado"""
    try:
        result = subprocess.run(['trcli', '--version'], 
                              capture_output=True, text=True, timeout=10)
        # A ausência de erro indica que o TRCLI foi encontrado.
        return True
    except FileNotFoundError:
        print("TRCLI não encontrado!")
        print("Instale com: pip install trcli")
        print("Mais info: https://github.com/gurock/trcli")
        return False
    except subprocess.TimeoutExpired:
        print("TRCLI instalado mas não responde")
        return False

def find_junit_files():
    """Encontra arquivos JUnit XML nos diretórios relevantes."""
    # Lista priorizada de caminhos/nomes de arquivos específicos a serem verificados.
    # O primeiro corresponde ao local de saída do script run_local_tests.sh.
    specific_files_to_check = [
        Path('reports/junit-report.xml'),
        Path('junit-report.xml'),
        Path('test-results.xml'),
        Path('pytest-results.xml'),
    ]
    
    found_files = []
    
    # 1. Verificar caminhos de arquivos específicos e conhecidos
    for file_path_obj in specific_files_to_check:
        if file_path_obj.exists() and file_path_obj.is_file():
            resolved_path_str = str(file_path_obj.resolve())
            # Evitar adicionar o mesmo arquivo várias vezes se caminhos diferentes apontarem para ele
            if resolved_path_str not in [str(Path(f).resolve()) for f in found_files]: # type: ignore
                found_files.append(str(file_path_obj)) # Armazenar o caminho como string
    
    # 2. Se nenhum arquivo específico for encontrado, procurar por *.xml no diretório atual e em ./reports
    if not found_files:
        search_dirs_for_glob = [Path('.'), Path('reports')]
        for s_dir in search_dirs_for_glob:
            if s_dir.exists() and s_dir.is_dir():
                for xml_file_path in s_dir.glob('*.xml'):
                    if xml_file_path.is_file(): # Garantir que é um arquivo
                        try:
                            with open(xml_file_path, 'r', encoding='utf-8') as f:
                                content = f.read(500)  # Ler apenas o início
                                if 'testsuite' in content.lower() or 'testcase' in content.lower():
                                    resolved_path_str = str(xml_file_path.resolve())
                                    if resolved_path_str not in [str(Path(f).resolve()) for f in found_files]: # type: ignore
                                        found_files.append(str(xml_file_path))
                        except Exception:  # Ser tolerante a erros de leitura ou codificação
                            pass
    
    return found_files

def execute_trcli_with_validation(junit_file, url, user, key, project="PrintQA"):
    """Executa TRCLI com validação completa"""
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    title = f"Pytest Run - {timestamp}"
    
    command = [
        "trcli",
        "-y",
        "-h", url,
        "--project", project,
        "--username", user,
        "--password", key,
        "parse_junit",
        "--title", title,
        "-f", junit_file
    ]
    
    file_name_to_log = Path(junit_file).name
    print(f"-> Enviando '{file_name_to_log}' para o TestRail...")
    
    try:
        result = subprocess.run(
            command,
            check=False, # Verifica o returncode manualmente para controlar a saída
            capture_output=True,
            text=True,
            timeout=300
        )
        
        if result.returncode == 0:
            print(f"   Envio de '{file_name_to_log}' bem-sucedido.")
            if result.stderr: # Imprime stderr mesmo em sucesso, pois pode conter avisos
                print("   Avisos do TRCLI:")
                print(result.stderr.strip())
            return True
        else:
            print(f"   Falha no envio de '{file_name_to_log}' (TRCLI código {result.returncode}). Detalhes:")
            if result.stdout:
                print("   Saída padrão do TRCLI:")
                print(result.stdout.strip())
            if result.stderr:
                print("   Saída de erro do TRCLI:")
                print(result.stderr.strip())
            return False
        
    except subprocess.CalledProcessError as e:
        # Este bloco pode não ser alcançado se check=False, mas mantido por segurança
        print(f"   Erro inesperado ao executar TRCLI para '{file_name_to_log}' (código {e.returncode}).")
        if e.stdout: print(f"   Saída padrão: {e.stdout.strip()}")
        if e.stderr: print(f"   Saída de erro: {e.stderr.strip()}")
        return False
        
    except subprocess.TimeoutExpired:
        print(f"   Falha no envio de '{file_name_to_log}': TRCLI expirou após 5 minutos.")
        return False

def main():
    print("=" * 60)
    print("DIAGNÓSTICO E ENVIO PARA TESTRAIL")
    print("=" * 60)
    print()
    
    # 1. Configurar TestRail
    config = TestRailConfig()
    
    # Gerenciar arquivo .env: criar se não existir, usando variáveis de ambiente se possível
    env_status = config.prepare_env_file()
    
    if env_status['needs_manual_config']:
        if env_status['created']:
            print("-" * 60)
            print("AÇÃO NECESSÁRIA: O arquivo .env foi criado mas requer configuração manual.")
            print(f"Por favor, edite o arquivo: {config.env_file.absolute()}")
            print("Preencha os valores de exemplo e execute o script novamente.")
            print("-" * 60)
        else: # Não foi criado (ex: IOError) ou já existia e precisa de config.
            if not config.env_file.exists(): # Confirma se realmente não pôde ser criado
                print("-" * 60)
                print("ERRO: Falha ao tentar criar o arquivo .env.")
                print("Verifique as permissões de escrita no diretório ou crie o .env manualmente com as credenciais.")
                print("Se as variáveis de ambiente TESTRAIL_URL/USER/KEY estiverem definidas, elas serão usadas.")
                print("-" * 60)
        return 1
        
    # Validar variáveis de ambiente
    if not config.validate_env_vars():
        return 1
    
    # 2. Verificar TRCLI
    if not check_trcli_installation():
        return 1
    
    # 3. Encontrar arquivos JUnit
    junit_files = find_junit_files()
    
    if not junit_files:
        print("ERRO: Nenhum arquivo JUnit XML encontrado!")
        print("      Execute seus testes primeiro para gerar o arquivo XML.")
        print("      Exemplo: pytest --junitxml=reports/junit-report.xml")
        return 1
    
    print(f"Encontrados {len(junit_files)} arquivo(s) JUnit XML para processar.")
    
    # 4. Obter credenciais
    url, user, key = config.get_testrail_credentials()
    
    # Adicionar verificação explícita para garantir que todas as credenciais foram obtidas
    if not all([url, user, key]):
        print("ERRO CRÍTICO: Não foi possível obter as credenciais completas do TestRail (URL, Usuário e/ou Chave).")
        print("Isso pode ocorrer se o arquivo .env estiver presente, mas uma ou mais variáveis essenciais estiverem vazias,")
        print("ou se o fallback para o arquivo .testrail_config.json (se existir) não forneceu todas as informações.")
        print("Por favor, verifique suas configurações no arquivo .env e/ou .testrail_config.json.")
        print("O envio para o TestRail será pulado devido à ausência de credenciais completas.")
        return 1
    
    # 5. Executar TRCLI para cada arquivo
    success_count = 0
    for junit_file in junit_files:
        if execute_trcli_with_validation(junit_file, url, user, key):
            success_count += 1
    
    # 6. Resultado final
    print("=" * 60)
    print("Resumo do Envio para TestRail:")
    if success_count == len(junit_files):
        if len(junit_files) > 0:
            print(f"  SUCESSO: {success_count}/{len(junit_files)} arquivo(s) enviado(s).")
        else: # Caso não haja arquivos, mas o script chegou até aqui (improvável com as checagens)
            print("  Nenhum arquivo JUnit foi processado.")
    else:
        print(f"  ATENÇÃO: {success_count}/{len(junit_files)} arquivo(s) enviado(s). {len(junit_files) - success_count} falha(s).")
        print("           Verifique os detalhes acima para os arquivos que falharam.")
    print("=" * 60)
    
    return 0 if success_count == len(junit_files) and len(junit_files) > 0 else 1

if __name__ == "__main__":
    sys.exit(main())