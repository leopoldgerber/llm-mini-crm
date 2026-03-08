import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AgentConfig:
    llm_model: str
    llm_temperature: float
    llm_max_tokens: int
    llm_timeout_seconds: int


def load_agent_config() -> AgentConfig:
    """Load agent configuration from environment variables.
    Args:
        _ (None): No arguments required."""
    llm_model = os.getenv('LLM_MODEL', 'gpt-4.1-mini')
    llm_temperature = float(os.getenv('LLM_TEMPERATURE', '0.0'))
    llm_max_tokens = int(os.getenv('LLM_MAX_TOKENS', '400'))
    llm_timeout_seconds = int(os.getenv('LLM_TIMEOUT_SECONDS', '30'))

    return AgentConfig(
        llm_model=llm_model,
        llm_temperature=llm_temperature,
        llm_max_tokens=llm_max_tokens,
        llm_timeout_seconds=llm_timeout_seconds,
    )
