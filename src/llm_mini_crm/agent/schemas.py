from dataclasses import dataclass
from typing import Any, Literal


OperationType = Literal['select', 'insert', 'delete']


@dataclass(frozen=True)
class AgentRequest:
    user_text: str


@dataclass(frozen=True)
class AgentSqlPlan:
    operation: OperationType
    sql: str
    params: dict[str, Any]


@dataclass(frozen=True)
class AgentDbResult:
    rows: list[dict[str, Any]]


def build_agent_request(user_text: str) -> AgentRequest:
    """Build agent request from raw user text.
    Args:
        user_text (str): Raw user input."""
    cleaned_text = user_text.strip()
    return AgentRequest(user_text=cleaned_text)


def build_db_result(rows: list[dict[str, Any]]) -> AgentDbResult:
    """Build database result wrapper.
    Args:
        rows (list[dict[str, Any]]): Rows returned by database."""
    safe_rows = rows if rows is not None else []
    return AgentDbResult(rows=safe_rows)
