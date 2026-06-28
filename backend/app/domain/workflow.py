"""Workflow domain model for orchestrating tasks across departments."""

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.domain.assignment import Assignment
from app.domain.task import PRIORITY_ORDER, Task, TaskStatus


@dataclass(frozen=True, slots=True)
class Workflow:
    """Ordered execution graph of tasks flowing between AI departments."""

    id: UUID
    tasks: tuple[Task, ...]
    assignments: tuple[Assignment, ...]
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "tasks", tuple(self.tasks))
        object.__setattr__(self, "assignments", tuple(self.assignments))
        self._validate_task_ids_unique()
        self.validate_dependencies()

    @classmethod
    def create(
        cls,
        *,
        workflow_id: UUID | None = None,
        created_at: datetime | None = None,
    ) -> "Workflow":
        """Create an empty workflow ready to accept tasks."""
        timestamp = created_at or datetime.now(UTC)
        return cls(
            id=workflow_id or uuid4(),
            tasks=(),
            assignments=(),
            created_at=timestamp,
        )

    def add_task(self, task: Task) -> "Workflow":
        """Add a task to the workflow after validating dependencies."""
        if self._has_task(task.id):
            msg = f"Task {task.id} already exists in workflow."
            raise ValueError(msg)

        proposed_tasks = {existing.id: existing for existing in self.tasks}
        proposed_tasks[task.id] = task
        self._validate_dependency_graph(proposed_tasks)

        return Workflow(
            id=self.id,
            tasks=(*self.tasks, task),
            assignments=self.assignments,
            created_at=self.created_at,
        )

    def assign_task(
        self,
        employee_id: UUID,
        task_id: UUID,
        assigned_at: datetime,
        *,
        accepted: bool = False,
    ) -> "Workflow":
        """Assign an employee to a task and record the assignment."""
        task = self._get_task(task_id)
        assignment = Assignment(
            employee=employee_id,
            task=task_id,
            assigned_at=assigned_at,
            accepted=accepted,
        )
        updated_task = task.with_assignment(employee_id, assigned_at)

        return Workflow(
            id=self.id,
            tasks=self._replace_task(updated_task),
            assignments=(*self.assignments, assignment),
            created_at=self.created_at,
        )

    def complete_task(
        self,
        task_id: UUID,
        result_reference: str,
        updated_at: datetime,
    ) -> "Workflow":
        """Mark a task completed once all dependencies are satisfied."""
        task = self._get_task(task_id)
        self._ensure_dependencies_completed(task)

        completed_task = task.with_completion(result_reference, updated_at)
        return Workflow(
            id=self.id,
            tasks=self._replace_task(completed_task),
            assignments=self.assignments,
            created_at=self.created_at,
        )

    def next_available_tasks(self) -> tuple[Task, ...]:
        """Return tasks ready to start, ordered by priority."""
        task_map = self._task_map()
        available = [
            task
            for task in self.tasks
            if task.status in {TaskStatus.CREATED, TaskStatus.QUEUED}
            and self._dependencies_completed(task, task_map)
        ]
        return tuple(sorted(available, key=self._priority_sort_key))

    def validate_dependencies(self) -> None:
        """Validate that every dependency exists and the graph has no cycles."""
        self._validate_dependency_graph(self._task_map())

    def get_task(self, task_id: UUID) -> Task:
        """Return a task by identifier."""
        return self._get_task(task_id)

    def _task_map(self) -> dict[UUID, Task]:
        return {task.id: task for task in self.tasks}

    def _has_task(self, task_id: UUID) -> bool:
        return task_id in self._task_map()

    def _get_task(self, task_id: UUID) -> Task:
        task = self._task_map().get(task_id)
        if task is None:
            msg = f"Task {task_id} not found in workflow."
            raise KeyError(msg)
        return task

    def _replace_task(self, updated_task: Task) -> tuple[Task, ...]:
        return tuple(updated_task if task.id == updated_task.id else task for task in self.tasks)

    def _validate_task_ids_unique(self) -> None:
        task_ids = [task.id for task in self.tasks]
        if len(task_ids) != len(set(task_ids)):
            msg = "Workflow tasks must have unique identifiers."
            raise ValueError(msg)

    def _validate_dependency_graph(self, tasks: Mapping[UUID, Task]) -> None:
        for task in tasks.values():
            for dependency_id in task.depends_on:
                if dependency_id not in tasks:
                    msg = f"Task {task.id} depends on missing task {dependency_id}."
                    raise ValueError(msg)
                if dependency_id == task.id:
                    msg = f"Task {task.id} cannot depend on itself."
                    raise ValueError(msg)

        if _has_cycle(tasks):
            msg = "Workflow contains circular task dependencies."
            raise ValueError(msg)

    def _dependencies_completed(
        self,
        task: Task,
        task_map: Mapping[UUID, Task],
    ) -> bool:
        return all(task_map[dependency_id].is_completed for dependency_id in task.depends_on)

    def _ensure_dependencies_completed(self, task: Task) -> None:
        task_map = self._task_map()
        incomplete = [
            dependency_id
            for dependency_id in task.depends_on
            if not task_map[dependency_id].is_completed
        ]
        if incomplete:
            msg = (
                f"Task {task.id} cannot complete until dependencies are finished: "
                f"{', '.join(str(dep) for dep in incomplete)}"
            )
            raise ValueError(msg)

    @staticmethod
    def _priority_sort_key(task: Task) -> int:
        return PRIORITY_ORDER.index(task.priority)


def _has_cycle(tasks: Mapping[UUID, Task]) -> bool:
    visiting: set[UUID] = set()
    visited: set[UUID] = set()

    def visit(task_id: UUID) -> bool:
        if task_id in visiting:
            return True
        if task_id in visited:
            return False

        visiting.add(task_id)
        for dependency_id in tasks[task_id].depends_on:
            if visit(dependency_id):
                return True
        visiting.remove(task_id)
        visited.add(task_id)
        return False

    return any(visit(task_id) for task_id in tasks)
