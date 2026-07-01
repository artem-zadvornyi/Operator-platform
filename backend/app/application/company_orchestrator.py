"""Company orchestration — coordinates application services for the company API."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID

from app.application.company_service import CompanyService
from app.application.execution_service import ExecutionService
from app.application.mission_service import MissionService
from app.domain.ceo import CEOStatus
from app.domain.mission import MissionPriority, MissionStatus
from app.mappers.company_presenter import CompanyPresenter
from app.mappers.idea_mapper import MOCK_FAILURE_IDEA, map_idea
from app.schemas.company import CompanyDetailResponse, CreateCompanyResponse, StartCompanyResponse
from app.stores.company_session import CompanySession
from app.stores.memory_company_store import MemoryCompanyStore


class CompanyNotFoundError(Exception):
    """Raised when a company session does not exist in the store."""


@dataclass(slots=True)
class CompanyOrchestrator:
    """Coordinates company creation and lifecycle for the HTTP API."""

    store: MemoryCompanyStore
    company_service: CompanyService = field(default_factory=CompanyService)
    mission_service: MissionService = field(default_factory=MissionService)
    execution_service: ExecutionService = field(default_factory=ExecutionService)
    presenter: CompanyPresenter = field(default_factory=CompanyPresenter)

    def create_company(self, idea: str) -> CreateCompanyResponse:
        trimmed = idea.strip()
        if not trimmed:
            msg = "Business idea is required."
            raise ValueError(msg)
        if trimmed == MOCK_FAILURE_IDEA:
            msg = "Company creation failed."
            raise ValueError(msg)

        now = datetime.now(UTC)
        mapping = map_idea(trimmed)

        company_setup = self.company_service.create_company(
            company_name=mapping.company_name,
            business_goal=mapping.business_goal,
            target_audience=mapping.target_audience,
            platforms=mapping.platforms,
            content_style=mapping.content_style,
            languages=mapping.languages,
            tone_of_voice=mapping.tone_of_voice,
            publishing_frequency=mapping.publishing_frequency,
            created_at=now,
        )
        mission = self.mission_service.create_mission(
            title=mapping.mission_title,
            description=mapping.mission_description,
            goal=mapping.mission_goal,
            target_audience=mapping.mission_target_audience,
            primary_platforms=mapping.platforms,
            languages=mapping.languages,
            priority=MissionPriority.MEDIUM,
            status=MissionStatus.ACTIVE,
            created_at=now,
            updated_at=now,
        )
        ceo = self.mission_service.create_ceo("AI CEO", created_at=now)
        assigned_ceo = self.mission_service.assign_ceo(ceo, mission, now)
        start_result = self.mission_service.start_company(
            mission=mission,
            ceo=assigned_ceo,
            updated_at=now,
        )
        workflow_setup = self.execution_service.create_workflow(start_result.decision)

        session = CompanySession(
            company_id=company_setup.blueprint.id,
            blueprint=company_setup.blueprint,
            departments=company_setup.departments,
            mission=start_result.mission,
            ceo=start_result.ceo,
            decision=start_result.decision,
            plan=workflow_setup.plan,
            workflow=workflow_setup.workflow,
            started=False,
            created_at=now,
        )
        self.store.save(session)
        return self.presenter.to_create_response(session)

    def start_company(self, company_id: UUID) -> StartCompanyResponse:
        session = self._require_session(company_id)
        if session.started:
            return StartCompanyResponse(companyId=str(company_id), status="started")

        now = datetime.now(UTC)
        session.ceo = session.ceo.with_status(CEOStatus.EXECUTING, now)
        session.started = True
        self.store.save(session)

        return StartCompanyResponse(companyId=str(company_id), status="started")

    def get_company(self, company_id: UUID) -> CompanyDetailResponse:
        session = self._require_session(company_id)
        return self.presenter.to_company_detail(session)

    def _require_session(self, company_id: UUID) -> CompanySession:
        session = self.store.get(company_id)
        if session is None:
            msg = "Company not found."
            raise CompanyNotFoundError(msg)
        return session
