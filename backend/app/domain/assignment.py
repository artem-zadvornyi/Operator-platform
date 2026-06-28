"""Assignment domain model linking employees to tasks."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True, slots=True)
class Assignment:
    """Records that a specific employee has been assigned a task."""

    employee: UUID
    task: UUID
    assigned_at: datetime
    accepted: bool

    def accept(self) -> "Assignment":
        """Return a copy of the assignment marked as accepted."""
        if self.accepted:
            msg = f"Assignment for task {self.task} is already accepted."
            raise ValueError(msg)
        return Assignment(
            employee=self.employee,
            task=self.task,
            assigned_at=self.assigned_at,
            accepted=True,
        )
