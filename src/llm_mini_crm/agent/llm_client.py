import os
import json
import httpx
from typing import Any
from dataclasses import dataclass
from dotenv import load_dotenv
load_dotenv()


@dataclass(frozen=True)
class LlmClientConfig:
    api_key: str
    base_url: str
    endpoint_path: str
    timeout_seconds: int


def load_llm_config(timeout_seconds: int) -> LlmClientConfig:
    """Load LLM client configuration from environment variables.
    Args:
        timeout_seconds (int): Request timeout in seconds."""
    api_key = os.getenv('LLM_API_KEY', '').strip()
    base_url = os.getenv('LLM_BASE_URL', 'https://api.openai.com').strip()
    endpoint_path = os.getenv(
        'LLM_ENDPOINT_PATH',
        '/v1/chat/completions'
    ).strip()

    return LlmClientConfig(
        api_key=api_key,
        base_url=base_url,
        endpoint_path=endpoint_path,
        timeout_seconds=timeout_seconds,
    )


def build_auth_headers(api_key: str) -> dict[str, str]:
    """Build authorization headers for LLM requests.
    Args:
        api_key (str): API key string."""
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }
    return headers


def build_chat_payload(
    model: str,
    temperature: float,
    max_tokens: int,
    system_prompt: str,
    user_prompt: str,
) -> dict[str, Any]:
    """Build chat payload for an OpenAI-compatible chat completions endpoint.
    Args:
        model (str): Model name.
        temperature (float): Sampling temperature.
        max_tokens (int): Maximum output tokens.
        system_prompt (str): System prompt content.
        user_prompt (str): User prompt content."""
    payload = {
        'model': model,
        'temperature': float(temperature),
        'max_tokens': int(max_tokens),
        'messages': [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt},
        ],
    }
    return payload


def extract_chat_text(response_data: dict[str, Any]) -> str:
    """Extract assistant text from chat completions response.
    Args:
        response_data (dict[str, Any]): Raw response json."""
    choices = response_data.get('choices', [])
    if not choices:
        return ''

    message = choices[0].get('message', {})
    content = message.get('content', '')
    if content is None:
        return ''

    return str(content)


class LlmClient:
    def __init__(self, client_config: LlmClientConfig) -> None:
        self._client_config = client_config

    async def generate_text(
        self,
        model: str,
        temperature: float,
        max_tokens: int,
        system_prompt: str,
        user_prompt: str,
    ) -> str:
        """Generate text response from LLM.
        Args:
            model (str): Model name.
            temperature (float): Sampling temperature.
            max_tokens (int): Maximum output tokens.
            system_prompt (str): System prompt content.
            user_prompt (str): User prompt content."""
        if not self._client_config.api_key:
            raise ValueError('LLM_API_KEY is not set')

        url = f'{self._client_config.base_url}'
        url = f'{url}{self._client_config.endpoint_path}'

        headers = build_auth_headers(self._client_config.api_key)
        payload = build_chat_payload(
            model, temperature, max_tokens, system_prompt, user_prompt)
        timeout = httpx.Timeout(self._client_config.timeout_seconds)

        async with httpx.AsyncClient(timeout=timeout) as http_client:
            response = await http_client.post(
                url,
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            response_data = response.json()

        text = extract_chat_text(response_data)
        return text


def parse_json_text(text: str) -> dict[str, Any]:
    """Parse JSON object from text.
    Args:
        text (str): Raw text that should contain a JSON object."""
    cleaned_text = text.strip()

    if cleaned_text.startswith('```'):
        cleaned_text = cleaned_text.strip('`').strip()
        if cleaned_text.lower().startswith('json'):
            cleaned_text = cleaned_text[4:].strip()

    parsed_data = json.loads(cleaned_text)
    if not isinstance(parsed_data, dict):
        raise ValueError('LLM output is not a JSON object')

    return parsed_data


async def test_llm_connection() -> None:
    """Test LLM connectivity with a simple request.
    Args:
        _ (None): No arguments required."""
    client_config = load_llm_config(timeout_seconds=15)
    llm_client = LlmClient(client_config)

    system_prompt = 'You are a helpful assistant.'
    user_prompt = 'Reply with a short confirmation message.'

    try:
        response_text = await llm_client.generate_text(
            model='gpt-4.1-mini',
            temperature=0.0,
            max_tokens=50,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )
        print('LLM connection successful.')
        print('Response:')
        print(response_text)
    except Exception as error:
        print('LLM connection failed.')
        print(str(error))


if __name__ == '__main__':
    import asyncio
    asyncio.run(test_llm_connection())
