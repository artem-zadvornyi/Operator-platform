"""Repository contracts for persisted company aggregates."""

from typing import Protocol
from uuid import UUID

from app.stores.company_session import CompanySession


class CompanyRepository(Protocol):
    """Persistence boundary for company creation sessions."""

    async def save(self, session: CompanySession) -> None:
        """Create or update a company session aggregate."""

    async def get(self, company_id: UUID) -> CompanySession | None:
        """Load a company session aggregate by identifier."""
