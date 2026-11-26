.PHONY: autoformat type lint test test-cov dev full install docs-gen self-install all precommit

autoformat:
	uv run ruff check lintel/ tests/ --fix
	uv run ruff format lintel/ tests/

type:
	uv run pyright lintel/

lint:
	uv run ruff check lintel/ tests/
	uv run ruff format lintel/ tests/ --check

test:
	uv run pytest tests/

test-cov:
	uv run pytest tests/ --cov=lintel

dev:
	uv sync --extra dev

full:
	uv sync --all-extras --extra dev

install:
	uv sync

docs-gen:
	uv run python ./docs/pydocs/generate_pydocs.py

self-install:
	pip install -e .

all: autoformat type lint test

precommit:
	uv run pyright lintel/
	make lint
