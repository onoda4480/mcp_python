.PHONY: help install install-dev test test-cov lint format clean docker-build docker-run

# デフォルトターゲット
help:
	@echo "Available commands:"
	@echo "  make install      - Install production dependencies"
	@echo "  make install-dev  - Install development dependencies"
	@echo "  make test         - Run tests"
	@echo "  make test-cov     - Run tests with coverage"
	@echo "  make lint         - Run linter (ruff)"
	@echo "  make format       - Format code (ruff)"
	@echo "  make clean        - Clean up generated files"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-run   - Run Docker container"

# 依存関係のインストール
install:
	poetry install --no-dev

install-dev:
	poetry install

# テスト実行
test:
	poetry run pytest

test-cov:
	poetry run pytest --cov=src/mcp_server --cov-report=html --cov-report=term

# リンター・フォーマッター
lint:
	poetry run ruff check src/ tests/

format:
	poetry run ruff format src/ tests/
	poetry run ruff check --fix src/ tests/

# クリーンアップ
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete
	rm -rf dist/ build/ *.egg-info

# Docker
docker-build:
	docker build -t mcp-document-server:latest .

docker-run:
	docker run -it --rm \
		-v $(PWD)/docs:/app/docs:ro \
		mcp-document-server:latest

docker-compose-up:
	docker-compose up -d

docker-compose-down:
	docker-compose down

# サーバー実行（開発用）
run:
	poetry run python -m mcp_server.main

# MCP Inspector でテスト
inspect:
	npx @modelcontextprotocol/inspector poetry run python -m mcp_server.main
