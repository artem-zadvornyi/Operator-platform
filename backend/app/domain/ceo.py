"""AI CEO domain model for transforming missions into strategic decisions."""

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from app.domain.decision import Confidence, Decision, DecisionStatus, RiskLevel
from app.domain.mission import Mission


class CEOStatus(StrEnum):
    """Operational state of the AI CEO."""

    IDLE = "idle"
    THINKING = "thinking"
    WAITING_APPROVAL = "waiting_approval"
    EXECUTING = "executing"
    PAUSED = "paused"
    ARCHIVED = "archived"


class StrategyMode(StrEnum):
    """Strategic posture guiding how the CEO proposes decisions."""

    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    AGGRESSIVE = "aggressive"
    EXPERIMENTAL = "experimental"


@dataclass(frozen=True, slots=True)
class _StrategyProfile:
    confidence: float
    risk_level: RiskLevel
    rationale: str
    outcome_focus: str


STRATEGY_PROFILES: dict[StrategyMode, _StrategyProfile] = {
    StrategyMode.CONSERVATIVE: _StrategyProfile(
        confidence=0.85,
        risk_level=RiskLevel.LOW,
        rationale=("Prioritize validated execution with measured rollout and downside protection."),
        outcome_focus="a stable foundation with controlled risk exposure",
    ),
    StrategyMode.BALANCED: _StrategyProfile(
        confidence=0.65,
        risk_level=RiskLevel.MEDIUM,
        rationale=("Balance growth opportunity with operational discipline across departments."),
        outcome_focus="steady progress toward the mission goal",
    ),
    StrategyMode.AGGRESSIVE: _StrategyProfile(
        confidence=0.70,
        risk_level=RiskLevel.HIGH,
        rationale=("Prioritize accelerated growth, faster publishing cadence, and market capture."),
        outcome_focus="maximum audience and revenue growth within the mission window",
    ),
    StrategyMode.EXPERIMENTAL: _StrategyProfile(
        confidence=0.50,
        risk_level=RiskLevel.HIGH,
        rationale=("Test innovative formats and positioning while accepting higher uncertainty."),
        outcome_focus="validated learning from bold content experiments",
    ),
}


@dataclass(frozen=True, slots=True)
class AICEO:
    """Strategic domain entity that transforms missions into proposed decisions."""

    id: UUID
    name: str
    status: CEOStatus
    strategy_mode: StrategyMode
    created_at: datetime
    updated_at: datetime
    current_mission_id: UUID | None
    decision_ids: tuple[UUID, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "decision_ids", tuple(self.decision_ids))
        if not self.name.strip():
            msg = "AI CEO name must not be empty."
            raise ValueError(msg)
        if len(self.decision_ids) != len(set(self.decision_ids)):
            msg = "AI CEO decision references must be unique."
            raise ValueError(msg)

    @classmethod
    def create(
        cls,
        name: str,
        *,
        strategy_mode: StrategyMode = StrategyMode.BALANCED,
        ceo_id: UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> "AICEO":
        """Create a new AI CEO in idle state."""
        timestamp = created_at or datetime.now(UTC)
        update_timestamp = updated_at or timestamp
        return cls(
            id=ceo_id or uuid4(),
            name=name.strip(),
            status=CEOStatus.IDLE,
            strategy_mode=strategy_mode,
            created_at=timestamp,
            updated_at=update_timestamp,
            current_mission_id=None,
            decision_ids=(),
        )

    def assign_mission(self, mission: Mission, updated_at: datetime) -> "AICEO":
        """Assign the CEO to a single mission for v1 strategic focus."""
        self._ensure_mutable()

        return AICEO(
            id=self.id,
            name=self.name,
            status=self.status,
            strategy_mode=self.strategy_mode,
            created_at=self.created_at,
            updated_at=updated_at,
            current_mission_id=mission.id,
            decision_ids=self.decision_ids,
        )

    def propose_decision(
        self,
        mission: Mission,
        updated_at: datetime,
    ) -> tuple["AICEO", Decision]:
        """Propose a deterministic strategic decision derived from a mission."""
        self._ensure_mutable()
        self._ensure_can_propose()
        self._ensure_mission_assigned(mission)

        decision = _build_decision_from_mission(
            mission,
            self.strategy_mode,
            created_at=updated_at,
        )

        if decision.id in self.decision_ids:
            msg = f"Decision {decision.id} is already linked to this CEO."
            raise ValueError(msg)

        updated_ceo = AICEO(
            id=self.id,
            name=self.name,
            status=CEOStatus.WAITING_APPROVAL,
            strategy_mode=self.strategy_mode,
            created_at=self.created_at,
            updated_at=updated_at,
            current_mission_id=self.current_mission_id,
            decision_ids=(*self.decision_ids, decision.id),
        )

        return updated_ceo, decision

    def add_decision(self, decision_id: UUID, updated_at: datetime) -> "AICEO":
        """Attach an existing decision reference to this CEO."""
        self._ensure_mutable()

        if decision_id in self.decision_ids:
            msg = f"Decision {decision_id} is already linked to this CEO."
            raise ValueError(msg)

        return AICEO(
            id=self.id,
            name=self.name,
            status=self.status,
            strategy_mode=self.strategy_mode,
            created_at=self.created_at,
            updated_at=updated_at,
            current_mission_id=self.current_mission_id,
            decision_ids=(*self.decision_ids, decision_id),
        )

    def with_status(self, status: CEOStatus, updated_at: datetime) -> "AICEO":
        """Return a copy of the CEO with an updated status."""
        self._ensure_mutable()

        return AICEO(
            id=self.id,
            name=self.name,
            status=status,
            strategy_mode=self.strategy_mode,
            created_at=self.created_at,
            updated_at=updated_at,
            current_mission_id=self.current_mission_id,
            decision_ids=self.decision_ids,
        )

    def with_strategy_mode(
        self,
        strategy_mode: StrategyMode,
        updated_at: datetime,
    ) -> "AICEO":
        """Return a copy of the CEO with an updated strategy mode."""
        self._ensure_mutable()

        return AICEO(
            id=self.id,
            name=self.name,
            status=self.status,
            strategy_mode=strategy_mode,
            created_at=self.created_at,
            updated_at=updated_at,
            current_mission_id=self.current_mission_id,
            decision_ids=self.decision_ids,
        )

    @property
    def is_archived(self) -> bool:
        return self.status is CEOStatus.ARCHIVED

    def _ensure_mutable(self) -> None:
        if self.is_archived:
            msg = f"AI CEO {self.id} is archived and cannot be modified."
            raise ValueError(msg)

    def _ensure_can_propose(self) -> None:
        if self.status is CEOStatus.PAUSED:
            msg = "Paused AI CEO cannot propose decisions."
            raise ValueError(msg)

    def _ensure_mission_assigned(self, mission: Mission) -> None:
        if self.current_mission_id is None:
            msg = "AI CEO cannot propose decisions without an assigned mission."
            raise ValueError(msg)
        if self.current_mission_id != mission.id:
            msg = "AI CEO can only propose decisions for the currently assigned mission."
            raise ValueError(msg)


def _build_decision_from_mission(
    mission: Mission,
    strategy_mode: StrategyMode,
    *,
    created_at: datetime,
) -> Decision:
    profile = STRATEGY_PROFILES[strategy_mode]
    platforms = ", ".join(mission.primary_platforms)
    languages = ", ".join(mission.languages)

    return Decision.create(
        title=f"Advance mission: {mission.title}",
        context=(
            f"{mission.description} Goal: {mission.goal} "
            f"Audience: {mission.target_audience} "
            f"Platforms: {platforms} Languages: {languages}."
        ),
        rationale=(
            f"{profile.rationale} This proposal supports mission "
            f"'{mission.title}' with a {strategy_mode.value} strategy."
        ),
        confidence=Confidence.create(profile.confidence),
        risk_level=profile.risk_level,
        expected_outcome=(f"Deliver {profile.outcome_focus} aligned with: {mission.goal}"),
        status=DecisionStatus.PROPOSED,
        created_at=created_at,
    )
