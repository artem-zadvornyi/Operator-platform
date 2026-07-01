"""Tests for company session persistence mapping and repository behavior."""

from uuid import UUID

import pytest

from app.application.company_orchestrator import CompanyOrchestrator
from app.repositories.mappers.company_session_mapper import CompanySessionPersistenceMapper
from app.repositories.memory_company_repository import MemoryCompanyRepository
from app.stores.company_session import CompanySession


@pytest.fixture
async def company_session() -> CompanySession:
    repository = MemoryCompanyRepository()
    orchestrator = CompanyOrchestrator(repository=repository)
    response = await orchestrator.create_company("Persistence Test Brand")
    session = await repository.get(UUID(response.company_id))
    assert session is not None
    return session


@pytest.mark.asyncio
async def test_mapper_roundtrip_preserves_company_identity(company_session: CompanySession) -> None:
    mapper = CompanySessionPersistenceMapper()

    record = mapper.to_record(company_session)
    restored = mapper.to_session(record)

    assert restored.company_id == company_session.company_id
    assert restored.blueprint.company_name == company_session.blueprint.company_name
    assert restored.mission.title == company_session.mission.title
    assert restored.ceo.name == company_session.ceo.name
    assert restored.decision.title == company_session.decision.title
    assert len(restored.plan.steps) == len(company_session.plan.steps)
    assert len(restored.workflow.tasks) == len(company_session.workflow.tasks)
    assert restored.started == company_session.started


@pytest.mark.asyncio
async def test_memory_repository_persists_session_across_calls() -> None:
    repository = MemoryCompanyRepository()
    orchestrator = CompanyOrchestrator(repository=repository)

    created = await orchestrator.create_company("Memory Repository Brand")
    loaded = await repository.get(UUID(created.company_id))

    assert loaded is not None
    assert loaded.mission.title == "Memory Repository Brand"
