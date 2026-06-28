"""Mission domain model — the highest-level business objective in Operator."""

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4


class MissionStatus(StrEnum):
    """Lifecycle state of a user's long-term mission."""

    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class MissionPriority(StrEnum):
    """Relative strategic importance of a mission."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


TERMINAL_MISSION_STATUSES: frozenset[MissionStatus] = frozenset({MissionStatus.ARCHIVED})


@dataclass(frozen=True, slots=True)
class Mission:
    """Aggregate root representing a user's long-term objective.

    Missions own strategic intent and reference decisions by identifier only.
    They do not know about plans, workflows, or tasks.
    """

    id: UUID
    title: str
    description: str
    goal: str
    target_audience: str
    primary_platforms: tuple[str, ...]
    languages: tuple[str, ...]
    priority: MissionPriority
    status: MissionStatus
    created_at: datetime
    updated_at: datetime
    decision_ids: tuple[UUID, ...]

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "primary_platforms",
            tuple(platform.strip() for platform in self.primary_platforms),
        )
        object.__setattr__(
            self,
            "languages",
            tuple(language.strip() for language in self.languages),
        )
        object.__setattr__(self, "decision_ids", tuple(self.decision_ids))
        self._validate()

    @classmethod
    def create(
        cls,
        *,
        title: str,
        description: str,
        goal: str,
        target_audience: str,
        primary_platforms: tuple[str, ...],
        languages: tuple[str, ...],
        priority: MissionPriority = MissionPriority.MEDIUM,
        status: MissionStatus = MissionStatus.DRAFT,
        decision_ids: tuple[UUID, ...] = (),
        mission_id: UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> "Mission":
        """Create a new mission in draft state."""
        timestamp = created_at or datetime.now(UTC)
        update_timestamp = updated_at or timestamp
        return cls(
            id=mission_id or uuid4(),
            title=title.strip(),
            description=description.strip(),
            goal=goal.strip(),
            target_audience=target_audience.strip(),
            primary_platforms=primary_platforms,
            languages=languages,
            priority=priority,
            status=status,
            created_at=timestamp,
            updated_at=update_timestamp,
            decision_ids=decision_ids,
        )

    def add_decision(self, decision_id: UUID, updated_at: datetime) -> "Mission":
        """Attach a decision reference to this mission."""
        self._ensure_mutable()

        if decision_id in self.decision_ids:
            msg = f"Decision {decision_id} is already linked to this mission."
            raise ValueError(msg)

        return Mission(
            id=self.id,
            title=self.title,
            description=self.description,
            goal=self.goal,
            target_audience=self.target_audience,
            primary_platforms=self.primary_platforms,
            languages=self.languages,
            priority=self.priority,
            status=self.status,
            created_at=self.created_at,
            updated_at=updated_at,
            decision_ids=(*self.decision_ids, decision_id),
        )

    def with_status(self, status: MissionStatus, updated_at: datetime) -> "Mission":
        """Return a copy of the mission with an updated status."""
        self._ensure_mutable()

        if self.status is MissionStatus.COMPLETED and status is MissionStatus.ACTIVE:
            msg = "Completed missions cannot become active again."
            raise ValueError(msg)

        return Mission(
            id=self.id,
            title=self.title,
            description=self.description,
            goal=self.goal,
            target_audience=self.target_audience,
            primary_platforms=self.primary_platforms,
            languages=self.languages,
            priority=self.priority,
            status=status,
            created_at=self.created_at,
            updated_at=updated_at,
            decision_ids=self.decision_ids,
        )

    def with_priority(
        self,
        priority: MissionPriority,
        updated_at: datetime,
    ) -> "Mission":
        """Return a copy of the mission with an updated priority."""
        self._ensure_mutable()

        return Mission(
            id=self.id,
            title=self.title,
            description=self.description,
            goal=self.goal,
            target_audience=self.target_audience,
            primary_platforms=self.primary_platforms,
            languages=self.languages,
            priority=priority,
            status=self.status,
            created_at=self.created_at,
            updated_at=updated_at,
            decision_ids=self.decision_ids,
        )

    @property
    def is_archived(self) -> bool:
        return self.status is MissionStatus.ARCHIVED

    def _ensure_mutable(self) -> None:
        if self.is_archived:
            msg = f"Mission {self.id} is archived and cannot be modified."
            raise ValueError(msg)

    def _validate(self) -> None:
        if not self.title.strip():
            msg = "Mission title must not be empty."
            raise ValueError(msg)
        if not self.goal.strip():
            msg = "Mission goal must not be empty."
            raise ValueError(msg)
        if not self.primary_platforms:
            msg = "Mission must define at least one platform."
            raise ValueError(msg)
        if not self.languages:
            msg = "Mission must define at least one language."
            raise ValueError(msg)
        if len(self.decision_ids) != len(set(self.decision_ids)):
            msg = "Mission decision references must be unique."
            raise ValueError(msg)
