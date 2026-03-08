from dataclasses import dataclass
from typing import Any

from llm_mini_crm.agent.config import AgentConfig
from llm_mini_crm.agent.llm_client import LlmClient, parse_json_text
from llm_mini_crm.agent.prompts import SYSTEM_PROMPT, build_user_prompt
from llm_mini_crm.agent.schemas import AgentRequest, AgentSqlPlan
from llm_mini_crm.agent.sql_safety import (
    check_sql_allowed, ensure_select_limit)


@dataclass(frozen=True)
class SqlAgentConfig:
    select_limit: int


def build_sql_agent_config() -> SqlAgentConfig:
    """Build SQL agent configuration.
    Args:
        _ (None): No arguments required."""
    return SqlAgentConfig(select_limit=50)


def validate_llm_plan(plan_data: dict[str, Any]) -> AgentSqlPlan:
    """Validate and build AgentSqlPlan from LLM json.
    Args:
        plan_data (dict[str, Any]): Parsed JSON returned by LLM."""
    operation_value = str(plan_data.get('operation', '')).strip().lower()
    sql_value = str(plan_data.get('sql', '')).strip()
    params_value = plan_data.get('params', {})

    if operation_value not in ('select', 'insert', 'delete'):
        raise ValueError('Invalid operation in LLM response')

    if not sql_value:
        raise ValueError('Empty sql in LLM response')

    if params_value is None:
        params_value = {}

    if not isinstance(params_value, dict):
        raise ValueError('Invalid params in LLM response')

    operation_typed = operation_value  # type: ignore[assignment]
    return AgentSqlPlan(
        operation=operation_typed,
        sql=sql_value,
        params=params_value,
    )


class SqlAgent:
    def __init__(
            self,
            agent_config: AgentConfig,
            llm_client: LlmClient,
            sql_agent_config: SqlAgentConfig
    ) -> None:
        self._agent_config = agent_config
        self._llm_client = llm_client
        self._sql_agent_config = sql_agent_config

    async def build_sql_plan(
            self,
            agent_request: AgentRequest
    ) -> AgentSqlPlan:
        """Build SQL plan using LLM.
        Args:
            agent_request (AgentRequest): Agent request wrapper."""
        user_prompt = build_user_prompt(agent_request.user_text)

        llm_text = await self._llm_client.generate_text(
            model=self._agent_config.llm_model,
            temperature=self._agent_config.llm_temperature,
            max_tokens=self._agent_config.llm_max_tokens,
            system_prompt=SYSTEM_PROMPT,
            user_prompt=user_prompt,
        )

        plan_data = parse_json_text(llm_text)
        sql_plan = validate_llm_plan(plan_data)

        safety_result = check_sql_allowed(sql_plan.sql)
        if safety_result.status != 'ok':
            raise ValueError(f'SQL blocked: {safety_result.reason}')

        safe_sql = ensure_select_limit(
            sql_plan.sql, self._sql_agent_config.select_limit)

        return AgentSqlPlan(
            operation=sql_plan.operation,
            sql=safe_sql,
            params=sql_plan.params,
        )
