.PHONY: help install dev up down migrate test lint format

help:
	@echo "FastForge — Available commands"
	@echo ""
	@echo "  make install   Install all dependencies (uv + pnpm)"
	@echo "  make up        Start Docker services (postgres, redis, mailpit)"
	@echo "  make down      Stop Docker services"
	@echo "  make dev       Start development services"
	@echo "  make migrate   Run database migrations"
	@echo "  make test      Run all tests"
	@echo "  make lint      Run linters"
	@echo "  make format    Format code"

install:
	uv sync --all-packages
	pnpm install

up:
	docker compose up -d

down:
	docker compose down

dev: up
	@echo "TODO: Start api, web, and worker when implemented"

migrate:
	cd packages/database && uv run alembic upgrade head

test:
	uv run pytest

lint:
	uv run ruff check .
	uv run mypy packages/database/src
	pnpm lint

format:
	uv run ruff format .
	uv run ruff check --fix .
