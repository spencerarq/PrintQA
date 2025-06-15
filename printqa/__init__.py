# printqa/__init__.py
"""
PrintQA - Sistema de análise de qualidade para arquivos 3D
"""

__version__ = "1.0.0"

# Importações controladas para evitar circular imports
def init_database():
    """Inicializa o banco de dados criando as tabelas necessárias."""
    try:
        from .database import create_tables
        create_tables()
        print("✓ Tabelas do banco de dados criadas com sucesso")
        return True
    except Exception as e:
        print(f"✗ Erro ao criar tabelas: {e}")
        return False

# Função utilitária para verificar configuração
def check_config():
    """Verifica se todas as configurações necessárias estão presentes."""
    import os
    from dotenv import load_dotenv
    
    # Carrega .env se disponível
    load_dotenv()
    
    config_items = {
        'DATABASE_URL': os.getenv('DATABASE_URL'),
        'TESTRAIL_URL': os.getenv('TESTRAIL_URL'),
        'TESTRAIL_USER': os.getenv('TESTRAIL_USER'),
        'TESTRAIL_KEY': os.getenv('TESTRAIL_KEY'),
        'TESTRAIL_PROJECT_ID': os.getenv('TESTRAIL_PROJECT_ID'),
        'TESTRAIL_SUITE_ID': os.getenv('TESTRAIL_SUITE_ID'),
        'TESTRAIL_RUN_ID': os.getenv('TESTRAIL_RUN_ID'),
    }
    
    print("=== Configuração do PrintQA ===")
    for key, value in config_items.items():
        status = "✓" if value else "✗"
        display_value = value if key != 'DATABASE_URL' else (value[:30] + "..." if value else None)
        print(f"{status} {key}: {display_value}")
    
    return all(v is not None for v in [config_items['DATABASE_URL']])