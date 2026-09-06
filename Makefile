.PHONY: install train test lint format mlflow help

help:
	@echo "Available commands:"
	@echo "  make install   - install dependencies with uv"
	@echo "  make train     - run the training pipeline"
	@echo "  make test      - run the unit tests"
	@echo "  make lint      - check lint and formatting"
	@echo "  make format    - auto-format the project"
	@echo "  make mlflow    - launch the MLflow UI"

install:
	uv sync --locked --python 3.12

train:
	uv run python -m src.models.train

test:
	uv run pytest

lint:
	uv run ruff check .
	uv run ruff format --check .

format:
	uv run ruff format .

mlflow:
	uv run mlflow ui --backend-store-uri sqlite:///mlflow.db --host 127.0.0.1 --port 5000
