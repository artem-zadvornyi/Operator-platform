"""Decision domain model for strategic choices made by Operator."""

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4


class DecisionStatus(StrEnum):
    """Lifecycle state of a strategic decision."""

    PROPOSED = "proposed"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"


class RiskLevel(StrEnum):
    """Assessed risk associated with pursuing a decision."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


CONFIDENCE_LOW_THRESHOLD = 0.4
CONFIDENCE_HIGH_THRESHOLD = 0.7


@dataclass(frozen=True, slots=True)
class Confidence:
    """Normalized confidence score for a strategic decision."""

    value: float

    def __post_init__(self) -> None:
        if not 0.0 <= self.value <= 1.0:
            msg = "Confidence value must be between 0.0 and 1.0."
            raise ValueError(msg)

    @classmethod
    def create(cls, value: float) -> "Confidence":
        """Create a validated confidence score."""
        return cls(value=value)

    @property
    def is_low(self) -> bool:
        return self.value < CONFIDENCE_LOW_THRESHOLD

    @property
    def is_medium(self) -> bool:
        return CONFIDENCE_LOW_THRESHOLD <= self.value < CONFIDENCE_HIGH_THRESHOLD

    @property
    def is_high(self) -> bool:
        return self.value >= CONFIDENCE_HIGH_THRESHOLD


@dataclass(frozen=True, slots=True)
class Decision:
    """A strategic choice explaining why Operator pursues a course of action."""

    id: UUID
    title: str
    context: str
    rationale: str
    confidence: Confidence
    risk_level: RiskLevel
    expected_outcome: str
    created_at: datetime
    status: DecisionStatus

    def __post_init__(self) -> None:
        if not self.title.strip():
            msg = "Decision title must not be empty."
            raise ValueError(msg)
        if not self.context.strip():
            msg = "Decision context must not be empty."
            raise ValueError(msg)
        if not self.rationale.strip():
            msg = "Decision rationale must not be empty."
            raise ValueError(msg)
        if not self.expected_outcome.strip():
            msg = "Decision expected outcome must not be empty."
            raise ValueError(msg)

    @classmethod
    def create(
        cls,
        *,
        title: str,
        context: str,
        rationale: str,
        confidence: Confidence,
        risk_level: RiskLevel,
        expected_outcome: str,
        status: DecisionStatus = DecisionStatus.PROPOSED,
        decision_id: UUID | None = None,
        created_at: datetime | None = None,
    ) -> "Decision":
        """Create a new proposed decision."""
        timestamp = created_at or datetime.now(UTC)
        return cls(
            id=decision_id or uuid4(),
            title=title.strip(),
            context=context.strip(),
            rationale=rationale.strip(),
            confidence=confidence,
            risk_level=risk_level,
            expected_outcome=expected_outcome.strip(),
            created_at=timestamp,
            status=status,
        )

    def with_status(self, status: DecisionStatus) -> "Decision":
        """Return a copy of the decision with an updated status."""
        return Decision(
            id=self.id,
            title=self.title,
            context=self.context,
            rationale=self.rationale,
            confidence=self.confidence,
            risk_level=self.risk_level,
            expected_outcome=self.expected_outcome,
            created_at=self.created_at,
            status=status,
        )
