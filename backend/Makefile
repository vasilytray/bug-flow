# Makefile для удобства

# backend/Makefile
.PHONY: help install dev test db migrate lint format clean

help:
	@echo "Available commands:"
	@echo "  install     Install dependencies"
	@echo "  dev         Run development server"
	@echo "  test        Run tests"
	@echo "  db          Start database services"
	@echo "  migrate     Create and run migrations"
	@echo "  lint        Run code linting"
	@echo "  format      Format code"
	@echo "  clean       Clean up temporary files"

install:
	pip install -r requirements.txt
	pip install -r requirements/dev.txt

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest tests/ -v --cov=app --cov-report=html

db:
	docker-compose -f ../docker-compose.dev.yml up -d postgres redis minio

db-down:
	docker-compose -f ../docker-compose.dev.yml down

migrate:
	alembic revision --autogenerate -m "$(m)"
	alembic upgrade head

migrate-downgrade:
	alembic downgrade -1

lint:
	flake8 app/
	mypy app/
	isort --check-only app/
	black --check app/

format:
	isort app/
	black app/

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name ".pytest_cache" -delete
	find . -type d -name ".mypy_cache" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".coverage" -delete
	find . -type d -name "htmlcov" -exec rm -rf {} +