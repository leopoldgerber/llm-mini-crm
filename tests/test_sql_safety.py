from llm_mini_crm.agent.sql_safety import (
    check_sql_allowed, ensure_select_limit)


def test_check_sql_allowed_blocks_update() -> None:
    """Check blocked SQL keyword is rejected.
    Args:
        _ (None): No arguments required."""
    sql = 'UPDATE clients SET email = :email WHERE id = :id'
    result = check_sql_allowed(sql)

    assert result.status == 'blocked'
    assert 'Blocked keyword detected' in result.reason


def test_check_sql_allowed_accepts_select() -> None:
    """Check valid SELECT query is allowed.
    Args:
        _ (None): No arguments required."""
    sql = 'SELECT id, full_name FROM clients'
    result = check_sql_allowed(sql)

    assert result.status == 'ok'
    assert result.reason == 'SQL is allowed'


def test_ensure_select_limit_adds_limit() -> None:
    """Check LIMIT is added to SELECT query when absent.
    Args:
        _ (None): No arguments required."""
    sql = 'SELECT id, full_name FROM clients'
    limited_sql = ensure_select_limit(sql, 50)

    assert limited_sql == 'SELECT id, full_name FROM clients LIMIT 50'


def test_ensure_select_limit_keeps_existing_limit() -> None:
    """Check existing LIMIT clause is preserved.
    Args:
        _ (None): No arguments required."""
    sql = 'SELECT id, full_name FROM clients LIMIT 10'
    limited_sql = ensure_select_limit(sql, 50)

    assert limited_sql == 'SELECT id, full_name FROM clients LIMIT 10'


def test_ensure_select_limit_does_not_change_insert() -> None:
    """Check non-SELECT query is returned unchanged.
    Args:
        _ (None): No arguments required."""
    sql = 'INSERT INTO clients (full_name, email) VALUES (:full_name, :email)'
    limited_sql = ensure_select_limit(sql, 50)

    assert limited_sql == sql
