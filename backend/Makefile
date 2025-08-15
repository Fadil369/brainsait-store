# Makefile for brainsait-store backend testing and development

.PHONY: help test test-unit test-integration test-api test-db test-all test-fast test-coverage test-comprehensive test-quality clean install dev docs

# Default target
help:
	@echo "BrainSAIT Store Backend - Available Commands:"
	@echo ""
	@echo "Testing Commands:"
	@echo "  test                 Run all tests"
	@echo "  test-unit           Run unit tests only"
	@echo "  test-integration    Run integration tests"
	@echo "  test-api            Run API endpoint tests"
	@echo "  test-db             Run database tests"
	@echo "  test-fast           Run tests in fast mode (stop on first failure)"
	@echo "  test-coverage       Generate coverage report"
	@echo "  test-comprehensive  Run comprehensive test suite"
	@echo "  test-quality        Run code quality checks"
	@echo ""
	@echo "Development Commands:"
	@echo "  install             Install dependencies"
	@echo "  dev                 Start development server"
	@echo "  clean               Clean test artifacts and cache"
	@echo "  docs                Generate documentation"
	@echo ""
	@echo "Examples:"
	@echo "  make test                    # Run all tests"
	@echo "  make test-unit              # Run only unit tests"
	@echo "  make test-comprehensive     # Run full test suite"
	@echo "  make test-quality           # Check code quality"

# Testing commands using the test runner script
test:
	@python scripts/test_runner.py --category all

test-unit:
	@python scripts/test_runner.py --category unit

test-integration:
	@python scripts/test_runner.py --category integration

test-api:
	@python scripts/test_runner.py --category api

test-db:
	@python scripts/test_runner.py --category db

test-performance:
	@python scripts/test_runner.py --category performance

test-security:
	@python scripts/test_runner.py --category security

test-slow:
	@python scripts/test_runner.py --category slow

test-fast:
	@python scripts/test_runner.py --category all --fast

test-coverage:
	@python scripts/test_runner.py --coverage

test-comprehensive:
	@python scripts/test_runner.py --comprehensive

test-quality:
	@python scripts/test_runner.py --quality

# Development commands
install:
	@echo "📦 Installing dependencies..."
	@pip install -r requirements.txt
	@pip install -r requirements-dev.txt

dev:
	@echo "🚀 Starting development server..."
	@uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Maintenance commands
clean:
	@echo "🧹 Cleaning artifacts..."
	@python scripts/test_runner.py --clean
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type f -name ".DS_Store" -delete

# Documentation generation
docs:
	@echo "📚 Generating documentation..."
	@python -m sphinx.cmd.build -b html docs/ docs/_build/html/

# Database commands
db-migrate:
	@echo "🔄 Running database migrations..."
	@alembic upgrade head

db-revision:
	@echo "📝 Creating new migration..."
	@alembic revision --autogenerate -m "$(MSG)"

db-reset:
	@echo "🗃️  Resetting database..."
	@rm -f *.db
	@alembic upgrade head

# Code formatting and linting
format:
	@echo "🎨 Formatting code..."
	@black app tests
	@isort app tests

lint:
	@echo "🔍 Linting code..."
	@flake8 app tests
	@mypy app

# Security scanning
security-scan:
	@echo "🔒 Running security scan..."
	@bandit -r app/
	@safety check

# Performance profiling
profile:
	@echo "⚡ Running performance profiling..."
	@python -m cProfile -o profile.stats scripts/load_test.py

# Docker commands
docker-build:
	@echo "🐳 Building Docker image..."
	@docker build -t brainsait-backend .

docker-run:
	@echo "🐳 Running Docker container..."
	@docker run -p 8000:8000 brainsait-backend

# CI/CD helpers
ci-test:
	@echo "🔄 Running CI test suite..."
	@python scripts/test_runner.py --comprehensive --fast

ci-quality:
	@echo "🔄 Running CI quality checks..."
	@python scripts/test_runner.py --quality

# Environment setup
env-setup:
	@echo "🏗️  Setting up environment..."
	@cp .env.example .env
	@echo "Please edit .env file with your configuration"

# Backup and restore
backup-db:
	@echo "💾 Backing up database..."
	@mkdir -p backups
	@cp *.db backups/backup_$(shell date +%Y%m%d_%H%M%S).db

# Load testing
load-test:
	@echo "🚦 Running load tests..."
	@locust --host=http://localhost:8000 --headless --users 10 --spawn-rate 2 -t 30s

# Monitoring
health-check:
	@echo "❤️  Checking application health..."
	@curl -f http://localhost:8000/health || echo "❌ Health check failed"

# Analytics
test-analytics:
	@echo "📊 Generating test analytics..."
	@python -c "import json; import glob; files = glob.glob('htmlcov/*.html'); print(f'Coverage files: {len(files)}')"

# Integration with external services
sync-schemas:
	@echo "🔄 Syncing API schemas..."
	@python scripts/sync_schemas.py

# Release preparation
prepare-release:
	@echo "🎯 Preparing release..."
	@python scripts/test_runner.py --comprehensive
	@python scripts/test_runner.py --quality
	@echo "✅ Release preparation complete"

# Quick development workflow
quick-test:
	@echo "⚡ Quick test run..."
	@python scripts/test_runner.py --category unit --fast

dev-test:
	@echo "🔧 Development test cycle..."
	@python scripts/test_runner.py --category unit
	@python scripts/test_runner.py --category integration