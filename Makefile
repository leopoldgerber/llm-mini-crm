include .env
export

.PHONY: run stop remove restart init-db run-agent test

run:
	docker compose up -d

stop:
	docker compose stop

remove:
	docker compose down

restart: stop run

init-db:
	python -m llm_mini_crm.db.init_clients_table

run-agent:
	python -m llm_mini_crm.agent.run_agent

test:
	pytest tests -v