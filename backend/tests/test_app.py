from fastapi import FastAPI

from app.db.session import dispose_database_engine
from app.main import create_app


def test_create_app_returns_fastapi_instance() -> None:
    application = create_app()
    assert isinstance(application, FastAPI)


def test_dispose_database_engine_does_not_require_greenlet() -> None:
    dispose_database_engine()
