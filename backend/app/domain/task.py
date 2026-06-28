"""Task domain model for units of work flowing between departments."""

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from app.domain.department import DepartmentName


class TaskStatus(StrEnum):
    """Lifecycle state of a single unit of work."""

    CREATED = "created"
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    WAITING_APPROVAL = "waiting_approval"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriority(StrEnum):
    """Relative urgency of a task within the workflow."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


TERMINAL_TASK_STATUSES: frozenset[TaskStatus] = frozenset(
    {TaskStatus.COMPLETED, TaskStatus.CANCELLED}
)

PRIORITY_ORDER: tuple[TaskPriority, ...] = (
    TaskPriority.CRITICAL,
    TaskPriority.HIGH,
    TaskPriority.MEDIUM,
    TaskPriority.LOW,
)


@dataclass(frozen=True, slots=True)
class Task:
    """A single unit of work assigned to a department within a workflow."""

    id: UUID
    title: str
    description: str
    created_at: datetime
    updated_at: datetime
    status: TaskStatus
    priority: TaskPriority
    department: DepartmentName
    assigned_employee: UUID | None
    depends_on: tuple[UUID, ...]
    result_reference: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "depends_on", tuple(self.depends_on))
        if not self.title.strip():
            msg = "Task title must not be empty."
            raise ValueError(msg)
        if not self.description.strip():
            msg = "Task description must not be empty."
            raise ValueError(msg)

    @classmethod
    def create(
        cls,
        *,
        title: str,
        description: str,
        department: DepartmentName,
        priority: TaskPriority = TaskPriority.MEDIUM,
        depends_on: tuple[UUID, ...] = (),
        assigned_employee: UUID | None = None,
        status: TaskStatus = TaskStatus.CREATED,
        result_reference: str = "",
        task_id: UUID | None = None,
        created_at: datetime | None = None,
    ) -> "Task":
        """Create a new task in the initial created state."""
        timestamp = created_at or datetime.now(UTC)
        return cls(
            id=task_id or uuid4(),
            title=title.strip(),
            description=description.strip(),
            created_at=timestamp,
            updated_at=timestamp,
            status=status,
            priority=priority,
            department=department,
            assigned_employee=assigned_employee,
            depends_on=depends_on,
            result_reference=result_reference,
        )

    @property
    def is_terminal(self) -> bool:
        return self.status in TERMINAL_TASK_STATUSES

    @property
    def is_completed(self) -> bool:
        return self.status is TaskStatus.COMPLETED

    def with_status(self, status: TaskStatus, updated_at: datetime) -> "Task":
        """Return a copy of the task with an updated status."""
        if self.is_terminal:
            msg = f"Task {self.id} is {self.status.value} and cannot be modified."
            raise ValueError(msg)
        return Task(
            id=self.id,
            title=self.title,
            description=self.description,
            created_at=self.created_at,
            updated_at=updated_at,
            status=status,
            priority=self.priority,
            department=self.department,
            assigned_employee=self.assigned_employee,
            depends_on=self.depends_on,
            result_reference=self.result_reference,
        )

    def with_assignment(self, employee_id: UUID, updated_at: datetime) -> "Task":
        """Return a copy of the task with an assigned employee."""
        if self.is_terminal:
            msg = f"Task {self.id} is {self.status.value} and cannot be assigned."
            raise ValueError(msg)
        return Task(
            id=self.id,
            title=self.title,
            description=self.description,
            created_at=self.created_at,
            updated_at=updated_at,
            status=self.status,
            priority=self.priority,
            department=self.department,
            assigned_employee=employee_id,
            depends_on=self.depends_on,
            result_reference=self.result_reference,
        )

    def with_completion(self, result_reference: str, updated_at: datetime) -> "Task":
        """Return a completed, immutable copy of the task."""
        if self.is_terminal:
            msg = f"Task {self.id} is already {self.status.value}."
            raise ValueError(msg)
        return Task(
            id=self.id,
            title=self.title,
            description=self.description,
            created_at=self.created_at,
            updated_at=updated_at,
            status=TaskStatus.COMPLETED,
            priority=self.priority,
            department=self.department,
            assigned_employee=self.assigned_employee,
            depends_on=self.depends_on,
            result_reference=result_reference.strip(),
        )
