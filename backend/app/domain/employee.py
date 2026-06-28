"""Employee domain model for AI workers inside a company blueprint."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from app.domain.department import DepartmentName


class EmployeeStatus(StrEnum):
    """Operational state of an individual AI employee."""

    IDLE = "idle"
    WORKING = "working"
    WAITING_FOR_APPROVAL = "waiting_for_approval"
    COMPLETE = "complete"


@dataclass(frozen=True, slots=True)
class Employee:
    """An AI employee assigned to a single department within a company blueprint."""

    id: UUID
    name: str
    department: DepartmentName
    role: str
    status: EmployeeStatus
    memory_reference: str
    created_at: datetime

    def __post_init__(self) -> None:
        if not self.name.strip():
            msg = "Employee name must not be empty."
            raise ValueError(msg)
        if not self.role.strip():
            msg = "Employee role must not be empty."
            raise ValueError(msg)
