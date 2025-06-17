import os
import pytest
from unittest.mock import patch, call

pytestmark = pytest.mark.unit

def test_version_import():
    """Testa se a variável __version__ pode ser importada corretamente."""
    from printqa import __version__
    assert __version__ == "1.0.0"

# --- Testes para a função check_config() ---

def test_check_config_all_present(monkeypatch, capsys):
    """
    Testa check_config() quando todas as variáveis de ambiente (incluindo opcionais)
    estão presentes. Deve retornar True e imprimir status "Definida".
    """
    from printqa import check_config

    with monkeypatch.context() as m:
        m.setenv('DATABASE_URL', 'mysql://user:pass@localhost/db_test')
        m.setenv('TESTRAIL_URL', 'https://testrail.example.com')
        m.setenv('TESTRAIL_USER', 'test@example.com')
        m.setenv('TESTRAIL_KEY', 'mysecretkey')
        
        result = check_config()
        
        assert result is True
        
        captured = capsys.readouterr()
        stdout_lines = captured.out.splitlines()

        # ASSERÇÃO AJUSTADA PARA A URL TRUNCADA CORRETA
        assert "--- Verificação de Configuração do Ambiente PrintQA ---" in stdout_lines
        assert "✓ (Definida)    DATABASE_URL: mysql://user:pass@localhost/db..." in stdout_lines # CORRIGIDO
        assert "✓ (Definida)    TESTRAIL_URL: https://testrail.example.com" in stdout_lines
        assert "✓ (Definida)    TESTRAIL_USER: test@example.com" in stdout_lines
        assert "✓ (Definida)    TESTRAIL_KEY: ********" in stdout_lines
        assert "Configuração de banco de dados parece OK." in stdout_lines
        
        testrail_key_line = [line for line in stdout_lines if "TESTRAIL_KEY" in line][0]
        assert "********" in testrail_key_line


def test_check_config_database_url_missing(monkeypatch, capsys):
    """
    Testa check_config() quando DATABASE_URL está faltando.
    Deve retornar False e imprimir status "Crítico" e mensagem de erro.
    """
    from printqa import check_config

    with monkeypatch.context() as m:
        m.delenv('DATABASE_URL', raising=False)
        m.setenv('TESTRAIL_URL', 'https://testrail.example.com')
        m.setenv('TESTRAIL_USER', 'test@example.com')
        m.setenv('TESTRAIL_KEY', 'mysecretkey')
        
        result = check_config()
        
        assert result is False
        
        captured = capsys.readouterr()
        stdout_lines = captured.out.splitlines()

        assert "--- Verificação de Configuração do Ambiente PrintQA ---" in stdout_lines
        assert "✗ (Crítico)     DATABASE_URL: None" in stdout_lines
        assert "✓ (Definida)    TESTRAIL_URL: https://testrail.example.com" in stdout_lines
        assert "ERRO: DATABASE_URL não está configurada. A aplicação não conseguirá se conectar ao banco." in stdout_lines


def test_check_config_optional_missing(monkeypatch, capsys):
    """
    Testa check_config() quando variáveis opcionais (TESTRAIL_*) estão faltando.
    Deve retornar True e imprimir status "Opcional, não definida".
    """
    from printqa import check_config

    with monkeypatch.context() as m:
        m.setenv('DATABASE_URL', 'mysql://user:pass@localhost/db_ok')
        m.delenv('TESTRAIL_URL', raising=False)
        m.delenv('TESTRAIL_USER', raising=False)
        m.delenv('TESTRAIL_KEY', raising=False)
        
        result = check_config()
        
        assert result is True
        
        captured = capsys.readouterr()
        stdout_lines = captured.out.splitlines()

        # ASSERÇÃO AJUSTADA PARA A URL TRUNCADA CORRETA
        assert "--- Verificação de Configuração do Ambiente PrintQA ---" in stdout_lines
        assert "✓ (Definida)    DATABASE_URL: mysql://user:pass@localhost/db..." in stdout_lines # CORRIGIDO
        assert "○ (Opcional, não definida) TESTRAIL_URL: None" in stdout_lines
        assert "○ (Opcional, não definida) TESTRAIL_USER: None" in stdout_lines
        assert "○ (Opcional, não definida) TESTRAIL_KEY: None" in stdout_lines
        assert "Configuração de banco de dados parece OK." in stdout_lines


def test_check_config_database_url_truncated(monkeypatch, capsys):
    """
    Testa se a DATABASE_URL é truncada na saída do print.
    """
    from printqa import check_config
    long_db_url = "mysql+mysqlconnector://user:password@long.hostname.example.com:3306/very_long_database_name"
    
    with monkeypatch.context() as m:
        m.setenv('DATABASE_URL', long_db_url)
        
        check_config()
        
        captured = capsys.readouterr()
        stdout_lines = captured.out.splitlines()

        db_url_line = [line for line in stdout_lines if "DATABASE_URL" in line][0]
        # Esta asserção já estava correta em seu código anterior
        assert "mysql+mysqlconnector://user:pa..." in db_url_line 
        assert len(db_url_line) < len(long_db_url) + 50 # Garante que foi truncado