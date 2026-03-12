import json
from datetime import date, datetime, time

from llm_mini_crm.agent.run_agent import normalize_rows, normalize_value


def test_normalize_value_converts_datetime_types() -> None:
    """Check datetime-like values are converted to isoformat strings.
    Args:
        _ (None): No arguments required."""
    timestamp = datetime(2026, 3, 12, 14, 30, 15)
    only_date = date(2026, 3, 12)
    only_time = time(14, 30, 15)

    normalized_timestamp = normalize_value(timestamp)
    normalized_date = normalize_value(only_date)
    normalized_time = normalize_value(only_time)

    assert normalized_timestamp == '2026-03-12T14:30:15'
    assert normalized_date == '2026-03-12'
    assert normalized_time == '14:30:15'


def test_normalize_rows_converts_nested_values() -> None:
    """Check row values are normalized recursively.
    Args:
        _ (None): No arguments required."""
    rows = [
        {
            'id': 1,
            'created_at': datetime(2026, 3, 12, 14, 30, 15),
            'meta': {
                'birth_date': date(1990, 5, 1),
                'login_time': time(9, 45, 0),
            },
        }
    ]

    normalized_rows = normalize_rows(rows)

    assert normalized_rows == [
        {
            'id': 1,
            'created_at': '2026-03-12T14:30:15',
            'meta': {
                'birth_date': '1990-05-01',
                'login_time': '09:45:00',
            },
        }
    ]


def test_normalized_rows_are_json_serializable() -> None:
    """Check normalized rows can be serialized to JSON.
    Args:
        _ (None): No arguments required."""
    rows = [
        {
            'id': 1,
            'created_at': datetime(2026, 3, 12, 14, 30, 15),
        }
    ]

    normalized_rows = normalize_rows(rows)
    json_text = json.dumps(normalized_rows, ensure_ascii=False, indent=2)

    assert '2026-03-12T14:30:15' in json_text
