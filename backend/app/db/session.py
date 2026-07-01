from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings


def require_async_database_runtime() -> None:
    """Ensure async SQLAlchemy dependencies are available before serving traffic."""
    try:
        import greenlet  # noqa: F401
    except ModuleNotFoundError as error:
        msg = (
            "greenlet is required for async SQLAlchemy but is not installed. "
            "Run `poetry install` in backend/ to install project dependencies."
        )
        raise RuntimeError(msg) from error


engine: AsyncEngine = create_async_engine(settings.database_url, echo=settings.debug)
async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


def dispose_database_engine() -> None:
    """Release database connections without requiring async greenlet shutdown."""
    engine.sync_engine.dispose()
