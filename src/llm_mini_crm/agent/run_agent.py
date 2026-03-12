import sys
import json
import asyncio
from datetime import date, datetime, time

from llm_mini_crm.agent.config import load_agent_config
from llm_mini_crm.agent.llm_client import LlmClient, load_llm_config
from llm_mini_crm.agent.schemas import build_agent_request
from llm_mini_crm.agent.sql_agent import SqlAgent, build_sql_agent_config
from llm_mini_crm.agent.tools.db_tool import execute_sql_plan


def read_user_text(argv: list[str]) -> str:
    """Read user text from CLI args or stdin.
    Args:
        argv (list[str]): CLI arguments."""
    if len(argv) > 1:
        user_text = ' '.join(argv[1:]).strip()
        return user_text

    user_text = input('Enter request: ').strip()
    return user_text


def normalize_value(data: object) -> object:
    """Normalize value for JSON serialization.
    Args:
        data (object): Input value to normalize."""
    if isinstance(data, dict):
        return {key: normalize_value(value) for key, value in data.items()}

    if isinstance(data, list):
        return [normalize_value(item) for item in data]

    if isinstance(data, (datetime, date, time)):
        return data.isoformat()

    return data


def normalize_rows(rows: list[dict[str, object]]) -> list[dict[str, object]]:
    """Normalize database rows for JSON serialization.
    Args:
        rows (list[dict[str, object]]): Database result rows."""
    normalized_rows = []

    for row in rows:
        normalized_row = {
            key: normalize_value(value)
            for key, value in row.items()
        }
        normalized_rows.append(normalized_row)

    return normalized_rows


async def run_agent_once(user_text: str) -> None:
    """Run agent one time, execute SQL plan, print result.
    Args:
        user_text (str): Raw user input."""
    try:
        agent_config = load_agent_config()
        llm_config = load_llm_config(
            timeout_seconds=agent_config.llm_timeout_seconds,
        )
        llm_client = LlmClient(llm_config)

        sql_agent_config = build_sql_agent_config()
        sql_agent = SqlAgent(
            agent_config=agent_config,
            llm_client=llm_client,
            sql_agent_config=sql_agent_config,
        )

        agent_request = build_agent_request(user_text)
        sql_plan = await sql_agent.build_sql_plan(agent_request)
        db_result = await execute_sql_plan(sql_plan)
        result_rows = normalize_rows(db_result.rows)

        output_data = {
            'status': 'success',
            'request': user_text,
            'plan': {
                'operation': sql_plan.operation,
                'sql': sql_plan.sql,
                'params': sql_plan.params,
            },
            'result': result_rows,
        }
        print(json.dumps(output_data, ensure_ascii=False, indent=2))
    except ValueError as error:
        error_data = {
            'status': 'error',
            'request': user_text,
            'message': str(error),
        }
        print(json.dumps(error_data, ensure_ascii=False, indent=2))
    except Exception as error:
        error_data = {
            'status': 'error',
            'request': user_text,
            'message': 'Unexpected application error.',
            'details': str(error),
        }
        print(json.dumps(error_data, ensure_ascii=False, indent=2))


def main(input_text: list[str]) -> None:
    """Run CLI entrypoint.
    Args:
        input_text (list[str]): Input arguments list."""
    user_text = read_user_text(input_text)
    if not user_text:
        print('Empty request.')
        return

    asyncio.run(run_agent_once(user_text))


if __name__ == '__main__':
    main(sys.argv)

    # # Use from root
    # text = "Add client John Smith with email john.smith@example.co.uk"
    # argv = ["script.py"] + text.split()
    # main(argv)
