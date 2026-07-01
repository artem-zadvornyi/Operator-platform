from fastapi import FastAPI

from app.db.session import dispose_database_engine, require_async_database_runtime
from app.main import create_app


def test_create_app_returns_fastapi_instance() -> None:
    application = create_app()
    assert isinstance(application, FastAPI)


def test_async_database_runtime_requires_greenlet() -> None:
    require_async_database_runtime()


def test_dispose_database_engine_does_not_require_greenlet() -> None:
    dispose_database_engine()
