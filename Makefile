.PHONY: setup smoke install train test lint check format mlflow model-card promote monitor help

setup: install

smoke:
	uv run python -m scripts.smoke

check: lint test
	uv run python -m scripts.notebook_outputs --check

model-card:
	uv run python -m scripts.model_card

promote:
	uv run python -m src.models.gate

monitor:
	uv run python -m src.monitoring

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
	uv run python -m src.pipeline run

test:
	uv run pytest

lint:
	uv run ruff check .
	uv run ruff format --check .

format:
	uv run ruff format .

mlflow:
	uv run mlflow ui --backend-store-uri sqlite:///mlflow.db --host 127.0.0.1 --port 5000
