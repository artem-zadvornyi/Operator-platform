"""In-memory company session model."""

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.blueprint import CompanyBlueprint
from app.domain.ceo import AICEO
from app.domain.decision import Decision
from app.domain.department import Department
from app.domain.mission import Mission
from app.domain.plan import Plan
from app.domain.workflow import Workflow


@dataclass(slots=True)
class CompanySession:
    """Mutable aggregate stored for a created company."""

    company_id: UUID
    blueprint: CompanyBlueprint
    departments: tuple[Department, ...]
    mission: Mission
    ceo: AICEO
    decision: Decision
    plan: Plan
    workflow: Workflow
    started: bool
    created_at: datetime
