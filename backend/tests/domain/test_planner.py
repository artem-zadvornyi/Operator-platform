from datetime import UTC, datetime

import pytest

from app.domain import (
    Confidence,
    Decision,
    DecisionStatus,
    DepartmentName,
    Planner,
    PlanStatus,
    RiskLevel,
)


def _timestamp() -> datetime:
    return datetime(2026, 5, 1, 9, 0, tzinfo=UTC)


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


def test_planner_rejects_proposed_decision() -> None:
    planner = Planner()
    decision = _approved_decision(status=DecisionStatus.PROPOSED)

    with pytest.raises(ValueError, match="Only approved decisions"):
        planner.create_plan(decision)


def test_planner_rejects_rejected_decision() -> None:
    planner = Planner()
    decision = _approved_decision(status=DecisionStatus.REJECTED)

    with pytest.raises(ValueError, match="Only approved decisions"):
        planner.create_plan(decision)


def test_planner_rejects_low_confidence() -> None:
    planner = Planner()
    decision = _approved_decision(confidence=Confidence.create(0.29))

    with pytest.raises(ValueError, match="below the minimum planning threshold"):
        planner.create_plan(decision)


def test_planner_accepts_minimum_confidence() -> None:
    planner = Planner()
    decision = _approved_decision(confidence=Confidence.create(0.30))

    plan = planner.create_plan(decision)

    assert plan.status is PlanStatus.READY


def test_planner_rejects_critical_risk() -> None:
    planner = Planner()
    decision = _approved_decision(risk_level=RiskLevel.CRITICAL)

    with pytest.raises(ValueError, match="Critical risk decisions"):
        planner.create_plan(decision)


def test_planner_generates_department_order() -> None:
    planner = Planner()
    plan = planner.create_plan(_approved_decision())

    departments = [step.target_department for step in plan.steps]
    assert departments == [
        DepartmentName.RESEARCH,
        DepartmentName.BRAND,
        DepartmentName.SCRIPTS,
        DepartmentName.VIDEO,
        DepartmentName.PUBLISHING,
        DepartmentName.GROWTH,
    ]
    assert DepartmentName.CEO not in departments


def test_planner_builds_linear_dependency_chain() -> None:
    planner = Planner()
    plan = planner.create_plan(_approved_decision())

    assert plan.steps[0].depends_on == ()
    for index in range(1, len(plan.steps)):
        previous_step = plan.steps[index - 1]
        current_step = plan.steps[index]
        assert current_step.depends_on == (previous_step.id,)


def test_planner_generates_ready_valid_plan() -> None:
    planner = Planner()
    decision = _approved_decision()
    plan = planner.create_plan(decision)

    assert plan.status is PlanStatus.READY
    assert plan.decision_id == decision.id
    assert plan.title == f"Plan: {decision.title}"
    assert len(plan.steps) == 6

    for step in plan.steps:
        assert step.title
        assert step.description
        assert step.priority

    plan.validate_step_dependencies()


def test_planner_is_instance_based_not_static() -> None:
    strict_planner = Planner(min_confidence=0.50)
    permissive_planner = Planner(min_confidence=0.30)

    decision = _approved_decision(confidence=Confidence.create(0.40))

    plan = permissive_planner.create_plan(decision)
    assert plan.status is PlanStatus.READY

    with pytest.raises(ValueError, match="below the minimum planning threshold"):
        strict_planner.create_plan(decision)
