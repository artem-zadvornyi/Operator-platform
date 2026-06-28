from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from app.domain import (
    Assignment,
    DepartmentName,
    Task,
    TaskPriority,
    TaskStatus,
    Workflow,
)


def _timestamp(offset_minutes: int = 0) -> datetime:
    return datetime(2026, 3, 1, 12, 0, tzinfo=UTC) + timedelta(minutes=offset_minutes)


def _task(
    *,
    title: str = "Research niche",
    department: DepartmentName = DepartmentName.RESEARCH,
    priority: TaskPriority = TaskPriority.MEDIUM,
    depends_on: tuple = (),
    created_at: datetime | None = None,
) -> Task:
    return Task.create(
        title=title,
        description=f"Complete {title.lower()}.",
        department=department,
        priority=priority,
        depends_on=depends_on,
        created_at=created_at or _timestamp(),
    )


def test_task_create_sets_defaults() -> None:
    created_at = _timestamp()
    task = _task(created_at=created_at)

    assert task.status is TaskStatus.CREATED
    assert task.priority is TaskPriority.MEDIUM
    assert task.assigned_employee is None
    assert task.result_reference == ""
    assert task.created_at == created_at
    assert task.updated_at == created_at


def test_task_rejects_empty_title() -> None:
    with pytest.raises(ValueError, match="title"):
        Task.create(
            title="   ",
            description="Valid description.",
            department=DepartmentName.BRAND,
        )


def test_completed_task_is_immutable() -> None:
    task = _task()
    completed = task.with_completion("research-brief-001", _timestamp(1))

    assert completed.is_completed
    assert completed.is_terminal

    with pytest.raises(ValueError, match="cannot be modified"):
        completed.with_status(TaskStatus.IN_PROGRESS, _timestamp(2))


def test_workflow_create_starts_empty() -> None:
    workflow = Workflow.create(created_at=_timestamp())

    assert workflow.tasks == ()
    assert workflow.assignments == ()
    assert workflow.next_available_tasks() == ()


def test_workflow_add_task() -> None:
    workflow = Workflow.create(created_at=_timestamp())
    task = _task()

    updated = workflow.add_task(task)

    assert len(updated.tasks) == 1
    assert updated.get_task(task.id).title == task.title


def test_workflow_rejects_duplicate_task_ids() -> None:
    task_id = uuid4()
    task = Task.create(
        title="Define strategy",
        description="Set company direction.",
        department=DepartmentName.CEO,
        task_id=task_id,
        created_at=_timestamp(),
    )
    workflow = Workflow.create(created_at=_timestamp()).add_task(task)

    duplicate = Task.create(
        title="Duplicate",
        description="Should fail.",
        department=DepartmentName.CEO,
        task_id=task_id,
        created_at=_timestamp(1),
    )

    with pytest.raises(ValueError, match="already exists"):
        workflow.add_task(duplicate)


def test_workflow_rejects_missing_dependency() -> None:
    workflow = Workflow.create(created_at=_timestamp())
    missing_dependency = uuid4()
    dependent_task = _task(depends_on=(missing_dependency,))

    with pytest.raises(ValueError, match="depends on missing task"):
        workflow.add_task(dependent_task)


def test_workflow_rejects_self_dependency() -> None:
    task_id = uuid4()
    task = Task.create(
        title="Self dependent",
        description="Invalid dependency.",
        department=DepartmentName.SCRIPTS,
        task_id=task_id,
        depends_on=(task_id,),
        created_at=_timestamp(),
    )
    workflow = Workflow.create(created_at=_timestamp())

    with pytest.raises(ValueError, match="cannot depend on itself"):
        workflow.add_task(task)


def test_workflow_rejects_circular_dependencies() -> None:
    task_a_id = uuid4()
    task_b_id = uuid4()
    task_a = Task.create(
        title="Task A",
        description="Depends on B.",
        department=DepartmentName.BRAND,
        task_id=task_a_id,
        depends_on=(task_b_id,),
        created_at=_timestamp(),
    )
    task_b = Task.create(
        title="Task B",
        description="Depends on A.",
        department=DepartmentName.BRAND,
        task_id=task_b_id,
        depends_on=(task_a_id,),
        created_at=_timestamp(1),
    )

    with pytest.raises(ValueError, match="circular"):
        Workflow(
            id=uuid4(),
            tasks=(task_a, task_b),
            assignments=(),
            created_at=_timestamp(),
        )


def test_workflow_rejects_cycle_when_adding_dependent_task() -> None:
    workflow = Workflow.create(created_at=_timestamp())
    task_a = _task(title="Research")
    task_b = Task.create(
        title="Brand",
        description="Depends on research.",
        department=DepartmentName.BRAND,
        depends_on=(task_a.id,),
        created_at=_timestamp(1),
    )
    workflow = workflow.add_task(task_a).add_task(task_b)

    task_c = Task.create(
        title="Scripts",
        description="Depends on brand.",
        department=DepartmentName.SCRIPTS,
        depends_on=(task_b.id,),
        created_at=_timestamp(2),
    )
    workflow = workflow.add_task(task_c)

    cyclic_task = Task.create(
        title="Cycle",
        description="Depends on scripts and closes the loop to research.",
        department=DepartmentName.GROWTH,
        depends_on=(task_c.id, task_a.id),
        created_at=_timestamp(3),
    )
    workflow = workflow.add_task(cyclic_task)

    research_with_cycle = Task.create(
        title="Research",
        description="Now depends on cycle task.",
        department=DepartmentName.RESEARCH,
        task_id=task_a.id,
        depends_on=(cyclic_task.id,),
        created_at=_timestamp(4),
    )

    with pytest.raises(ValueError, match="already exists"):
        workflow.add_task(research_with_cycle)


def test_next_available_tasks_respects_dependencies() -> None:
    workflow = Workflow.create(created_at=_timestamp())
    research = _task(title="Research niche", priority=TaskPriority.HIGH)
    brand = Task.create(
        title="Create brand",
        description="Build visual identity.",
        department=DepartmentName.BRAND,
        depends_on=(research.id,),
        created_at=_timestamp(1),
    )

    workflow = workflow.add_task(research).add_task(brand)

    available = workflow.next_available_tasks()
    assert [task.id for task in available] == [research.id]

    workflow = workflow.complete_task(research.id, "brief-001", _timestamp(2))
    available = workflow.next_available_tasks()

    assert [task.id for task in available] == [brand.id]


def test_next_available_tasks_orders_by_priority() -> None:
    workflow = Workflow.create(created_at=_timestamp())
    low = _task(title="Low priority", priority=TaskPriority.LOW)
    critical = _task(title="Critical path", priority=TaskPriority.CRITICAL)
    medium = _task(title="Medium priority", priority=TaskPriority.MEDIUM)

    workflow = workflow.add_task(low).add_task(critical).add_task(medium)
    available = workflow.next_available_tasks()

    assert [task.priority for task in available] == [
        TaskPriority.CRITICAL,
        TaskPriority.MEDIUM,
        TaskPriority.LOW,
    ]


def test_complete_task_marks_task_immutable() -> None:
    workflow = Workflow.create(created_at=_timestamp())
    task = _task()
    workflow = workflow.add_task(task)

    completed_at = _timestamp(1)
    workflow = workflow.complete_task(task.id, "output-001", completed_at)
    completed = workflow.get_task(task.id)

    assert completed.status is TaskStatus.COMPLETED
    assert completed.result_reference == "output-001"
    assert completed.updated_at == completed_at

    with pytest.raises(ValueError, match="already completed"):
        completed.with_completion("output-002", _timestamp(2))


def test_complete_task_requires_dependencies() -> None:
    workflow = Workflow.create(created_at=_timestamp())
    research = _task(title="Research")
    brand = Task.create(
        title="Brand",
        description="Depends on research.",
        department=DepartmentName.BRAND,
        depends_on=(research.id,),
        created_at=_timestamp(1),
    )
    workflow = workflow.add_task(research).add_task(brand)

    with pytest.raises(ValueError, match="cannot complete until dependencies"):
        workflow.complete_task(brand.id, "brand-kit", _timestamp(2))


def test_workflow_assignment_updates_task_and_records_history() -> None:
    workflow = Workflow.create(created_at=_timestamp())
    employee_id = uuid4()
    task = _task()
    workflow = workflow.add_task(task)

    assigned_at = _timestamp(1)
    workflow = workflow.assign_task(employee_id, task.id, assigned_at)

    updated_task = workflow.get_task(task.id)
    assert updated_task.assigned_employee == employee_id
    assert len(workflow.assignments) == 1

    assignment = workflow.assignments[0]
    assert isinstance(assignment, Assignment)
    assert assignment.employee == employee_id
    assert assignment.task == task.id
    assert assignment.assigned_at == assigned_at
    assert assignment.accepted is False


def test_assignment_acceptance() -> None:
    assignment = Assignment(
        employee=uuid4(),
        task=uuid4(),
        assigned_at=_timestamp(),
        accepted=False,
    )

    accepted = assignment.accept()
    assert accepted.accepted is True

    with pytest.raises(ValueError, match="already accepted"):
        accepted.accept()


def test_workflow_progression_across_department_chain() -> None:
    workflow = Workflow.create(created_at=_timestamp())
    research = _task(title="Research", department=DepartmentName.RESEARCH)
    brand = Task.create(
        title="Brand",
        description="Create identity.",
        department=DepartmentName.BRAND,
        depends_on=(research.id,),
        created_at=_timestamp(1),
    )
    scripts = Task.create(
        title="Scripts",
        description="Write first scripts.",
        department=DepartmentName.SCRIPTS,
        depends_on=(brand.id,),
        created_at=_timestamp(2),
    )

    workflow = workflow.add_task(research).add_task(brand).add_task(scripts)

    assert len(workflow.next_available_tasks()) == 1

    workflow = workflow.complete_task(research.id, "research-brief", _timestamp(3))
    assert len(workflow.next_available_tasks()) == 1
    assert workflow.next_available_tasks()[0].id == brand.id

    workflow = workflow.complete_task(brand.id, "brand-kit", _timestamp(4))
    assert workflow.next_available_tasks()[0].id == scripts.id

    workflow = workflow.complete_task(scripts.id, "script-pack", _timestamp(5))
    assert workflow.next_available_tasks() == ()
    assert all(task.is_completed for task in workflow.tasks)


def test_validate_dependencies_on_existing_workflow() -> None:
    workflow = Workflow.create(created_at=_timestamp())
    first = _task(title="First")
    second = Task.create(
        title="Second",
        description="Depends on first.",
        department=DepartmentName.VIDEO,
        depends_on=(first.id,),
        created_at=_timestamp(1),
    )
    workflow = workflow.add_task(first).add_task(second)

    workflow.validate_dependencies()
