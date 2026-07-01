"""In-memory company session store."""

from uuid import UUID

from app.stores.company_session import CompanySession


class MemoryCompanyStore:
    """Process-local dictionary store for company sessions."""

    def __init__(self) -> None:
        self._sessions: dict[UUID, CompanySession] = {}

    def save(self, session: CompanySession) -> None:
        self._sessions[session.company_id] = session

    def get(self, company_id: UUID) -> CompanySession | None:
        return self._sessions.get(company_id)

    def clear(self) -> None:
        self._sessions.clear()
