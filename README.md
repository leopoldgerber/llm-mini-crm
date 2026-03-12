
# llm-mini-crm

Lightweight demo of an LLM-powered SQL agent for a mini CRM dataset.

## Overview
`llm-mini-crm` is a compact demo project that shows how an LLM-based agent can:
- interpret a natural language request
- build an SQL execution plan
- validate the generated SQL
- execute it against a PostgreSQL database
- return a structured JSON response

The project is intentionally small and focused. It is designed as a clean baseline example of agent orchestration, tool calling, and database interaction.

## Architecture

The system follows a simple flow:
```text
User request
    ↓
CLI entrypoint
    ↓
Agent request builder
    ↓
SQL agent
    ↓
LLM generates SQL plan
    ↓
SQL validation and safety checks
    ↓
Database tool executes SQL
    ↓
Structured JSON response
````

## Project structure

```text
llm-mini-crm/
├── src/
│   └── llm_mini_crm/
│       ├── agent/
│       │   ├── run_agent.py
│       │   ├── sql_agent.py
│       │   ├── sql_safety.py
│       │   ├── llm_client.py
│       │   ├── config.py
│       │   └── schemas.py
│       └── db/
│           └── init_clients_table.py
├── tests/
├── .env.example
├── Makefile
├── pyproject.toml
└── docker-compose.yml
```

## Requirements

Before running the project, make sure you have:
* Python 3.10+
* Docker and Docker Compose
* PostgreSQL running through Docker
* an OpenAI-compatible API key

## Environment variables

Create a local `.env` file from `.env.example`.

Example:
```dotenv
# Postgres
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=postgres

# LLM
LLM_API_KEY=your_api_key_here
LLM_BASE_URL=https://api.openai.com
LLM_ENDPOINT_PATH=/v1/chat/completions
```

## Installation

Clone the repository and install dependencies:
```bash
pip install -e .
```

Or, if preferred:
```bash
pip install .
```

## Running the project
### 1. Start PostgreSQL
```bash
make run
```

### 2. Initialize the database
```bash
make init-db
```

### 3. Run the agent
```bash
make run-agent
```

You can also run it directly:
```bash
python -m llm_mini_crm.agent.run_agent
```

If no CLI arguments are provided, the script will ask for input interactively.

Example:
```bash
python -m llm_mini_crm.agent.run_agent "Find all clients"
```

## Makefile commands
- `make run` — start PostgreSQL via Docker
- `make init-db` — initialize the demo database
- `make run-agent` — run the CLI agent
- `make test` — run unit tests

## Example workflow

Example request:
```text
Find all clients
```

Example response:
```json
{
  "status": "success",
  "request": "Find all clients",
  "plan": {
    "operation": "select",
    "sql": "SELECT * FROM clients LIMIT 100",
    "params": {}
  },
  "result": [
    {
      "id": 1,
      "full_name": "John Smith",
      "email": "john.smith@example.com"
    }
  ]
}
```

## Testing

Run tests with:
```bash
make test
```

or:
```bash
pytest tests -v
```

The test suite covers core project behavior such as:
* SQL safety checks
* automatic `LIMIT` handling
* LLM SQL plan validation
* JSON serialization of database results

## Limitations

This project has several intentional limitations:
* no web API
* no frontend
* no authentication
* no persistent conversational memory
* no multi-agent orchestration
* no advanced retry or recovery logic
* limited SQL operation scope
* designed for demo and learning purposes only

## Future improvements
Possible next steps for a more advanced version:
* add richer validation and guardrails
* support more complex CRM operations
* add logging and tracing
* introduce evaluation scenarios
* add an API layer
* support routing across multiple tools
* add memory or stateful user context

## License

MIT License
