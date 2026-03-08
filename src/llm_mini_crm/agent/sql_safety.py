import re
from dataclasses import dataclass
from typing import Literal


SafetyStatus = Literal['ok', 'blocked']


@dataclass(frozen=True)
class SafetyCheckResult:
    status: SafetyStatus
    reason: str


def normalize_sql(sql: str) -> str:
    """Normalize SQL string for safe checks.
    Args:
        sql (str): Raw SQL string."""
    normalized_sql = sql.strip()
    normalized_sql = re.sub(r'\s+', ' ', normalized_sql)
    return normalized_sql


def check_sql_allowed(sql: str) -> SafetyCheckResult:
    """Validate SQL contains only allowed operations.
    Args:
        sql (str): SQL string to validate."""
    normalized_sql = normalize_sql(sql)
    lowered_sql = normalized_sql.lower()

    if not lowered_sql:
        return SafetyCheckResult(
            status='blocked', reason='Empty SQL is not allowed')

    blocked_keywords = [
        'drop ',
        'alter ',
        'update ',
        'truncate ',
        'create ',
        'grant ',
        'revoke ',
        'comment ',
        'vacuum ',
        'analyze ',
    ]
    for keyword in blocked_keywords:
        if keyword in lowered_sql:
            return SafetyCheckResult(
                status='blocked',
                reason=f'Blocked keyword detected: {keyword.strip()}'
            )

    allowed_prefixes = ('select', 'insert', 'delete')
    if not lowered_sql.startswith(allowed_prefixes):
        return SafetyCheckResult(
            status='blocked',
            reason='Only SELECT, INSERT, DELETE are allowed'
        )

    return SafetyCheckResult(status='ok', reason='SQL is allowed')


def ensure_select_limit(sql: str, limit_value: int) -> str:
    """Ensure SELECT queries include a LIMIT clause.
    Args:
        sql (str): SQL query.
        limit_value (int): Limit value to enforce."""
    normalized_sql = normalize_sql(sql)
    lowered_sql = normalized_sql.lower()

    if not lowered_sql.startswith('select'):
        return normalized_sql

    if ' limit ' in lowered_sql:
        return normalized_sql

    limited_sql = f'{normalized_sql} LIMIT {int(limit_value)}'
    return limited_sql
