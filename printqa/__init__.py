# printqa/__init__.py
"""
PrintQA - Sistema de análise de qualidade para arquivos 3D
Este arquivo define a versão do pacote e fornece utilitários de diagnóstico.
"""

__version__ = "1.0.0"

def check_config():
    """
    Verifica se as configurações de ambiente essenciais estão presentes.

    Útil para diagnóstico rápido do ambiente de desenvolvimento antes de rodar a aplicação.
    """
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    config_items = {
        'DATABASE_URL': os.getenv('DATABASE_URL'),
        'TESTRAIL_URL': os.getenv('TESTRAIL_URL'),
        'TESTRAIL_USER': os.getenv('TESTRAIL_USER'),
        'TESTRAIL_KEY': os.getenv('TESTRAIL_KEY'),
    }
    
    print("--- Verificação de Configuração do Ambiente PrintQA ---")
    is_db_ok = True
    
    for key, value in config_items.items():
        if key == 'DATABASE_URL' and not value:
            status = "✗ (Crítico)"
            is_db_ok = False
        elif value:
            status = "✓ (Definida)"
        else:
            status = "○ (Opcional, não definida)"

        display_value = value
        if key == 'DATABASE_URL' and value:
            display_value = str(value)[:30] + "..."
        elif key == 'TESTRAIL_KEY' and value:
            display_value = '********'
        
        print(f"{status: <15} {key}")

    print("-----------------------------------------------------")
    if not is_db_ok:
        print("ERRO: DATABASE_URL não está configurada. A aplicação não conseguirá se conectar ao banco.")
    else:
        print("Configuração de banco de dados parece OK.")
        
    return is_db_ok