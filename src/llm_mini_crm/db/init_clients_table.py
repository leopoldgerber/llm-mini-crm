import asyncio
from pathlib import Path

from loguru import logger

from llm_mini_crm.db.scripts.connection import (
    dispose_async_engine, get_async_engine)
from llm_mini_crm.db.scripts.executor import execute_query


def build_queries_dir(script_path: Path) -> Path:
    """Build queries directory path relative to the script.
    Args:
        script_path (Path): Path to the current script file.
    """
    return script_path.parent / 'queries'


def read_sql_file(file_path: Path) -> str:
    """Read SQL file content as text.
    Args:
        file_path (Path): Path to the .sql file.
    """
    return file_path.read_text(encoding='utf-8')


def collect_sql_statements(
        queries_dir: Path,
        file_names: list[str]
) -> list[str]:
    """Load SQL statements from multiple files.
    Args:
        queries_dir (Path): Directory containing .sql files.
        file_names (list[str]): Ordered list of .sql file names.
    """
    if not isinstance(file_names, list) or not file_names:
        return []

    statements: list[str] = []

    for file_name in file_names:
        file_path = queries_dir / file_name
        if not file_path.exists():
            logger.error(f'SQL file not found: {file_path}')
            continue

        sql_text = read_sql_file(file_path=file_path).strip()
        if sql_text:
            statements.append(sql_text)

    return statements


async def init_clients_table() -> int:
    """Initialize clients table and seed initial data."""
    script_path = Path(__file__).resolve()
    queries_dir = build_queries_dir(script_path=script_path)

    file_names = [
        '001_drop_clients.sql',
        '002_create_clients.sql',
        '003_create_index.sql',
        '004_insert_clients.sql',
    ]

    engine = get_async_engine()
    statements = collect_sql_statements(
        queries_dir=queries_dir,
        file_names=file_names
    )

    if not statements:
        logger.error('No SQL statements collected. Nothing to execute.')
        return 0

    executed_count = await execute_query(statements=statements, engine=engine)
    return executed_count


async def run_init() -> None:
    """Run init script with graceful shutdown."""
    try:
        executed_count = await init_clients_table()
        logger.info(f'Init finished. Executed statements: {executed_count}')
    finally:
        await dispose_async_engine()


if __name__ == '__main__':
    asyncio.run(run_init())
