"""Execution strategy domain service for preparing how tasks should be executed."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import timedelta
from enum import StrEnum
from uuid import UUID, uuid4

from app.domain.department import DepartmentName
from app.domain.employee import Employee
from app.domain.task import Task, TaskPriority


class ExecutionMode(StrEnum):
    """How an agent should carry out a prepared execution plan."""

    DETERMINISTIC = "deterministic"
    LLM = "llm"
    HYBRID = "hybrid"
    MANUAL = "manual"


@dataclass(frozen=True, slots=True)
class ExecutionPlan:
    """Immutable blueprint describing how a task should be executed."""

    id: UUID
    task_id: UUID
    employee_id: UUID
    department: DepartmentName
    strategy_name: str
    execution_mode: ExecutionMode
    estimated_duration: timedelta
    requires_memory: bool
    requires_human_review: bool
    artifact_type: str

    def __post_init__(self) -> None:
        if not self.strategy_name.strip():
            msg = "Execution plan strategy name must not be empty."
            raise ValueError(msg)
        if not self.artifact_type.strip():
            msg = "Execution plan artifact type must not be empty."
            raise ValueError(msg)
        if self.estimated_duration <= timedelta(0):
            msg = "Execution plan estimated duration must be positive."
            raise ValueError(msg)

    @classmethod
    def create(
        cls,
        *,
        task: Task,
        employee_id: UUID,
        strategy_name: str,
        execution_mode: ExecutionMode,
        estimated_duration: timedelta,
        requires_memory: bool,
        requires_human_review: bool,
        artifact_type: str,
        plan_id: UUID | None = None,
    ) -> "ExecutionPlan":
        """Build an immutable execution plan from task and strategy metadata."""
        return cls(
            id=plan_id or uuid4(),
            task_id=task.id,
            employee_id=employee_id,
            department=task.department,
            strategy_name=strategy_name.strip(),
            execution_mode=execution_mode,
            estimated_duration=estimated_duration,
            requires_memory=requires_memory,
            requires_human_review=requires_human_review,
            artifact_type=artifact_type.strip(),
        )


class ExecutionStrategy(ABC):
    """Domain contract for preparing task execution without performing it."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Stable identifier for the strategy implementation."""

    @abstractmethod
    def prepare_execution(self, task: Task, employee: Employee) -> ExecutionPlan:
        """Return an immutable plan describing how the task should be executed."""


@dataclass(frozen=True, slots=True)
class DepartmentExecutionProfile:
    """Deterministic execution defaults for a department."""

    artifact_type: str
    base_duration: timedelta
    requires_memory: bool
    requires_human_review: bool


DEPARTMENT_EXECUTION_PROFILES: dict[DepartmentName, DepartmentExecutionProfile] = {
    DepartmentName.CEO: DepartmentExecutionProfile(
        artifact_type="strategic_brief",
        base_duration=timedelta(minutes=10),
        requires_memory=True,
        requires_human_review=True,
    ),
    DepartmentName.RESEARCH: DepartmentExecutionProfile(
        artifact_type="research_brief",
        base_duration=timedelta(minutes=20),
        requires_memory=True,
        requires_human_review=False,
    ),
    DepartmentName.BRAND: DepartmentExecutionProfile(
        artifact_type="brand_guidelines",
        base_duration=timedelta(minutes=30),
        requires_memory=True,
        requires_human_review=False,
    ),
    DepartmentName.SCRIPTS: DepartmentExecutionProfile(
        artifact_type="content_script",
        base_duration=timedelta(minutes=25),
        requires_memory=True,
        requires_human_review=False,
    ),
    DepartmentName.VIDEO: DepartmentExecutionProfile(
        artifact_type="video_asset",
        base_duration=timedelta(minutes=45),
        requires_memory=True,
        requires_human_review=True,
    ),
    DepartmentName.PUBLISHING: DepartmentExecutionProfile(
        artifact_type="publishing_package",
        base_duration=timedelta(minutes=15),
        requires_memory=True,
        requires_human_review=True,
    ),
    DepartmentName.GROWTH: DepartmentExecutionProfile(
        artifact_type="growth_report",
        base_duration=timedelta(minutes=20),
        requires_memory=True,
        requires_human_review=False,
    ),
}

PRIORITY_DURATION_MULTIPLIERS: dict[TaskPriority, float] = {
    TaskPriority.CRITICAL: 0.75,
    TaskPriority.HIGH: 0.875,
    TaskPriority.MEDIUM: 1.0,
    TaskPriority.LOW: 1.25,
}


@dataclass(frozen=True, slots=True)
class DeterministicExecutionStrategy(ExecutionStrategy):
    """Produces predictable execution plans without external provider calls."""

    @property
    def name(self) -> str:
        return "deterministic"

    def prepare_execution(self, task: Task, employee: Employee) -> ExecutionPlan:
        """Build a deterministic execution plan from task and employee context."""
        _validate_assignment(task, employee)

        profile = DEPARTMENT_EXECUTION_PROFILES[task.department]
        multiplier = PRIORITY_DURATION_MULTIPLIERS[task.priority]
        estimated_duration = timedelta(
            seconds=round(profile.base_duration.total_seconds() * multiplier)
        )

        return ExecutionPlan.create(
            task=task,
            employee_id=employee.id,
            strategy_name=self.name,
            execution_mode=ExecutionMode.DETERMINISTIC,
            estimated_duration=estimated_duration,
            requires_memory=profile.requires_memory,
            requires_human_review=profile.requires_human_review,
            artifact_type=profile.artifact_type,
        )


@dataclass(frozen=True, slots=True)
class FutureExecutionStrategyReference:
    """Placeholder describing a provider-backed strategy reserved for later."""

    name: str
    provider: str
    execution_mode: ExecutionMode

    def __post_init__(self) -> None:
        if not self.name.strip():
            msg = "Future execution strategy name must not be empty."
            raise ValueError(msg)
        if not self.provider.strip():
            msg = "Future execution strategy provider must not be empty."
            raise ValueError(msg)


FUTURE_EXECUTION_STRATEGIES: tuple[FutureExecutionStrategyReference, ...] = (
    FutureExecutionStrategyReference("openai", "OpenAI", ExecutionMode.LLM),
    FutureExecutionStrategyReference("claude", "Anthropic", ExecutionMode.LLM),
    FutureExecutionStrategyReference("gemini", "Google", ExecutionMode.LLM),
    FutureExecutionStrategyReference("local", "Local Model", ExecutionMode.LLM),
    FutureExecutionStrategyReference("hybrid", "Operator", ExecutionMode.HYBRID),
)


def _validate_assignment(task: Task, employee: Employee) -> None:
    if employee.department is not task.department:
        msg = (
            f"Employee {employee.id} belongs to {employee.department.value} "
            f"but task {task.id} belongs to {task.department.value}."
        )
        raise ValueError(msg)
    if task.is_terminal:
        msg = f"Task {task.id} is {task.status.value} and cannot be prepared for execution."
        raise ValueError(msg)


def estimated_duration_for(task: Task) -> timedelta:
    """Return the deterministic estimated duration for a task."""
    profile = DEPARTMENT_EXECUTION_PROFILES[task.department]
    multiplier = PRIORITY_DURATION_MULTIPLIERS[task.priority]
    return timedelta(seconds=round(profile.base_duration.total_seconds() * multiplier))
