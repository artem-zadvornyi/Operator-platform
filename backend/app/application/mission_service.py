"""Mission application service — orchestrates mission and CEO strategic startup."""

from dataclasses import dataclass
from datetime import datetime

from app.domain.ceo import AICEO, StrategyMode
from app.domain.decision import Decision, DecisionStatus
from app.domain.mission import Mission, MissionPriority, MissionStatus


@dataclass(frozen=True, slots=True)
class CompanyStartResult:
    """Result of starting strategic operations for a mission."""

    mission: Mission
    ceo: AICEO
    decision: Decision


@dataclass(frozen=True, slots=True)
class MissionService:
    """Orchestrates mission lifecycle and CEO strategic kickoff."""

    def create_mission(
        self,
        *,
        title: str,
        description: str,
        goal: str,
        target_audience: str,
        primary_platforms: tuple[str, ...],
        languages: tuple[str, ...],
        priority: MissionPriority = MissionPriority.MEDIUM,
        status: MissionStatus = MissionStatus.DRAFT,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> Mission:
        """Delegate mission creation to the domain model."""
        return Mission.create(
            title=title,
            description=description,
            goal=goal,
            target_audience=target_audience,
            primary_platforms=primary_platforms,
            languages=languages,
            priority=priority,
            status=status,
            created_at=created_at,
            updated_at=updated_at,
        )

    def assign_ceo(
        self,
        ceo: AICEO,
        mission: Mission,
        updated_at: datetime,
    ) -> AICEO:
        """Delegate CEO mission assignment to the domain model."""
        return ceo.assign_mission(mission, updated_at)

    def start_company(
        self,
        *,
        mission: Mission,
        ceo: AICEO,
        updated_at: datetime,
    ) -> CompanyStartResult:
        """Assign the CEO, propose a decision, approve it, and link it to the mission."""
        assigned_ceo = self.assign_ceo(ceo, mission, updated_at)
        proposing_ceo, proposed_decision = assigned_ceo.propose_decision(mission, updated_at)
        linked_mission = mission.add_decision(proposed_decision.id, updated_at)
        approved_decision = proposed_decision.with_status(DecisionStatus.APPROVED)

        return CompanyStartResult(
            mission=linked_mission,
            ceo=proposing_ceo,
            decision=approved_decision,
        )

    def create_ceo(
        self,
        name: str,
        *,
        strategy_mode: StrategyMode = StrategyMode.BALANCED,
        created_at: datetime | None = None,
    ) -> AICEO:
        """Create a CEO ready for mission assignment."""
        return AICEO.create(name, strategy_mode=strategy_mode, created_at=created_at)
