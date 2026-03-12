from dataclasses import dataclass
from typing import Any

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from llm_mini_crm.agent.schemas import (
    AgentDbResult, AgentSqlPlan, build_db_result)
from llm_mini_crm.agent.sql_safety import check_sql_allowed
from llm_mini_crm.db.scripts.connection import get_async_engine


@dataclass(frozen=True)
class DbToolConfig:
    tool_name: str


def build_db_tool_config() -> DbToolConfig:
    """Build db tool configuration.
    Args:
        _ (None): No arguments required."""
    return DbToolConfig(tool_name='db_tool')


def normalize_params(params: dict[str, Any]) -> dict[str, Any]:
    """Normalize sql params.
    Args:
        params (dict[str, Any]): Params dictionary."""
    if params is None:
        return {}

    if not isinstance(params, dict):
        return {}

    return params


def parse_result_rows(result_data: Any) -> list[dict[str, Any]]:
    """Parse SQLAlchemy result into list of dict rows.
    Args:
        result_data (Any): SQLAlchemy Result object."""
    if result_data is None:
        return []

    try:
        rows = result_data.mappings().all()
        return [dict(row) for row in rows]
    except Exception:
        return []


def parse_integrity_error(error: IntegrityError) -> str:
    """Parse integrity error into readable message.
    Args:
        error (IntegrityError): Database integrity error."""
    error_text = str(error).lower()

    if ('clients_email_key' in error_text
            or 'duplicate key value' in error_text):
        return 'Client with this email already exists.'

    return 'Database integrity error.'


async def execute_select(
        sql: str,
        params: dict[str, Any]
) -> list[dict[str, Any]]:
    """Execute SELECT query and fetch rows.
    Args:
        sql (str): SQL query string.
        params (dict[str, Any]): Named parameters."""
    engine = get_async_engine()
    safe_params = normalize_params(params=params)

    async with engine.connect() as connection:
        result_data = await connection.execute(text(sql), safe_params)
        rows = parse_result_rows(result_data=result_data)
        return rows


async def execute_change(sql: str, params: dict[str, Any]) -> int:
    """Execute INSERT or DELETE query and return affected rows.
    Args:
        sql (str): SQL query string.
        params (dict[str, Any]): Named parameters."""
    engine = get_async_engine()
    safe_params = normalize_params(params=params)

    try:
        async with engine.begin() as connection:
            result_data = await connection.execute(text(sql), safe_params)
            affected_count = (
                result_data.rowcount if result_data is not None else 0)
            return int(affected_count) if affected_count is not None else 0
    except IntegrityError as error:
        error_message = parse_integrity_error(error=error)
        raise ValueError(error_message) from error


async def execute_sql_plan(sql_plan: AgentSqlPlan) -> AgentDbResult:
    """Execute SQL plan against database and return rows.
    Args:
        sql_plan (AgentSqlPlan): SQL plan built by agent."""
    safety_result = check_sql_allowed(sql_plan.sql)
    if safety_result.status != 'ok':
        raise ValueError(f'SQL blocked: {safety_result.reason}')

    operation = str(sql_plan.operation).strip().lower()
    if operation == 'select':
        rows = await execute_select(sql=sql_plan.sql, params=sql_plan.params)
        return build_db_result(rows)

    if operation in ('insert', 'delete'):
        affected_count = await execute_change(
            sql=sql_plan.sql,
            params=sql_plan.params
        )
        rows = [{'affected_rows': affected_count}]
        return build_db_result(rows)

    raise ValueError('Unsupported operation for db tool')
