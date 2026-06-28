"""Agent runtime domain model for AI employee task execution lifecycle."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from app.domain.department import DepartmentName
from app.domain.task import Task


class ExecutionStatus(StrEnum):
    """Lifecycle state of a single agent task execution."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


TERMINAL_EXECUTION_STATUSES: frozenset[ExecutionStatus] = frozenset(
    {ExecutionStatus.SUCCEEDED, ExecutionStatus.FAILED, ExecutionStatus.CANCELLED}
)


@dataclass(frozen=True, slots=True)
class ExecutionFailure:
    """Describes why an agent execution failed or was cancelled."""

    reason: str
    recoverable: bool
    created_at: datetime

    def __post_init__(self) -> None:
        if not self.reason.strip():
            msg = "Execution failure reason must not be empty."
            raise ValueError(msg)


@dataclass(frozen=True, slots=True)
class ExecutionResult:
    """Deterministic metadata describing a successful agent execution output."""

    id: UUID
    task_id: UUID
    employee_id: UUID
    title: str
    summary: str
    artifact_reference: str
    created_at: datetime

    def __post_init__(self) -> None:
        if not self.title.strip():
            msg = "Execution result title must not be empty."
            raise ValueError(msg)
        if not self.summary.strip():
            msg = "Execution result summary must not be empty."
            raise ValueError(msg)


@dataclass(frozen=True, slots=True)
class AgentExecution:
    """Represents one employee executing one workflow task."""

    id: UUID
    task_id: UUID
    employee_id: UUID
    department: DepartmentName
    status: ExecutionStatus
    started_at: datetime | None
    finished_at: datetime | None
    result: ExecutionResult | None
    failure: ExecutionFailure | None

    def __post_init__(self) -> None:
        self._validate_state()

    @classmethod
    def create(
        cls,
        task: Task,
        employee_id: UUID,
        *,
        execution_id: UUID | None = None,
    ) -> "AgentExecution":
        """Create a pending execution for an employee and task."""
        return cls(
            id=execution_id or uuid4(),
            task_id=task.id,
            employee_id=employee_id,
            department=task.department,
            status=ExecutionStatus.PENDING,
            started_at=None,
            finished_at=None,
            result=None,
            failure=None,
        )

    def start(self, started_at: datetime) -> "AgentExecution":
        """Transition a pending execution into the running state."""
        self._ensure_status(ExecutionStatus.PENDING, "start")

        return AgentExecution(
            id=self.id,
            task_id=self.task_id,
            employee_id=self.employee_id,
            department=self.department,
            status=ExecutionStatus.RUNNING,
            started_at=started_at,
            finished_at=None,
            result=None,
            failure=None,
        )

    def succeed(
        self,
        title: str,
        summary: str,
        finished_at: datetime,
        *,
        artifact_reference: str | None = None,
    ) -> "AgentExecution":
        """Mark a running execution as succeeded with deterministic result metadata."""
        self._ensure_status(ExecutionStatus.RUNNING, "complete successfully")

        result = ExecutionResult(
            id=uuid4(),
            task_id=self.task_id,
            employee_id=self.employee_id,
            title=title.strip(),
            summary=summary.strip(),
            artifact_reference=artifact_reference
            or _default_artifact_reference(self.task_id, self.id),
            created_at=finished_at,
        )

        return AgentExecution(
            id=self.id,
            task_id=self.task_id,
            employee_id=self.employee_id,
            department=self.department,
            status=ExecutionStatus.SUCCEEDED,
            started_at=self.started_at,
            finished_at=finished_at,
            result=result,
            failure=None,
        )

    def fail(
        self,
        reason: str,
        finished_at: datetime,
        *,
        recoverable: bool = True,
    ) -> "AgentExecution":
        """Mark a running execution as failed."""
        self._ensure_status(ExecutionStatus.RUNNING, "fail")

        failure = ExecutionFailure(
            reason=reason.strip(),
            recoverable=recoverable,
            created_at=finished_at,
        )

        return AgentExecution(
            id=self.id,
            task_id=self.task_id,
            employee_id=self.employee_id,
            department=self.department,
            status=ExecutionStatus.FAILED,
            started_at=self.started_at,
            finished_at=finished_at,
            result=None,
            failure=failure,
        )

    def cancel(self, reason: str, finished_at: datetime) -> "AgentExecution":
        """Cancel a pending or running execution."""
        if self.status not in {ExecutionStatus.PENDING, ExecutionStatus.RUNNING}:
            msg = f"Execution {self.id} cannot be cancelled from {self.status.value}."
            raise ValueError(msg)

        failure = ExecutionFailure(
            reason=reason.strip(),
            recoverable=False,
            created_at=finished_at,
        )

        return AgentExecution(
            id=self.id,
            task_id=self.task_id,
            employee_id=self.employee_id,
            department=self.department,
            status=ExecutionStatus.CANCELLED,
            started_at=self.started_at,
            finished_at=finished_at,
            result=None,
            failure=failure,
        )

    @property
    def is_terminal(self) -> bool:
        return self.status in TERMINAL_EXECUTION_STATUSES

    def _ensure_status(self, required: ExecutionStatus, action: str) -> None:
        if self.is_terminal:
            msg = f"Execution {self.id} is {self.status.value} and cannot be modified."
            raise ValueError(msg)
        if self.status is not required:
            msg = f"Execution {self.id} cannot {action} from {self.status.value}."
            raise ValueError(msg)

    def _validate_state(self) -> None:
        if self.status is ExecutionStatus.PENDING:
            if self.started_at is not None or self.finished_at is not None:
                msg = "Pending execution cannot have start or finish timestamps."
                raise ValueError(msg)
            if self.result is not None or self.failure is not None:
                msg = "Pending execution cannot have result or failure."
                raise ValueError(msg)

        if self.status is ExecutionStatus.RUNNING:
            if self.started_at is None:
                msg = "Running execution must have a start timestamp."
                raise ValueError(msg)
            if self.finished_at is not None:
                msg = "Running execution cannot have a finish timestamp."
                raise ValueError(msg)
            if self.result is not None or self.failure is not None:
                msg = "Running execution cannot have result or failure."
                raise ValueError(msg)

        if self.status is ExecutionStatus.SUCCEEDED:
            if self.result is None:
                msg = "Succeeded execution must have a result."
                raise ValueError(msg)
            if self.failure is not None:
                msg = "Succeeded execution cannot have a failure."
                raise ValueError(msg)
            if self.started_at is None or self.finished_at is None:
                msg = "Succeeded execution must have start and finish timestamps."
                raise ValueError(msg)

        if self.status is ExecutionStatus.FAILED:
            if self.failure is None:
                msg = "Failed execution must have a failure."
                raise ValueError(msg)
            if self.result is not None:
                msg = "Failed execution cannot have a result."
                raise ValueError(msg)
            if self.started_at is None or self.finished_at is None:
                msg = "Failed execution must have start and finish timestamps."
                raise ValueError(msg)

        if self.status is ExecutionStatus.CANCELLED:
            if self.failure is None:
                msg = "Cancelled execution must have a failure reason."
                raise ValueError(msg)
            if self.result is not None:
                msg = "Cancelled execution cannot have a result."
                raise ValueError(msg)
            if self.finished_at is None:
                msg = "Cancelled execution must have a finish timestamp."
                raise ValueError(msg)


def _default_artifact_reference(task_id: UUID, execution_id: UUID) -> str:
    return f"artifact://tasks/{task_id}/executions/{execution_id}"
