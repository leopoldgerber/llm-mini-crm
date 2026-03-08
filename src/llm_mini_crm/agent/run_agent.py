import asyncio
import json
# import sys

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


async def run_agent_once(user_text: str) -> None:
    """Run agent one time, execute SQL plan, print result.
    Args:
        user_text (str): Raw user input."""
    agent_config = load_agent_config()
    llm_config = load_llm_config(
        timeout_seconds=agent_config.llm_timeout_seconds)
    llm_client = LlmClient(llm_config)

    sql_agent_config = build_sql_agent_config()
    sql_agent = SqlAgent(
        agent_config=agent_config,
        llm_client=llm_client,
        sql_agent_config=sql_agent_config
    )

    agent_request = build_agent_request(user_text)
    sql_plan = await sql_agent.build_sql_plan(agent_request)

    db_result = await execute_sql_plan(sql_plan)

    output_data = {
        'request': user_text,
        'plan': {
            'operation': sql_plan.operation,
            'sql': sql_plan.sql,
            'params': sql_plan.params,
        },
        'result': db_result.rows,
    }
    print(json.dumps(output_data, ensure_ascii=False, indent=2))


def main(input_text: list[str]) -> None:
    """Run CLI entrypoint.
    Args:
        _ (None): No arguments required."""
    # user_text = read_user_text(sys.argv)
    user_text = read_user_text(input_text)
    if not user_text:
        print('Empty request.')
        return

    asyncio.run(run_agent_once(user_text))


if __name__ == '__main__':
    text = "Add client John Smith with email john.smith@example.co.uk"
    argv = ["script.py"] + text.split()
    main(argv)
