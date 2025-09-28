# Makefile for RapidOCR Service

.PHONY: help install dev test lint format type-check clean run docker-build docker-run

help:  ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install dependencies
	uv sync

dev:  ## Install with dev dependencies
	uv sync --dev

test:  ## Run tests
	uv run pytest -v

lint:  ## Run linting
	uv run ruff check app/ tests/

format:  ## Format code
	uv run black app/ tests/
	uv run isort app/ tests/
	uv run ruff check --fix app/ tests/

type-check:  ## Run type checking
	uv run mypy app/

clean:  ## Clean temporary files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache/
	rm -rf temp/*
	rm -rf logs/*

run:  ## Run the application in development mode
	uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-prod:  ## Run in production mode
	uv run uvicorn app.main:app --host 0.0.0.0 --port 80

docker-build:  ## Build Docker image
	docker build -t rapidocr-service .

docker-run:  ## Run Docker container
	docker-compose up -d

docker-stop:  ## Stop Docker container
	docker-compose down

docker-logs:  ## View Docker logs
	docker-compose logs -f

check-all: lint type-check test  ## Run all checks
