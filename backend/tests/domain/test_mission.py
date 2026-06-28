from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from app.domain import Mission, MissionPriority, MissionStatus


def _timestamp(offset_minutes: int = 0) -> datetime:
    return datetime(2026, 7, 1, 10, 0, tzinfo=UTC) + timedelta(minutes=offset_minutes)


def _mission(**overrides: object) -> Mission:
    defaults: dict[str, object] = {
        "title": "Build a finance media business",
        "description": "Create a durable content company around personal finance education.",
        "goal": "Reach 100k subscribers and sustainable ad revenue within 18 months.",
        "target_audience": "Young professionals learning money management.",
        "primary_platforms": ("YouTube", "TikTok"),
        "languages": ("English",),
        "created_at": _timestamp(),
        "updated_at": _timestamp(),
    }
    defaults.update(overrides)
    return Mission.create(**defaults)


def test_mission_create_sets_defaults() -> None:
    mission = _mission()

    assert mission.status is MissionStatus.DRAFT
    assert mission.priority is MissionPriority.MEDIUM
    assert mission.decision_ids == ()
    assert mission.primary_platforms == ("YouTube", "TikTok")
    assert mission.languages == ("English",)


def test_mission_rejects_empty_title() -> None:
    with pytest.raises(ValueError, match="title"):
        _mission(title="   ")


def test_mission_rejects_empty_goal() -> None:
    with pytest.raises(ValueError, match="goal"):
        _mission(goal="   ")


def test_mission_requires_at_least_one_platform() -> None:
    with pytest.raises(ValueError, match="at least one platform"):
        _mission(primary_platforms=())


def test_mission_requires_at_least_one_language() -> None:
    with pytest.raises(ValueError, match="at least one language"):
        _mission(languages=())


def test_mission_can_exist_without_decisions() -> None:
    mission = _mission()
    assert mission.decision_ids == ()


def test_mission_add_decision() -> None:
    mission = _mission()
    decision_id = uuid4()

    updated = mission.add_decision(decision_id, _timestamp(1))

    assert updated.decision_ids == (decision_id,)
    assert updated.updated_at == _timestamp(1)
    assert mission.decision_ids == ()


def test_mission_rejects_duplicate_decision_ids() -> None:
    decision_id = uuid4()
    mission = _mission(decision_ids=(decision_id,))

    with pytest.raises(ValueError, match="already linked"):
        mission.add_decision(decision_id, _timestamp(1))


def test_mission_rejects_duplicate_decision_ids_on_create() -> None:
    decision_id = uuid4()

    with pytest.raises(ValueError, match="unique"):
        _mission(decision_ids=(decision_id, decision_id))


def test_mission_status_transition() -> None:
    mission = _mission().with_status(MissionStatus.ACTIVE, _timestamp(1))

    assert mission.status is MissionStatus.ACTIVE
    assert mission.updated_at == _timestamp(1)


def test_mission_completed_cannot_become_active() -> None:
    mission = _mission().with_status(MissionStatus.COMPLETED, _timestamp(1))

    with pytest.raises(ValueError, match="cannot become active again"):
        mission.with_status(MissionStatus.ACTIVE, _timestamp(2))


def test_mission_completed_can_be_archived() -> None:
    mission = (
        _mission()
        .with_status(MissionStatus.COMPLETED, _timestamp(1))
        .with_status(MissionStatus.ARCHIVED, _timestamp(2))
    )

    assert mission.status is MissionStatus.ARCHIVED


def test_mission_archived_is_immutable() -> None:
    mission = _mission().with_status(MissionStatus.ARCHIVED, _timestamp(1))
    decision_id = uuid4()

    with pytest.raises(ValueError, match="archived and cannot be modified"):
        mission.add_decision(decision_id, _timestamp(2))

    with pytest.raises(ValueError, match="archived and cannot be modified"):
        mission.with_status(MissionStatus.ACTIVE, _timestamp(2))

    with pytest.raises(ValueError, match="archived and cannot be modified"):
        mission.with_priority(MissionPriority.HIGH, _timestamp(2))


def test_mission_priority_change() -> None:
    mission = _mission().with_priority(MissionPriority.CRITICAL, _timestamp(1))

    assert mission.priority is MissionPriority.CRITICAL
    assert mission.updated_at == _timestamp(1)
