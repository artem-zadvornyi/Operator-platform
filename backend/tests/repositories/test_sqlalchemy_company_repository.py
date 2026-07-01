"""Integration tests for SQLAlchemy company persistence."""

import os
from uuid import UUID

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

import app.models.company_persistence  # noqa: F401
from app.application.company_orchestrator import CompanyOrchestrator
from app.core.config import settings
from app.db.base import Base
from app.domain.ceo import CEOStatus
from app.repositories.sqlalchemy_company_repository import SqlAlchemyCompanyRepository

POSTGRES_REQUIRED = os.getenv("OPERATOR_TEST_POSTGRES", "0") == "1"
pytestmark = pytest.mark.skipif(
    not POSTGRES_REQUIRED,
    reason="Set OPERATOR_TEST_POSTGRES=1 to run PostgreSQL integration tests.",
)


@pytest.fixture
async def db_session() -> AsyncSession:
    engine = create_async_engine(settings.database_url, echo=False)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_sqlalchemy_repository_persists_company_session(db_session: AsyncSession) -> None:
    repository = SqlAlchemyCompanyRepository(db_session)
    orchestrator = CompanyOrchestrator(repository=repository)

    created = await orchestrator.create_company("PostgreSQL Persistence Brand")
    company_id = UUID(created.company_id)

    loaded = await repository.get(company_id)
    assert loaded is not None
    assert loaded.mission.title == "PostgreSQL Persistence Brand"
    assert loaded.workflow.tasks

    await orchestrator.start_company(company_id)
    restarted = await repository.get(company_id)
    assert restarted is not None
    assert restarted.started is True
    assert restarted.ceo.status is CEOStatus.EXECUTING


@pytest.mark.asyncio
async def test_database_tables_exist_after_migration_shape(db_session: AsyncSession) -> None:
    result = await db_session.execute(
        text(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'public' ORDER BY table_name"
        )
    )
    tables = {row[0] for row in result}
    assert "companies" in tables
    assert "missions" in tables
    assert "workflows" in tables
    assert "workflow_tasks" in tables
