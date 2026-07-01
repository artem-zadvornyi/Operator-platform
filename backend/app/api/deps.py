from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.company_orchestrator import CompanyOrchestrator
from app.db.session import async_session_factory
from app.stores.memory_company_store import MemoryCompanyStore

_company_store = MemoryCompanyStore()
_company_orchestrator = CompanyOrchestrator(store=_company_store)


def get_company_store() -> MemoryCompanyStore:
    return _company_store


def get_company_orchestrator() -> CompanyOrchestrator:
    return _company_orchestrator


async def get_db_session() -> AsyncIterator[AsyncSession]:
    async with async_session_factory() as session:
        yield session
