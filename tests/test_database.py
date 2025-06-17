# Em tests/test_database.py

from sqlalchemy.orm import Session
from sqlalchemy import text

def test_database_connection(db_session: Session):
    """
    Testa se a conexão com o banco de dados pode ser estabelecida e
    se uma consulta simples pode ser executada.
    A própria injeção da fixture 'db_session' já testa parte da conexão.
    Este teste adiciona uma verificação explícita com uma query.
    """
    assert db_session is not None
    
    result = db_session.execute(text("SELECT 1"))
    
    assert result.scalar() == 1