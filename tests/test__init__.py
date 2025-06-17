# tests/test__init__.py

import os
import pytest
from unittest.mock import patch

pytestmark = pytest.mark.unit

def test_check_config_with_database_url():
    """Testa a verificação de configuração quando DATABASE_URL está presente."""
    from printqa import check_config
    with patch.dict(os.environ, {'DATABASE_URL': 'mysql://user:pass@localhost/db'}):
        with patch('dotenv.load_dotenv'): 
            
            with patch('builtins.print'):
                assert check_config() is True

def test_version_import():
    """Testa se a variável __version__ pode ser importada corretamente."""
    from printqa import __version__
    assert __version__ == "1.0.0"