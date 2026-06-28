from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from app.domain import (
    DepartmentName,
    Employee,
    EmployeeStatus,
    ExecutionMode,
    Task,
    TaskPriority,
    TaskStatus,
)
from app.domain.execution_strategy import (
    DEPARTMENT_EXECUTION_PROFILES,
    FUTURE_EXECUTION_STRATEGIES,
    DeterministicExecutionStrategy,
    ExecutionPlan,
    FutureExecutionStrategyReference,
    estimated_duration_for,
)


def _timestamp() -> datetime:
    return datetime(2026, 11, 1, 9, 0, tzinfo=UTC)


def _task(**overrides: object) -> Task:
    defaults: dict[str, object] = {
        "title": "Research niche",
        "description": "Validate audience demand and competitor landscape.",
        "department": DepartmentName.RESEARCH,
        "priority": TaskPriority.HIGH,
        "created_at": _timestamp(),
    }
    defaults.update(overrides)
    return Task.create(**defaults)


def _employee(**overrides: object) -> Employee:
    defaults: dict[str, object] = {
        "id": uuid4(),
        "name": "Research Analyst",
        "department": DepartmentName.RESEARCH,
        "role": "Audience Researcher",
        "status": EmployeeStatus.IDLE,
        "memory_reference": "memory://employees/research-analyst",
        "created_at": _timestamp(),
    }
    defaults.update(overrides)
    return Employee(**defaults)


def test_execution_plan_creation() -> None:
    task = _task()
    employee_id = uuid4()
    plan_id = uuid4()

    plan = ExecutionPlan.create(
        task=task,
        employee_id=employee_id,
        strategy_name="deterministic",
        execution_mode=ExecutionMode.DETERMINISTIC,
        estimated_duration=timedelta(minutes=20),
        requires_memory=True,
        requires_human_review=False,
        artifact_type="research_brief",
        plan_id=plan_id,
    )

    assert plan.id == plan_id
    assert plan.task_id == task.id
    assert plan.employee_id == employee_id
    assert plan.department is DepartmentName.RESEARCH
    assert plan.strategy_name == "deterministic"
    assert plan.execution_mode is ExecutionMode.DETERMINISTIC
    assert plan.estimated_duration == timedelta(minutes=20)
    assert plan.requires_memory is True
    assert plan.requires_human_review is False
    assert plan.artifact_type == "research_brief"


def test_execution_plan_rejects_invalid_fields() -> None:
    task = _task()
    employee_id = uuid4()

    with pytest.raises(ValueError, match="strategy name"):
        ExecutionPlan.create(
            task=task,
            employee_id=employee_id,
            strategy_name=" ",
            execution_mode=ExecutionMode.DETERMINISTIC,
            estimated_duration=timedelta(minutes=10),
            requires_memory=False,
            requires_human_review=False,
            artifact_type="research_brief",
        )

    with pytest.raises(ValueError, match="artifact type"):
        ExecutionPlan.create(
            task=task,
            employee_id=employee_id,
            strategy_name="deterministic",
            execution_mode=ExecutionMode.DETERMINISTIC,
            estimated_duration=timedelta(minutes=10),
            requires_memory=False,
            requires_human_review=False,
            artifact_type=" ",
        )

    with pytest.raises(ValueError, match="estimated duration"):
        ExecutionPlan.create(
            task=task,
            employee_id=employee_id,
            strategy_name="deterministic",
            execution_mode=ExecutionMode.DETERMINISTIC,
            estimated_duration=timedelta(0),
            requires_memory=False,
            requires_human_review=False,
            artifact_type="research_brief",
        )


def test_deterministic_strategy_produces_predictable_plan() -> None:
    strategy = DeterministicExecutionStrategy()
    task = _task(priority=TaskPriority.MEDIUM)
    employee = _employee(id=uuid4(), department=DepartmentName.RESEARCH)

    first_plan = strategy.prepare_execution(task, employee)
    second_plan = strategy.prepare_execution(task, employee)

    assert strategy.name == "deterministic"
    assert first_plan.strategy_name == "deterministic"
    assert first_plan.execution_mode is ExecutionMode.DETERMINISTIC
    assert first_plan.artifact_type == "research_brief"
    assert first_plan.estimated_duration == second_plan.estimated_duration
    assert first_plan.requires_memory == second_plan.requires_memory
    assert first_plan.requires_human_review == second_plan.requires_human_review


def test_deterministic_strategy_preserves_department_from_task() -> None:
    strategy = DeterministicExecutionStrategy()
    task = _task(department=DepartmentName.SCRIPTS)
    employee = _employee(department=DepartmentName.SCRIPTS, role="Script Writer")

    plan = strategy.prepare_execution(task, employee)

    assert plan.department is DepartmentName.SCRIPTS
    assert plan.artifact_type == DEPARTMENT_EXECUTION_PROFILES[DepartmentName.SCRIPTS].artifact_type


def test_deterministic_strategy_preserves_employee_id() -> None:
    strategy = DeterministicExecutionStrategy()
    employee_id = uuid4()
    task = _task()
    employee = _employee(id=employee_id)

    plan = strategy.prepare_execution(task, employee)

    assert plan.employee_id == employee_id
    assert plan.task_id == task.id


def test_deterministic_strategy_execution_mode_is_deterministic() -> None:
    strategy = DeterministicExecutionStrategy()
    task = _task(department=DepartmentName.BRAND)
    employee = _employee(department=DepartmentName.BRAND)

    plan = strategy.prepare_execution(task, employee)

    assert plan.execution_mode is ExecutionMode.DETERMINISTIC


def test_deterministic_strategy_estimated_duration_scales_with_priority() -> None:
    strategy = DeterministicExecutionStrategy()
    employee = _employee()

    medium_task = _task(priority=TaskPriority.MEDIUM)
    critical_task = _task(priority=TaskPriority.CRITICAL)

    medium_plan = strategy.prepare_execution(medium_task, employee)
    critical_plan = strategy.prepare_execution(critical_task, employee)

    assert medium_plan.estimated_duration == estimated_duration_for(medium_task)
    assert critical_plan.estimated_duration == estimated_duration_for(critical_task)
    assert critical_plan.estimated_duration < medium_plan.estimated_duration


def test_deterministic_strategy_human_review_flag_by_department() -> None:
    strategy = DeterministicExecutionStrategy()

    research_plan = strategy.prepare_execution(
        _task(department=DepartmentName.RESEARCH),
        _employee(department=DepartmentName.RESEARCH),
    )
    video_plan = strategy.prepare_execution(
        _task(department=DepartmentName.VIDEO),
        _employee(department=DepartmentName.VIDEO),
    )

    assert research_plan.requires_human_review is False
    assert video_plan.requires_human_review is True


def test_deterministic_strategy_artifact_type_by_department() -> None:
    strategy = DeterministicExecutionStrategy()

    for department, profile in DEPARTMENT_EXECUTION_PROFILES.items():
        plan = strategy.prepare_execution(
            _task(department=department),
            _employee(department=department),
        )
        assert plan.artifact_type == profile.artifact_type


def test_deterministic_strategy_rejects_department_mismatch() -> None:
    strategy = DeterministicExecutionStrategy()
    task = _task(department=DepartmentName.RESEARCH)
    employee = _employee(department=DepartmentName.BRAND)

    with pytest.raises(ValueError, match="belongs to"):
        strategy.prepare_execution(task, employee)


def test_deterministic_strategy_rejects_terminal_task() -> None:
    strategy = DeterministicExecutionStrategy()
    completed_task = Task.create(
        title="Completed task",
        description="Already finished.",
        department=DepartmentName.RESEARCH,
        status=TaskStatus.COMPLETED,
        created_at=_timestamp(),
    )
    employee = _employee()

    with pytest.raises(ValueError, match="cannot be prepared"):
        strategy.prepare_execution(completed_task, employee)


def test_future_execution_strategy_references() -> None:
    assert len(FUTURE_EXECUTION_STRATEGIES) == 5
    assert any(reference.name == "openai" for reference in FUTURE_EXECUTION_STRATEGIES)
    assert any(
        reference.execution_mode is ExecutionMode.HYBRID
        for reference in FUTURE_EXECUTION_STRATEGIES
    )

    with pytest.raises(ValueError, match="name must not be empty"):
        FutureExecutionStrategyReference(" ", "OpenAI", ExecutionMode.LLM)
