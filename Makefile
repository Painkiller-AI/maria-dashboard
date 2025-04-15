include .env

install:
	git config core.hooksPath .githooks
	uv sync
run:
	uv run streamlit run src/main.py
compose:
	docker compose up --build --force-recreate
seed:
	docker exec maria_db sh -c "psql -U $(POSTGRES_USER) -d $(POSTGRES_DB) -f /scripts/console-dump-extensions.sql" || true
	docker exec maria_db sh -c "pg_restore -U $(POSTGRES_USER) -d $(POSTGRES_DB) --no-owner --role=$(POSTGRES_USER) --schema=public -1 /scripts/console-dump-maria_console.sql" || true
lint:
	uv run ruff check .
format:
	uv run ruff format .