"""Plan domain model for operationalizing decisions into executable steps."""

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from app.domain.decision import Decision
from app.domain.department import DepartmentName
from app.domain.task import TaskPriority


class PlanStatus(StrEnum):
    """Lifecycle state of a plan derived from a decision."""

    DRAFT = "draft"
    READY = "ready"
    EXECUTING = "executing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass(frozen=True, slots=True)
class PlanStep:
    """A single departmental action within a plan.

    Designed for future conversion into workflow tasks via ``target_department``,
    ``priority``, and ``depends_on``.
    """

    id: UUID
    title: str
    description: str
    target_department: DepartmentName
    priority: TaskPriority
    depends_on: tuple[UUID, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "depends_on", tuple(self.depends_on))
        if not self.title.strip():
            msg = "Plan step title must not be empty."
            raise ValueError(msg)
        if not self.description.strip():
            msg = "Plan step description must not be empty."
            raise ValueError(msg)

    @classmethod
    def create(
        cls,
        *,
        title: str,
        description: str,
        target_department: DepartmentName,
        priority: TaskPriority = TaskPriority.MEDIUM,
        depends_on: tuple[UUID, ...] = (),
        step_id: UUID | None = None,
    ) -> "PlanStep":
        """Create a validated plan step."""
        return cls(
            id=step_id or uuid4(),
            title=title.strip(),
            description=description.strip(),
            target_department=target_department,
            priority=priority,
            depends_on=depends_on,
        )


@dataclass(frozen=True, slots=True)
class Plan:
    """An operational plan created from an approved strategic decision."""

    id: UUID
    decision_id: UUID
    title: str
    summary: str
    steps: tuple[PlanStep, ...]
    created_at: datetime
    status: PlanStatus

    def __post_init__(self) -> None:
        object.__setattr__(self, "steps", tuple(self.steps))
        if not self.title.strip():
            msg = "Plan title must not be empty."
            raise ValueError(msg)
        if not self.summary.strip():
            msg = "Plan summary must not be empty."
            raise ValueError(msg)
        self._validate_step_ids_unique()
        self.validate_step_dependencies()
        self._validate_ready_plan()

    @classmethod
    def create(
        cls,
        *,
        decision_id: UUID,
        title: str,
        summary: str,
        steps: tuple[PlanStep, ...] = (),
        status: PlanStatus = PlanStatus.DRAFT,
        plan_id: UUID | None = None,
        created_at: datetime | None = None,
    ) -> "Plan":
        """Create a plan linked to a single decision."""
        timestamp = created_at or datetime.now(UTC)
        return cls(
            id=plan_id or uuid4(),
            decision_id=decision_id,
            title=title.strip(),
            summary=summary.strip(),
            steps=steps,
            created_at=timestamp,
            status=status,
        )

    @classmethod
    def create_from_decision(
        cls,
        decision: Decision,
        *,
        title: str,
        summary: str,
        steps: tuple[PlanStep, ...] = (),
        status: PlanStatus = PlanStatus.DRAFT,
        plan_id: UUID | None = None,
        created_at: datetime | None = None,
    ) -> "Plan":
        """Create a plan explicitly derived from a decision."""
        return cls.create(
            decision_id=decision.id,
            title=title,
            summary=summary,
            steps=steps,
            status=status,
            plan_id=plan_id,
            created_at=created_at,
        )

    def add_step(self, step: PlanStep) -> "Plan":
        """Add a step to the plan after validating dependencies."""
        if self._has_step(step.id):
            msg = f"Plan step {step.id} already exists."
            raise ValueError(msg)

        proposed_steps = {existing.id: existing for existing in self.steps}
        proposed_steps[step.id] = step
        self._validate_dependency_graph(proposed_steps)

        return Plan(
            id=self.id,
            decision_id=self.decision_id,
            title=self.title,
            summary=self.summary,
            steps=(*self.steps, step),
            created_at=self.created_at,
            status=self.status,
        )

    def with_status(self, status: PlanStatus) -> "Plan":
        """Return a copy of the plan with an updated status."""
        return Plan(
            id=self.id,
            decision_id=self.decision_id,
            title=self.title,
            summary=self.summary,
            steps=self.steps,
            created_at=self.created_at,
            status=status,
        )

    def validate_step_dependencies(self) -> None:
        """Validate that every step dependency exists and the graph has no cycles."""
        self._validate_dependency_graph(self._step_map())

    def get_step(self, step_id: UUID) -> PlanStep:
        """Return a plan step by identifier."""
        step = self._step_map().get(step_id)
        if step is None:
            msg = f"Plan step {step_id} not found."
            raise KeyError(msg)
        return step

    def _step_map(self) -> dict[UUID, PlanStep]:
        return {step.id: step for step in self.steps}

    def _has_step(self, step_id: UUID) -> bool:
        return step_id in self._step_map()

    def _validate_step_ids_unique(self) -> None:
        step_ids = [step.id for step in self.steps]
        if len(step_ids) != len(set(step_ids)):
            msg = "Plan steps must have unique identifiers."
            raise ValueError(msg)

    def _validate_ready_plan(self) -> None:
        if self.status is PlanStatus.READY and not self.steps:
            msg = "A ready plan must contain at least one step."
            raise ValueError(msg)

    def _validate_dependency_graph(self, steps: Mapping[UUID, PlanStep]) -> None:
        for step in steps.values():
            for dependency_id in step.depends_on:
                if dependency_id not in steps:
                    msg = f"Plan step {step.id} depends on missing step {dependency_id}."
                    raise ValueError(msg)
                if dependency_id == step.id:
                    msg = f"Plan step {step.id} cannot depend on itself."
                    raise ValueError(msg)

        if _has_step_cycle(steps):
            msg = "Plan contains circular step dependencies."
            raise ValueError(msg)


def _has_step_cycle(steps: Mapping[UUID, PlanStep]) -> bool:
    visiting: set[UUID] = set()
    visited: set[UUID] = set()

    def visit(step_id: UUID) -> bool:
        if step_id in visiting:
            return True
        if step_id in visited:
            return False

        visiting.add(step_id)
        for dependency_id in steps[step_id].depends_on:
            if visit(dependency_id):
                return True
        visiting.remove(step_id)
        visited.add(step_id)
        return False

    return any(visit(step_id) for step_id in steps)
