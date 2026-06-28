from datetime import UTC, datetime
from uuid import uuid4

import pytest

from app.domain import (
    Confidence,
    Decision,
    DecisionStatus,
    DepartmentName,
    Plan,
    PlanStatus,
    PlanStep,
    RiskLevel,
    TaskPriority,
)


def _timestamp() -> datetime:
    return datetime(2026, 4, 1, 10, 0, tzinfo=UTC)


def _decision(**overrides: object) -> Decision:
    defaults: dict[str, object] = {
        "title": "Launch finance education channel",
        "context": "Operator identified underserved personal finance audience on YouTube.",
        "rationale": "Audience demand and monetization potential align with company goals.",
        "confidence": Confidence.create(0.82),
        "risk_level": RiskLevel.MEDIUM,
        "expected_outcome": "A validated content niche with a 90-day publishing roadmap.",
        "created_at": _timestamp(),
    }
    defaults.update(overrides)
    return Decision.create(**defaults)


def test_decision_create_sets_defaults() -> None:
    decision = _decision()

    assert decision.status is DecisionStatus.PROPOSED
    assert decision.title == "Launch finance education channel"
    assert decision.confidence.is_high


def test_decision_rejects_empty_fields() -> None:
    with pytest.raises(ValueError, match="title"):
        _decision(title="   ")

    with pytest.raises(ValueError, match="context"):
        _decision(context="   ")

    with pytest.raises(ValueError, match="rationale"):
        _decision(rationale="   ")

    with pytest.raises(ValueError, match="expected outcome"):
        _decision(expected_outcome="   ")


def test_decision_status_transition() -> None:
    decision = _decision().with_status(DecisionStatus.APPROVED)
    assert decision.status is DecisionStatus.APPROVED


def test_confidence_validation_rejects_out_of_range() -> None:
    with pytest.raises(ValueError, match="between 0.0 and 1.0"):
        Confidence.create(-0.1)

    with pytest.raises(ValueError, match="between 0.0 and 1.0"):
        Confidence.create(1.1)


def test_confidence_helpers() -> None:
    assert Confidence.create(0.2).is_low is True
    assert Confidence.create(0.2).is_medium is False
    assert Confidence.create(0.2).is_high is False

    assert Confidence.create(0.55).is_low is False
    assert Confidence.create(0.55).is_medium is True
    assert Confidence.create(0.55).is_high is False

    assert Confidence.create(0.85).is_low is False
    assert Confidence.create(0.85).is_medium is False
    assert Confidence.create(0.85).is_high is True


def test_confidence_boundary_values_are_valid() -> None:
    assert Confidence.create(0.0).value == 0.0
    assert Confidence.create(1.0).value == 1.0


def test_risk_level_values() -> None:
    assert RiskLevel.LOW.value == "low"
    assert RiskLevel.CRITICAL.value == "critical"


def test_plan_create_from_decision() -> None:
    decision = _decision()
    research_step = PlanStep.create(
        title="Research niche",
        description="Validate audience demand and competitor landscape.",
        target_department=DepartmentName.RESEARCH,
        priority=TaskPriority.HIGH,
    )

    plan = Plan.create_from_decision(
        decision,
        title="Finance channel launch plan",
        summary="Research, brand, and publish the first content wave.",
        steps=(research_step,),
        status=PlanStatus.DRAFT,
        created_at=_timestamp(),
    )

    assert plan.decision_id == decision.id
    assert len(plan.steps) == 1
    assert plan.steps[0].target_department is DepartmentName.RESEARCH


def test_plan_rejects_ready_without_steps() -> None:
    decision = _decision()

    with pytest.raises(ValueError, match="at least one step"):
        Plan.create_from_decision(
            decision,
            title="Empty ready plan",
            summary="Should fail.",
            status=PlanStatus.READY,
        )


def test_plan_ready_with_steps() -> None:
    decision = _decision()
    step = PlanStep.create(
        title="Define brand",
        description="Create visual and verbal identity.",
        target_department=DepartmentName.BRAND,
    )

    plan = Plan.create_from_decision(
        decision,
        title="Brand plan",
        summary="Establish identity.",
        steps=(step,),
        status=PlanStatus.READY,
    )

    assert plan.status is PlanStatus.READY


def test_plan_step_dependency_validation() -> None:
    decision = _decision()
    first = PlanStep.create(
        title="Research",
        description="Research step.",
        target_department=DepartmentName.RESEARCH,
    )
    second = PlanStep.create(
        title="Brand",
        description="Brand step.",
        target_department=DepartmentName.BRAND,
        depends_on=(first.id,),
    )

    plan = Plan.create_from_decision(
        decision,
        title="Sequential plan",
        summary="Research then brand.",
        steps=(first, second),
    )

    plan.validate_step_dependencies()


def test_plan_rejects_missing_step_dependency() -> None:
    decision = _decision()
    missing_id = uuid4()
    step = PlanStep.create(
        title="Scripts",
        description="Depends on missing step.",
        target_department=DepartmentName.SCRIPTS,
        depends_on=(missing_id,),
    )

    with pytest.raises(ValueError, match="depends on missing step"):
        Plan.create_from_decision(
            decision,
            title="Invalid plan",
            summary="Broken dependencies.",
            steps=(step,),
        )


def test_plan_rejects_self_dependency() -> None:
    step_id = uuid4()
    step = PlanStep.create(
        title="Self dependent",
        description="Invalid dependency.",
        target_department=DepartmentName.VIDEO,
        step_id=step_id,
        depends_on=(step_id,),
    )
    decision = _decision()

    with pytest.raises(ValueError, match="cannot depend on itself"):
        Plan.create_from_decision(
            decision,
            title="Invalid plan",
            summary="Self dependency.",
            steps=(step,),
        )


def test_plan_rejects_circular_step_dependencies() -> None:
    step_a_id = uuid4()
    step_b_id = uuid4()
    step_a = PlanStep.create(
        title="Step A",
        description="Depends on B.",
        target_department=DepartmentName.RESEARCH,
        step_id=step_a_id,
        depends_on=(step_b_id,),
    )
    step_b = PlanStep.create(
        title="Step B",
        description="Depends on A.",
        target_department=DepartmentName.BRAND,
        step_id=step_b_id,
        depends_on=(step_a_id,),
    )
    decision = _decision()

    with pytest.raises(ValueError, match="circular"):
        Plan.create_from_decision(
            decision,
            title="Cyclic plan",
            summary="Circular dependencies.",
            steps=(step_a, step_b),
        )


def test_plan_add_step_validates_dependencies() -> None:
    decision = _decision()
    plan = Plan.create_from_decision(
        decision,
        title="Growing plan",
        summary="Add steps incrementally.",
    )
    first = PlanStep.create(
        title="Research",
        description="Research step.",
        target_department=DepartmentName.RESEARCH,
    )
    plan = plan.add_step(first)

    second = PlanStep.create(
        title="Brand",
        description="Depends on research.",
        target_department=DepartmentName.BRAND,
        depends_on=(first.id,),
    )
    plan = plan.add_step(second)

    assert len(plan.steps) == 2
    assert plan.get_step(second.id).depends_on == (first.id,)


def test_plan_with_status_enforces_ready_rule() -> None:
    decision = _decision()
    plan = Plan.create_from_decision(
        decision,
        title="Draft plan",
        summary="No steps yet.",
        status=PlanStatus.DRAFT,
    )

    with pytest.raises(ValueError, match="at least one step"):
        plan.with_status(PlanStatus.READY)
