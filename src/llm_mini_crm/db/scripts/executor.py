from loguru import logger
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine


async def execute_query(
    statements: list[str],
    engine: AsyncEngine,
    raise_on_error: bool = False,
) -> int:
    """Execute SQL statements within a single transaction.
    Args:
        statements (list[str]): SQL statements to execute in order.
        engine (AsyncEngine): Async SQLAlchemy engine.
        raise_on_error (bool): Whether to raise on the first execution error.
    """
    if not isinstance(statements, list) or not statements:
        logger.error('Statements must be a non-empty list.')
        return 0

    if engine is None:
        logger.error('Engine must not be None.')
        return 0

    executed_count = 0

    try:
        async with engine.begin() as connection:
            for statement in statements:
                if not isinstance(statement, str) or not statement.strip():
                    continue

                await connection.execute(text(statement))
                executed_count += 1

        logger.info(f'Executed statements: {executed_count}')
        return executed_count

    except Exception as error:
        logger.error(f'Error executing SQL statements: {error}')

        if raise_on_error:
            raise

        return executed_count
