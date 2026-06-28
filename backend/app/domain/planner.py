"""Planning engine domain service for converting decisions into executable plans."""

from dataclasses import dataclass
from datetime import UTC, datetime

from app.domain.decision import Decision, DecisionStatus, RiskLevel
from app.domain.department import DepartmentName
from app.domain.plan import Plan, PlanStatus, PlanStep
from app.domain.task import TaskPriority

MIN_PLANNING_CONFIDENCE = 0.30

PLANNING_SEQUENCE: tuple[tuple[DepartmentName, str, str, TaskPriority], ...] = (
    (
        DepartmentName.RESEARCH,
        "Research niche and audience",
        "Validate the target audience, competitors, and content opportunities.",
        TaskPriority.HIGH,
    ),
    (
        DepartmentName.BRAND,
        "Define brand identity",
        "Establish visual and verbal brand guidelines aligned with the decision.",
        TaskPriority.MEDIUM,
    ),
    (
        DepartmentName.SCRIPTS,
        "Write content scripts",
        "Produce scripts that reflect the brand and research findings.",
        TaskPriority.MEDIUM,
    ),
    (
        DepartmentName.VIDEO,
        "Produce video content",
        "Transform approved scripts into production-ready video assets.",
        TaskPriority.MEDIUM,
    ),
    (
        DepartmentName.PUBLISHING,
        "Prepare publishing packages",
        "Package content for platform distribution and approval.",
        TaskPriority.MEDIUM,
    ),
    (
        DepartmentName.GROWTH,
        "Identify growth opportunities",
        "Analyze launch readiness and recommend initial growth experiments.",
        TaskPriority.MEDIUM,
    ),
)


@dataclass(frozen=True, slots=True)
class Planner:
    """Converts approved strategic decisions into department-ordered executable plans."""

    min_confidence: float = MIN_PLANNING_CONFIDENCE

    def __post_init__(self) -> None:
        if not 0.0 <= self.min_confidence <= 1.0:
            msg = "Minimum planning confidence must be between 0.0 and 1.0."
            raise ValueError(msg)

    def create_plan(self, decision: Decision) -> Plan:
        """Generate a ready plan from an approved decision."""
        self._validate_decision(decision)
        steps = self._generate_steps(decision)
        return Plan.create_from_decision(
            decision,
            title=f"Plan: {decision.title}",
            summary=(f"Execute the approved decision to achieve: {decision.expected_outcome}"),
            steps=tuple(steps),
            status=PlanStatus.READY,
            created_at=datetime.now(UTC),
        )

    def _validate_decision(self, decision: Decision) -> None:
        if decision.status is not DecisionStatus.APPROVED:
            msg = f"Only approved decisions can be planned; got {decision.status.value}."
            raise ValueError(msg)

        if decision.confidence.value < self.min_confidence:
            msg = (
                f"Decision confidence {decision.confidence.value} is below the "
                f"minimum planning threshold of {self.min_confidence}."
            )
            raise ValueError(msg)

        if decision.risk_level is RiskLevel.CRITICAL:
            msg = "Critical risk decisions cannot be planned automatically."
            raise ValueError(msg)

    def _generate_steps(self, decision: Decision) -> list[PlanStep]:
        steps: list[PlanStep] = []
        previous_step_id = None

        for department, title, description, priority in PLANNING_SEQUENCE:
            depends_on = () if previous_step_id is None else (previous_step_id,)
            contextual_description = f"{description} Context: {decision.context.strip()}"
            step = PlanStep.create(
                title=title,
                description=contextual_description,
                target_department=department,
                priority=priority,
                depends_on=depends_on,
            )
            steps.append(step)
            previous_step_id = step.id

        return steps
