from datetime import UTC, datetime

import pytest

from app.domain import (
    Confidence,
    Decision,
    DecisionStatus,
    DepartmentName,
    Pipeline,
    RiskLevel,
    TaskPriority,
)


def _timestamp() -> datetime:
    return datetime(2026, 6, 1, 8, 0, tzinfo=UTC)


def _approved_decision(**overrides: object) -> Decision:
    defaults: dict[str, object] = {
        "title": "Launch finance education channel",
        "context": "Operator identified underserved personal finance audience on YouTube.",
        "rationale": "Audience demand and monetization potential align with company goals.",
        "confidence": Confidence.create(0.82),
        "risk_level": RiskLevel.MEDIUM,
        "expected_outcome": "A validated content niche with a 90-day publishing roadmap.",
        "status": DecisionStatus.APPROVED,
        "created_at": _timestamp(),
    }
    defaults.update(overrides)
    return Decision.create(**defaults)


def test_pipeline_builds_workflow_from_approved_decision() -> None:
    pipeline = Pipeline()
    decision = _approved_decision()

    workflow = pipeline.build(decision)

    assert len(workflow.tasks) == 6
    assert len({task.id for task in workflow.tasks}) == 6
    workflow.validate_dependencies()


def test_pipeline_preserves_department_order() -> None:
    pipeline = Pipeline()
    workflow = pipeline.build(_approved_decision())

    departments = [task.department for task in workflow.tasks]
    assert departments == [
        DepartmentName.RESEARCH,
        DepartmentName.BRAND,
        DepartmentName.SCRIPTS,
        DepartmentName.VIDEO,
        DepartmentName.PUBLISHING,
        DepartmentName.GROWTH,
    ]


def test_pipeline_preserves_dependency_chain() -> None:
    pipeline = Pipeline()
    workflow = pipeline.build(_approved_decision())

    assert workflow.tasks[0].depends_on == ()
    for index in range(1, len(workflow.tasks)):
        previous_task = workflow.tasks[index - 1]
        current_task = workflow.tasks[index]
        assert current_task.depends_on == (previous_task.id,)


def test_pipeline_preserves_priorities() -> None:
    pipeline = Pipeline()
    workflow = pipeline.build(_approved_decision())

    assert workflow.tasks[0].priority is TaskPriority.HIGH
    assert all(task.priority is TaskPriority.MEDIUM for task in workflow.tasks[1:])


def test_pipeline_maps_one_task_per_plan_step() -> None:
    pipeline = Pipeline()
    decision = _approved_decision()
    plan = pipeline.planner.create_plan(decision)
    workflow = pipeline._build_workflow_from_plan(plan)

    assert len(workflow.tasks) == len(plan.steps)
    for step, task in zip(plan.steps, workflow.tasks, strict=True):
        assert task.id == step.id
        assert task.title == step.title
        assert task.description == step.description
        assert task.depends_on == step.depends_on


def test_pipeline_rejects_rejected_decision() -> None:
    pipeline = Pipeline()
    decision = _approved_decision(status=DecisionStatus.REJECTED)

    with pytest.raises(ValueError, match="Only approved decisions"):
        pipeline.build(decision)


def test_pipeline_rejects_critical_risk_decision() -> None:
    pipeline = Pipeline()
    decision = _approved_decision(risk_level=RiskLevel.CRITICAL)

    with pytest.raises(ValueError, match="Critical risk decisions"):
        pipeline.build(decision)


def test_pipeline_next_available_tasks_starts_with_research() -> None:
    pipeline = Pipeline()
    workflow = pipeline.build(_approved_decision())

    available = workflow.next_available_tasks()
    assert len(available) == 1
    assert available[0].department is DepartmentName.RESEARCH
