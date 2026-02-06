.PHONY: help install-cli build test lint format clean

help:
	@echo "Product Forge - Makefile Commands"
	@echo ""
	@echo "Available commands:"
	@echo "  make install-cli    Install/reinstall forge-cli from current repo"
	@echo "  make build          Build the package"
	@echo "  make test           Run tests"
	@echo "  make lint           Run linter"
	@echo "  make format         Format code"
	@echo "  make clean          Clean build artifacts"

install-cli:
	@echo "Installing forge-cli globally from current repository..."
	@echo "Cleaning Python cache..."
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "Reinstalling as uv tool (globally available)..."
	uv tool install --force --editable .
	@echo ""
	@echo "✓ forge-cli installed successfully"
	@echo ""
	@echo "Verify installation:"
	@forge --version
	@echo ""
	@echo "Available commands:"
	@forge --help

build:
	@echo "Building package..."
	uv build
	@echo "✓ Build complete"

test:
	@echo "Running tests..."
	uv run pytest --cov=forge_hooks --cov-report=term

lint:
	@echo "Running linter..."
	uv run ruff check src tests

format:
	@echo "Formatting code..."
	uv run ruff format src tests

clean:
	@echo "Cleaning build artifacts..."
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -f .coverage
	rm -f coverage.xml
	@echo "✓ Clean complete"
