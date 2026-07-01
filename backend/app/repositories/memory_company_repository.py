"""In-memory repository used for fast tests and local fallback."""

from uuid import UUID

from app.stores.company_session import CompanySession
from app.stores.memory_company_store import MemoryCompanyStore


class MemoryCompanyRepository:
    """Adapter that exposes the legacy in-memory store through the repository API."""

    def __init__(self, store: MemoryCompanyStore | None = None) -> None:
        self._store = store or MemoryCompanyStore()

    async def save(self, session: CompanySession) -> None:
        self._store.save(session)

    async def get(self, company_id: UUID) -> CompanySession | None:
        return self._store.get(company_id)

    def clear(self) -> None:
        self._store.clear()
