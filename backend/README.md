# Operator Backend

Python API and background workers for the Operator platform.

## Setup

```bash
poetry install
cp .env.example .env
docker compose up -d postgres
poetry run alembic upgrade head
```

Async SQLAlchemy requires `greenlet`. It is declared explicitly in `pyproject.toml`
because macOS reports `platform_machine=arm64`, which does not match SQLAlchemy's
default conditional `aarch64` marker. After pulling dependency changes, run
`poetry sync` to ensure your virtualenv is up to date.

## Run

```bash
poetry run operator-api
```

## Migrations

```bash
poetry run alembic upgrade head
```

PostgreSQL integration tests (optional):

```bash
OPERATOR_TEST_POSTGRES=1 poetry run pytest tests/repositories/test_sqlalchemy_company_repository.py
```

## Quality

```bash
poetry run ruff check .
poetry run ruff format --check .
poetry run mypy app
poetry run pytest
```
