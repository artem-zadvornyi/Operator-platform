# Operator Backend

Python API and background workers for the Operator platform.

## Setup

```bash
poetry install
cp .env.example .env
```

## Run

```bash
poetry run operator-api
```

## Migrations

```bash
poetry run alembic upgrade head
```

## Quality

```bash
poetry run ruff check .
poetry run ruff format --check .
poetry run mypy app
poetry run pytest
```
