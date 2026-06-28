from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from app.domain import (
    AgentExecution,
    DepartmentName,
    ExecutionStatus,
    Task,
    TaskPriority,
)


def _timestamp(offset_minutes: int = 0) -> datetime:
    return datetime(2026, 10, 1, 8, 0, tzinfo=UTC) + timedelta(minutes=offset_minutes)


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


def _execution(**overrides: object) -> AgentExecution:
    employee_id = uuid4()
    task = _task()
    execution = AgentExecution.create(task, employee_id)
    defaults: dict[str, object] = {"execution": execution}
    defaults.update(overrides)
    return defaults.get("execution", execution)


def test_execution_create_starts_pending() -> None:
    employee_id = uuid4()
    task = _task(department=DepartmentName.BRAND)
    execution = AgentExecution.create(task, employee_id)

    assert execution.status is ExecutionStatus.PENDING
    assert execution.task_id == task.id
    assert execution.employee_id == employee_id
    assert execution.department is DepartmentName.BRAND
    assert execution.started_at is None
    assert execution.result is None
    assert execution.failure is None


def test_execution_start_lifecycle() -> None:
    execution = _execution()
    running = execution.start(_timestamp(1))

    assert running.status is ExecutionStatus.RUNNING
    assert running.started_at == _timestamp(1)


def test_execution_success_lifecycle() -> None:
    execution = _execution().start(_timestamp(1))
    succeeded = execution.succeed(
        "Research brief complete",
        "Validated finance beginner audience on YouTube.",
        _timestamp(2),
    )

    assert succeeded.status is ExecutionStatus.SUCCEEDED
    assert succeeded.result is not None
    assert succeeded.result.title == "Research brief complete"
    assert succeeded.result.summary == "Validated finance beginner audience on YouTube."
    assert succeeded.result.task_id == execution.task_id
    assert succeeded.result.employee_id == execution.employee_id
    assert succeeded.result.artifact_reference.startswith("artifact://tasks/")
    assert succeeded.failure is None


def test_execution_failure_lifecycle() -> None:
    execution = _execution().start(_timestamp(1))
    failed = execution.fail("Source data unavailable", _timestamp(2), recoverable=True)

    assert failed.status is ExecutionStatus.FAILED
    assert failed.failure is not None
    assert failed.failure.reason == "Source data unavailable"
    assert failed.failure.recoverable is True
    assert failed.result is None


def test_execution_cancel_lifecycle() -> None:
    execution = _execution()
    cancelled = execution.cancel("Superseded by higher priority task", _timestamp(1))

    assert cancelled.status is ExecutionStatus.CANCELLED
    assert cancelled.failure is not None
    assert cancelled.failure.reason == "Superseded by higher priority task"
    assert cancelled.failure.recoverable is False


def test_execution_cancel_from_running() -> None:
    execution = _execution().start(_timestamp(1))
    cancelled = execution.cancel("Operator halted workflow", _timestamp(2))

    assert cancelled.status is ExecutionStatus.CANCELLED
    assert cancelled.started_at == _timestamp(1)


def test_execution_rejects_invalid_start_transition() -> None:
    execution = _execution().start(_timestamp(1))

    with pytest.raises(ValueError, match="cannot start"):
        execution.start(_timestamp(2))


def test_execution_rejects_success_from_pending() -> None:
    execution = _execution()

    with pytest.raises(ValueError, match="cannot complete successfully"):
        execution.succeed("Too early", "Should fail.", _timestamp(1))


def test_execution_rejects_failure_from_pending() -> None:
    execution = _execution()

    with pytest.raises(ValueError, match="cannot fail"):
        execution.fail("Too early", _timestamp(1))


def test_terminal_execution_is_immutable() -> None:
    execution = _execution().start(_timestamp(1)).succeed("Done", "Completed.", _timestamp(2))

    with pytest.raises(ValueError, match="cannot be modified"):
        execution.start(_timestamp(3))

    with pytest.raises(ValueError, match="cannot be modified"):
        execution.succeed("Again", "Nope.", _timestamp(3))

    with pytest.raises(ValueError, match="cannot be modified"):
        execution.fail("Nope", _timestamp(3))


def test_execution_preserves_department_from_task() -> None:
    task = _task(department=DepartmentName.SCRIPTS)
    execution = AgentExecution.create(task, uuid4())

    assert execution.department is DepartmentName.SCRIPTS


def test_execution_result_rejects_empty_fields() -> None:
    execution = _execution().start(_timestamp(1))

    with pytest.raises(ValueError, match="title"):
        execution.succeed("   ", "Valid summary.", _timestamp(2))

    with pytest.raises(ValueError, match="summary"):
        execution.succeed("Valid title", "   ", _timestamp(2))


def test_execution_failure_rejects_empty_reason() -> None:
    execution = _execution().start(_timestamp(1))

    with pytest.raises(ValueError, match="reason"):
        execution.fail("   ", _timestamp(2))
