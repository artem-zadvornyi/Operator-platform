from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from app.domain import (
    AICEO,
    CEOStatus,
    DecisionStatus,
    Mission,
    MissionPriority,
    RiskLevel,
    StrategyMode,
)


def _timestamp(offset_minutes: int = 0) -> datetime:
    return datetime(2026, 8, 1, 9, 0, tzinfo=UTC) + timedelta(minutes=offset_minutes)


def _mission(**overrides: object) -> Mission:
    defaults: dict[str, object] = {
        "title": "Build a finance media business",
        "description": "Create a durable content company around personal finance education.",
        "goal": "Reach 100k subscribers and sustainable ad revenue within 18 months.",
        "target_audience": "Young professionals learning money management.",
        "primary_platforms": ("YouTube", "TikTok"),
        "languages": ("English",),
        "priority": MissionPriority.HIGH,
        "created_at": _timestamp(),
        "updated_at": _timestamp(),
    }
    defaults.update(overrides)
    return Mission.create(**defaults)


def _ceo_with_mission(**mission_overrides: object) -> tuple[AICEO, Mission]:
    mission = _mission(**mission_overrides)
    ceo = AICEO.create("AI CEO", created_at=_timestamp()).assign_mission(
        mission,
        _timestamp(1),
    )
    return ceo, mission


def test_ceo_create_sets_defaults() -> None:
    ceo = AICEO.create("AI CEO", created_at=_timestamp())

    assert ceo.name == "AI CEO"
    assert ceo.status is CEOStatus.IDLE
    assert ceo.strategy_mode is StrategyMode.BALANCED
    assert ceo.current_mission_id is None
    assert ceo.decision_ids == ()


def test_ceo_assign_mission() -> None:
    mission = _mission()
    ceo = AICEO.create("AI CEO", created_at=_timestamp())

    updated = ceo.assign_mission(mission, _timestamp(1))

    assert updated.current_mission_id == mission.id
    assert updated.updated_at == _timestamp(1)


def test_ceo_propose_decision_creates_proposed_decision() -> None:
    ceo, mission = _ceo_with_mission()

    updated_ceo, decision = ceo.propose_decision(mission, _timestamp(2))

    assert decision.status is DecisionStatus.PROPOSED
    assert updated_ceo.status is CEOStatus.WAITING_APPROVAL
    assert decision.id in updated_ceo.decision_ids


def test_ceo_propose_decision_uses_mission_fields() -> None:
    ceo, mission = _ceo_with_mission()
    _, decision = ceo.propose_decision(mission, _timestamp(2))

    assert mission.title in decision.title
    assert mission.description in decision.context
    assert mission.goal in decision.context
    assert mission.target_audience in decision.context
    assert "YouTube" in decision.context
    assert mission.goal in decision.expected_outcome


def test_ceo_propose_decision_balanced_strategy() -> None:
    ceo, mission = _ceo_with_mission()
    _, decision = ceo.propose_decision(mission, _timestamp(2))

    assert decision.confidence.value == 0.65
    assert decision.risk_level is RiskLevel.MEDIUM
    assert "balanced" in decision.rationale


def test_ceo_propose_decision_conservative_strategy() -> None:
    ceo, mission = _ceo_with_mission()
    ceo = ceo.with_strategy_mode(StrategyMode.CONSERVATIVE, _timestamp(1))
    _, decision = ceo.propose_decision(mission, _timestamp(2))

    assert decision.confidence.value == 0.85
    assert decision.risk_level is RiskLevel.LOW
    assert decision.confidence.is_high


def test_ceo_propose_decision_aggressive_strategy() -> None:
    ceo, mission = _ceo_with_mission()
    ceo = ceo.with_strategy_mode(StrategyMode.AGGRESSIVE, _timestamp(1))
    _, decision = ceo.propose_decision(mission, _timestamp(2))

    assert decision.risk_level is RiskLevel.HIGH
    assert "growth" in decision.rationale.lower()


def test_ceo_propose_decision_experimental_strategy() -> None:
    ceo, mission = _ceo_with_mission()
    ceo = ceo.with_strategy_mode(StrategyMode.EXPERIMENTAL, _timestamp(1))
    _, decision = ceo.propose_decision(mission, _timestamp(2))

    assert decision.confidence.value == 0.50
    assert decision.risk_level is RiskLevel.HIGH
    assert decision.risk_level is not RiskLevel.CRITICAL


def test_ceo_rejects_proposal_without_assigned_mission() -> None:
    ceo = AICEO.create("AI CEO", created_at=_timestamp())
    mission = _mission()

    with pytest.raises(ValueError, match="without an assigned mission"):
        ceo.propose_decision(mission, _timestamp(1))


def test_ceo_rejects_proposal_for_non_current_mission() -> None:
    ceo, mission = _ceo_with_mission()
    other_mission = _mission(title="Different mission")

    with pytest.raises(ValueError, match="currently assigned mission"):
        ceo.propose_decision(other_mission, _timestamp(2))


def test_ceo_paused_cannot_propose_decisions() -> None:
    ceo, mission = _ceo_with_mission()
    ceo = ceo.with_status(CEOStatus.PAUSED, _timestamp(2))

    with pytest.raises(ValueError, match="Paused AI CEO cannot propose"):
        ceo.propose_decision(mission, _timestamp(3))


def test_ceo_archived_is_immutable() -> None:
    ceo, mission = _ceo_with_mission()
    ceo = ceo.with_status(CEOStatus.ARCHIVED, _timestamp(2))
    decision_id = uuid4()

    with pytest.raises(ValueError, match="archived and cannot be modified"):
        ceo.assign_mission(mission, _timestamp(3))

    with pytest.raises(ValueError, match="archived and cannot be modified"):
        ceo.propose_decision(mission, _timestamp(3))

    with pytest.raises(ValueError, match="archived and cannot be modified"):
        ceo.add_decision(decision_id, _timestamp(3))

    with pytest.raises(ValueError, match="archived and cannot be modified"):
        ceo.with_status(CEOStatus.IDLE, _timestamp(3))

    with pytest.raises(ValueError, match="archived and cannot be modified"):
        ceo.with_strategy_mode(StrategyMode.AGGRESSIVE, _timestamp(3))


def test_ceo_add_decision_enforces_unique_ids() -> None:
    decision_id = uuid4()
    ceo = AICEO.create("AI CEO", created_at=_timestamp())
    ceo = ceo.add_decision(decision_id, _timestamp(1))

    with pytest.raises(ValueError, match="already linked"):
        ceo.add_decision(decision_id, _timestamp(2))


def test_ceo_strategy_mode_change() -> None:
    ceo = AICEO.create("AI CEO", created_at=_timestamp())
    updated = ceo.with_strategy_mode(StrategyMode.AGGRESSIVE, _timestamp(1))

    assert updated.strategy_mode is StrategyMode.AGGRESSIVE
