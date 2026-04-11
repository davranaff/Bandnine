.PHONY: install lint test migrate upgrade seed seed-local run worker up down logs restart

APP_DIR=backend
PYTHON ?= python3
PIP ?= $(PYTHON) -m pip

install:
	$(PIP) install -r $(APP_DIR)/requirements.txt

lint:
	cd $(APP_DIR) && ruff check .

test:
	cd $(APP_DIR) && TEST_DATABASE_URL=sqlite+aiosqlite:///./test.db pytest -q

migrate:
	cd $(APP_DIR) && alembic revision --autogenerate -m "auto"

upgrade:
	cd $(APP_DIR) && alembic upgrade head

seed:
	docker compose up -d postgres redis api
	docker compose exec -T api python -m app.scripts.seed

seed-local:
	cd $(APP_DIR) && $(PYTHON) -m app.scripts.seed

run:
	cd $(APP_DIR) && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

worker:
	cd $(APP_DIR) && arq app.workers.arq_worker.WorkerSettings

up:
	docker compose up --build -d

down:
	docker compose down

logs:
	docker compose logs -f api frontend worker

restart:
	docker compose down && docker compose up --build
