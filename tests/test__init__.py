# tests/test_init.py
import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

def load_env_variables():
    """Carrega variáveis de ambiente do arquivo .env"""
    try:
        from dotenv import load_dotenv
        project_root = Path(__file__).parent.parent
        env_path = project_root / ".env"
        load_dotenv(env_path)
        return True
    except ImportError:
        project_root = Path(__file__).parent.parent
        env_file = project_root / ".env"
        if env_file.exists():
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key.strip()] = value.strip().strip('"\'')
            return True
        return False

load_env_variables()

def test_init_database_success():
    """Testa inicialização bem-sucedida do banco."""
    from printqa import init_database
    
    with patch('printqa.database.create_tables') as mock_create_tables:
        with patch('builtins.print') as mock_print:
            mock_create_tables.return_value = None
            
            result = init_database()
            
            assert result is True
            mock_create_tables.assert_called_once()
            mock_print.assert_called_with("✓ Tabelas do banco de dados criadas com sucesso")

def test_init_database_failure():
    """Testa falha na inicialização do banco."""
    from printqa import init_database
    
    with patch('printqa.database.create_tables') as mock_create_tables:
        with patch('builtins.print') as mock_print:
            mock_create_tables.side_effect = Exception("Erro de conexão")
            
            result = init_database()
            
            assert result is False
            mock_create_tables.assert_called_once()
            mock_print.assert_called_with("✗ Erro ao criar tabelas: Erro de conexão")

def test_check_config_with_all_vars():
    """Testa verificação de configuração com todas as variáveis."""
    from printqa import check_config
    
    # Mock das variáveis de ambiente
    env_vars = {
        'DATABASE_URL': 'mysql://user:pass@localhost/db_muito_longa_para_testar_o_truncamento_da_string_de_exibicao',
        'TESTRAIL_URL': 'https://test.testrail.io',
        'TESTRAIL_USER': 'user@test.com',
        'TESTRAIL_KEY': 'key123',
        'TESTRAIL_PROJECT_ID': '1',
        'TESTRAIL_SUITE_ID': '2',
        'TESTRAIL_RUN_ID': '3'
    }
    
    with patch.dict(os.environ, env_vars):
        with patch('builtins.print') as mock_print:
            with patch('dotenv.load_dotenv'):
                result = check_config()
                
                assert result is True
                
                assert mock_print.call_count >= 8 

def test_check_config_missing_database_url():
    """Testa verificação com DATABASE_URL ausente."""
    from printqa import check_config
    
    # Mock sem DATABASE_URL
    env_vars = {
        'TESTRAIL_URL': 'https://test.testrail.io',
        'TESTRAIL_USER': 'user@test.com',
        'TESTRAIL_KEY': 'key123',
        'TESTRAIL_PROJECT_ID': '1',
        'TESTRAIL_SUITE_ID': '2',
        'TESTRAIL_RUN_ID': '3'
    }
    
    with patch.dict(os.environ, env_vars, clear=True):
        with patch('builtins.print') as mock_print:
            with patch('dotenv.load_dotenv'):
                result = check_config()
                
                assert result is False

def test_check_config_partial_vars():
    """Testa verificação com variáveis parciais."""
    from printqa import check_config
    
    # Mock com apenas DATABASE_URL
    env_vars = {
        'DATABASE_URL': 'mysql://user:pass@localhost/db'
    }
    
    with patch.dict(os.environ, env_vars, clear=True):
        with patch('builtins.print') as mock_print:
            with patch('dotenv.load_dotenv'):
                result = check_config()
                
                assert result is True
                
                calls = [str(call) for call in mock_print.call_args_list]
                database_call = next((call for call in calls if 'DATABASE_URL' in call), None)
                assert database_call is not None
                assert '✓' in database_call

def test_version_import():
    """Testa se a versão pode ser importada."""
    from printqa import __version__
    assert __version__ == "1.0.0"