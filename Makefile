.PHONY: install lint test migrate upgrade seed run worker

APP_DIR=backend

install:
	pip install -r $(APP_DIR)/requirements.txt

lint:
	cd $(APP_DIR) && ruff check .

test:
	cd $(APP_DIR) && TEST_DATABASE_URL=sqlite+aiosqlite:///./test.db pytest -q

migrate:
	cd $(APP_DIR) && alembic revision --autogenerate -m "auto"

upgrade:
	cd $(APP_DIR) && alembic upgrade head

seed:
	cd $(APP_DIR) && python -m app.scripts.seed

run:
	cd $(APP_DIR) && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

worker:
	cd $(APP_DIR) && arq app.workers.arq_worker.WorkerSettings
