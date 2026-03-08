import asyncio
import os
from typing import Optional

from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine


_engine: Optional[AsyncEngine] = None


def create_db_url(env_file_path: Optional[str] = None) -> str:
    """Build database URL from .env variables."""
    load_dotenv(dotenv_path=env_file_path)

    database_url = os.getenv('DATABASE_URL')
    if database_url:
        return database_url

    db_user = os.getenv('POSTGRES_USER')
    db_password = os.getenv('POSTGRES_PASSWORD')
    db_host = os.getenv('POSTGRES_HOST', 'localhost')
    db_port = os.getenv('POSTGRES_PORT', '5432')
    db_name = os.getenv('POSTGRES_DB')
    db_driver = os.getenv('DB_DRIVER', 'asyncpg')
    db_dialect = os.getenv('DB_DIALECT', 'postgresql')

    return (
        f'{db_dialect}+{db_driver}://'
        f'{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    )


def create_async_engine_instance(db_url: str) -> AsyncEngine:
    """Create AsyncEngine instance with production-ready defaults."""
    return create_async_engine(
        db_url,
        echo=False,
        pool_pre_ping=True,
        pool_recycle=1800,
        pool_size=5,
        max_overflow=10,
        future=True,
    )


def get_async_engine(env_file_path: Optional[str] = None) -> AsyncEngine:
    """Get singleton AsyncEngine instance for the process."""
    global _engine

    if _engine is not None:
        return _engine

    db_url = create_db_url(env_file_path=env_file_path)
    _engine = create_async_engine_instance(db_url=db_url)

    return _engine


async def dispose_async_engine() -> None:
    """Dispose singleton engine and reset module state."""
    global _engine

    if _engine is None:
        return

    await _engine.dispose()
    _engine = None


async def check_db_connection(env_file_path: Optional[str] = None) -> bool:
    """Check database connectivity with a trivial query."""
    engine = get_async_engine(env_file_path=env_file_path)

    async with engine.connect() as connection:
        result = await connection.execute(text('SELECT 1'))
        result.scalar_one()

    return True


if __name__ == '__main__':
    connection_ok = asyncio.run(check_db_connection())
    print(connection_ok)
