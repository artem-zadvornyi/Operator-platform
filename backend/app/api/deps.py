from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.company_orchestrator import CompanyOrchestrator
from app.db.session import async_session_factory
from app.repositories.company_repository import CompanyRepository
from app.repositories.sqlalchemy_company_repository import SqlAlchemyCompanyRepository


async def get_db_session() -> AsyncIterator[AsyncSession]:
    async with async_session_factory() as session:
        yield session


async def get_company_repository(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
) -> CompanyRepository:
    return SqlAlchemyCompanyRepository(db_session)


async def get_company_orchestrator(
    repository: Annotated[CompanyRepository, Depends(get_company_repository)],
) -> CompanyOrchestrator:
    return CompanyOrchestrator(repository=repository)
