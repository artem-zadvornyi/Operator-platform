"""PostgreSQL-backed company session repository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.company_persistence import CompanyRecord, PlanRecord, WorkflowRecord
from app.repositories.mappers.company_session_mapper import CompanySessionPersistenceMapper
from app.stores.company_session import CompanySession


class SqlAlchemyCompanyRepository:
    """Persists company sessions through SQLAlchemy ORM aggregates."""

    def __init__(
        self,
        session: AsyncSession,
        mapper: CompanySessionPersistenceMapper | None = None,
    ) -> None:
        self._session = session
        self._mapper = mapper or CompanySessionPersistenceMapper()

    async def save(self, company_session: CompanySession) -> None:
        existing = await self._session.get(CompanyRecord, company_session.company_id)
        if existing is not None:
            await self._session.delete(existing)
            await self._session.flush()

        record = self._mapper.to_record(company_session)
        self._session.add(record)
        await self._session.commit()

    async def get(self, company_id: UUID) -> CompanySession | None:
        statement = (
            select(CompanyRecord)
            .where(CompanyRecord.id == company_id)
            .options(
                selectinload(CompanyRecord.departments),
                selectinload(CompanyRecord.mission),
                selectinload(CompanyRecord.ceo),
                selectinload(CompanyRecord.decision),
                selectinload(CompanyRecord.plan).selectinload(PlanRecord.steps),
                selectinload(CompanyRecord.workflow).selectinload(WorkflowRecord.tasks),
                selectinload(CompanyRecord.workflow).selectinload(WorkflowRecord.assignments),
            )
        )
        result = await self._session.execute(statement)
        record = result.scalar_one_or_none()
        if record is None:
            return None
        return self._mapper.to_session(record)
