# Makefile for Django Job Aggregator Project
# Run tests with coverage and cleanup

.PHONY: test clean help

# Default target
help:
	@echo "Available commands:"
	@echo "  make test    - Run all tests with coverage and cleanup"
	@echo "  make clean   - Clean up temporary files and cache"
	@echo "  make help    - Show this help message"

# Main test command - activates environment, runs tests with coverage, cleans up
test:
	@echo "🚀 Activating virtual environment and running tests..."
	@powershell -Command "& .\envir\Scripts\Activate.ps1; python -m pytest --cov=. --cov-report=html --cov-report=term-missing -v"
	@echo "🧹 Cleaning up temporary files..."
	@make clean
	@echo "✅ Tests completed! Coverage report saved to htmlcov/index.html"

# Clean up temporary files and cache
clean:
	@echo "🧹 Cleaning up temporary files..."
	@powershell -Command "Get-ChildItem -Path . -Recurse -Include '__pycache__' -Directory | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue"
	@powershell -Command "Get-ChildItem -Path . -Recurse -Include '*.pyc' -File | Remove-Item -Force -ErrorAction SilentlyContinue"
	@powershell -Command "Get-ChildItem -Path . -Recurse -Include '*.pyo' -File | Remove-Item -Force -ErrorAction SilentlyContinue"
	@powershell -Command "Get-ChildItem -Path . -Recurse -Include '.pytest_cache' -Directory | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue"
	@powershell -Command "Get-ChildItem -Path . -Recurse -Include '*.coverage' -File | Remove-Item -Force -ErrorAction SilentlyContinue"
	@echo "✨ Cleanup completed!"

# Alternative test commands for different scenarios
test-unit:
	@echo "🧪 Running unit tests only..."
	@powershell -Command "& .\envir\Scripts\Activate.ps1; python -m pytest tests/unit/ -v"

test-integration:
	@echo "🔗 Running integration tests only..."
	@powershell -Command "& .\envir\Scripts\Activate.ps1; python -m pytest tests/integration/ -v"

test-fast:
	@echo "⚡ Running tests without coverage (fast)..."
	@powershell -Command "& .\envir\Scripts\Activate.ps1; python -m pytest -x --tb=short"

# Development server
run:
	@echo "🌐 Starting Django development server..."
	@powershell -Command "& .\envir\Scripts\Activate.ps1; python manage.py runserver"

# Database operations
migrate:
	@echo "🗄️ Running database migrations..."
	@powershell -Command "& .\envir\Scripts\Activate.ps1; python manage.py migrate"

makemigrations:
	@echo "📝 Making database migrations..."
	@powershell -Command "& .\envir\Scripts\Activate.ps1; python manage.py makemigrations"