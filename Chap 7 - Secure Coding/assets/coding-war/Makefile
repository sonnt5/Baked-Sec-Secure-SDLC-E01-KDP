.PHONY: help install install-frontend install-backend \
        dev dev-frontend dev-backend \
        up down restart build logs \
        db-migrate db-seed db-reset \
        lint lint-frontend format format-frontend \
        clean setup

# ──────────────────────────────────────────────
#  Help
# ──────────────────────────────────────────────
help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-22s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# ──────────────────────────────────────────────
#  Local development (no Docker)
# ──────────────────────────────────────────────
install: install-backend install-frontend ## Install all dependencies

install-backend: ## Install Python backend dependencies (venv recommended)
	cd backend-py && pip install -e ".[dev]"

install-frontend: ## Install frontend Node dependencies
	cd frontend && npm install

dev-backend: ## Run FastAPI backend locally with hot-reload
	cd backend-py && uvicorn app.main:app --host 0.0.0.0 --port 3000 --reload

dev-frontend: ## Run Vite frontend dev server
	cd frontend && npm run dev

# ──────────────────────────────────────────────
#  Docker Compose
# ──────────────────────────────────────────────
up: ## Start all services (detached)
	docker compose up -d

up-build: ## Build images then start all services (detached)
	docker compose up -d --build

down: ## Stop and remove containers
	docker compose down

restart: ## Restart all services
	docker compose restart

build: ## Build / rebuild all Docker images
	docker compose build

logs: ## Tail logs for all services  (use svc=<name> to filter)
	docker compose logs -f $(svc)

logs-backend: ## Tail backend API logs
	docker compose logs -f backend

logs-worker: ## Tail judge-worker (Celery) logs
	docker compose logs -f judge-worker

ps: ## Show running service status
	docker compose ps

# ──────────────────────────────────────────────
#  Database / migrations
# ──────────────────────────────────────────────
db-migrate: ## Apply Alembic migrations (inside backend container)
	docker compose exec backend alembic upgrade head

db-migrate-local: ## Apply Alembic migrations locally
	cd backend-py && alembic upgrade head

db-seed: ## Seed problems into the database (inside backend container)
	docker compose exec backend python seed_problems.py

db-seed-local: ## Seed problems locally
	cd backend-py && python seed_problems.py

db-reset: ## Drop all data and reapply migrations (DESTRUCTIVE)
	docker compose exec backend alembic downgrade base
	docker compose exec backend alembic upgrade head

# ──────────────────────────────────────────────
#  First-time setup
# ──────────────────────────────────────────────
setup: ## First-time setup: build images, start services, run migrations & seed
	docker compose up -d --build
	@echo "⏳ Waiting for services to be ready..."
	@sleep 15
	@echo "🔄 Running database migrations..."
	docker compose exec backend alembic upgrade head
	@echo "🌱 Seeding problems..."
	docker compose exec backend python seed_problems.py || true
	@echo "✅ Setup complete! Backend → http://localhost:3000  Frontend → http://localhost:5173"

# ──────────────────────────────────────────────
#  Lint & format
# ──────────────────────────────────────────────
lint: ## Lint Python backend (ruff)
	cd backend-py && ruff check .

lint-frontend: ## Lint frontend (ESLint)
	cd frontend && npm run lint

format: ## Format Python backend (ruff + black)
	cd backend-py && ruff format . && black .

format-frontend: ## Format frontend (Prettier)
	cd frontend && npm run format

# ──────────────────────────────────────────────
#  Cleanup
# ──────────────────────────────────────────────
clean: ## Stop services and remove volumes (DESTRUCTIVE)
	docker compose down -v
