# alembic/env.py

import os
from logging.config import fileConfig

from dotenv import load_dotenv
from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Carrega variáveis de ambiente do .env para Alembic também.
# Certifique-se de que este script seja executado no diretório raiz do projeto
# ou que o caminho para o .env seja ajustado conforme necessário.
load_dotenv()

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Adicione seu objeto MetaData do modelo aqui
# para suporte 'autogenerate'
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata

# Importa a sua Base e modelos
from printqa.database import Base # Importa a Base do seu projeto
from printqa import models # Importa seus modelos para que Base.metadata os conheça
# Nota: A importação de 'models' garante que as classes declarativas
# que definem suas tabelas sejam carregadas e registradas no Base.metadata.

target_metadata = Base.metadata # Define a metadata para o Alembic usar


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Obtenha a DATABASE_URL das variáveis de ambiente
    # Isso garante que o Alembic usa a URL correta (produção/desenvolvimento)
    # que está configurada no seu .env.
    connectable_url = os.getenv("DATABASE_URL")
    if not connectable_url:
        raise ValueError("DATABASE_URL não está definida para o Alembic. Verifique seu arquivo .env")

    connectable = engine_from_config(
        {"sqlalchemy.url": connectable_url}, # Passa a URL diretamente
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()