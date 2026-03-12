import pytest
from llm_mini_crm.agent.sql_agent import validate_llm_plan


def test_validate_llm_plan_builds_valid_plan() -> None:
    """Check valid LLM plan is converted to AgentSqlPlan.
    Args:
        _ (None): No arguments required."""
    plan_data = {
        'operation': 'select',
        'sql': 'SELECT id, full_name FROM clients',
        'params': {},
    }

    sql_plan = validate_llm_plan(plan_data)

    assert sql_plan.operation == 'select'
    assert sql_plan.sql == 'SELECT id, full_name FROM clients'
    assert sql_plan.params == {}


def test_validate_llm_plan_rejects_invalid_operation() -> None:
    """Check invalid operation raises ValueError.
    Args:
        _ (None): No arguments required."""
    plan_data = {
        'operation': 'update',
        'sql': 'UPDATE clients SET email = :email WHERE id = :id',
        'params': {'id': 1, 'email': 'new@example.com'},
    }

    with pytest.raises(ValueError, match='Invalid operation in LLM response'):
        validate_llm_plan(plan_data)


def test_validate_llm_plan_rejects_empty_sql() -> None:
    """Check empty SQL raises ValueError.
    Args:
        _ (None): No arguments required."""
    plan_data = {
        'operation': 'select',
        'sql': '',
        'params': {},
    }

    with pytest.raises(ValueError, match='Empty sql in LLM response'):
        validate_llm_plan(plan_data)


def test_validate_llm_plan_rejects_invalid_params() -> None:
    """Check non-dict params raises ValueError.
    Args:
        _ (None): No arguments required."""
    plan_data = {
        'operation': 'select',
        'sql': 'SELECT id FROM clients',
        'params': ['bad', 'params'],
    }

    with pytest.raises(ValueError, match='Invalid params in LLM response'):
        validate_llm_plan(plan_data)


def test_validate_llm_plan_replaces_none_params() -> None:
    """Check None params are replaced with empty dict.
    Args:
        _ (None): No arguments required."""
    plan_data = {
        'operation': 'delete',
        'sql': 'DELETE FROM clients WHERE id = :id',
        'params': None,
    }

    sql_plan = validate_llm_plan(plan_data)

    assert sql_plan.operation == 'delete'
    assert sql_plan.params == {}
