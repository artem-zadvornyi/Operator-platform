"""Present domain company sessions as API response models."""

from datetime import datetime

from app.domain.department import Department, DepartmentName
from app.domain.mission import MissionStatus
from app.domain.task import Task, TaskStatus
from app.domain.workflow import Workflow
from app.schemas.company import (
    CompanyCEOSchema,
    CompanyDepartmentSchema,
    CompanyDetailResponse,
    CreateCompanyResponse,
    CreationEventSchema,
    WorkflowPreviewSchema,
    WorkflowTaskPreviewSchema,
)
from app.stores.company_session import CompanySession

_DEPARTMENT_IDS: dict[DepartmentName, str] = {
    DepartmentName.RESEARCH: "research",
    DepartmentName.BRAND: "brand",
    DepartmentName.SCRIPTS: "scripts",
    DepartmentName.VIDEO: "video",
    DepartmentName.PUBLISHING: "publishing",
    DepartmentName.GROWTH: "growth",
}

_CREATION_EVENT_DEFINITIONS: tuple[tuple[str, str, str, str, str | None], ...] = (
    ("ceo-assigned", "CEO_ASSIGNED", "AI CEO", "Analyzing mission...", None),
    ("research-ready", "RESEARCH_READY", "Research Department", "Assembling team...", "research"),
    ("brand-ready", "BRAND_READY", "Brand Department", "Assembling team...", "brand"),
    ("scripts-ready", "SCRIPTS_READY", "Script Department", "Assembling team...", "scripts"),
    ("video-ready", "VIDEO_READY", "Video Department", "Assembling team...", "video"),
    ("publishing-ready", "PUBLISHING_READY", "Publishing Department", "Assembling team...", "publishing"),
    ("growth-ready", "GROWTH_READY", "Growth Department", "Assembling team...", "growth"),
    ("workflow-created", "WORKFLOW_CREATED", "Workflow", "Execution pipeline ready", None),
)


class CompanyPresenter:
    """Maps stored company sessions to gateway-compatible API payloads."""

    def to_create_response(self, session: CompanySession) -> CreateCompanyResponse:
        workflow = self.to_workflow_preview(session)
        timestamp = session.created_at.isoformat()

        return CreateCompanyResponse(
            companyId=str(session.company_id),
            missionId=str(session.mission.id),
            missionTitle=session.mission.title,
            missionDescription=session.mission.description,
            missionStatus=_format_mission_status(session.mission.status),
            ceo=self.to_ceo_schema(session),
            departments=self.to_departments(session.departments),
            workflow=workflow,
            currentTask=workflow.current_task,
            creationEvents=self.to_creation_events(session, timestamp),
        )

    def to_company_detail(self, session: CompanySession) -> CompanyDetailResponse:
        return CompanyDetailResponse(
            companyId=str(session.company_id),
            missionId=str(session.mission.id),
            missionTitle=session.mission.title,
            missionDescription=session.mission.description,
            missionStatus=_format_mission_status(session.mission.status),
            ceo=self.to_ceo_schema(session),
            departments=self.to_departments(session.departments),
            workflow=self.to_workflow_preview(session),
        )

    def to_ceo_schema(self, session: CompanySession) -> CompanyCEOSchema:
        return CompanyCEOSchema(
            id=str(session.ceo.id),
            name=session.ceo.name,
            status="Executing" if session.started else "Planning",
            summary=(
                "Strategic plan approved. Workflow execution is underway."
                if session.started
                else "Mission analyzed. Departments assembled and ready to execute."
            ),
        )

    def to_departments(
        self,
        departments: tuple[Department, ...],
    ) -> list[CompanyDepartmentSchema]:
        return [
            CompanyDepartmentSchema(
                id=_DEPARTMENT_IDS[department.name],
                name=department.name.value,
                status="Ready",
                description="Department operational",
            )
            for department in departments
            if department.name is not DepartmentName.CEO
        ]

    def to_workflow_preview(self, session: CompanySession) -> WorkflowPreviewSchema:
        return self._workflow_to_preview(session.workflow)

    def _workflow_to_preview(self, workflow: Workflow) -> WorkflowPreviewSchema:
        available = workflow.next_available_tasks()
        current_task = available[0] if available else workflow.tasks[0]
        tasks = [
            self._task_to_preview(task, is_current=task.id == current_task.id)
            for task in workflow.tasks
        ]
        current_preview = self._task_to_preview(current_task, is_current=True)

        return WorkflowPreviewSchema(
            id=str(workflow.id),
            title="Mission execution workflow",
            tasks=tasks,
            currentTask=current_preview,
        )

    def _task_to_preview(self, task: Task, *, is_current: bool) -> WorkflowTaskPreviewSchema:
        return WorkflowTaskPreviewSchema(
            id=str(task.id),
            title=task.title,
            status=_format_task_status(task.status, is_current=is_current),
            description=task.description,
            department=_department_id(task.department),
        )

    def to_creation_events(
        self,
        session: CompanySession,
        timestamp: str,
    ) -> list[CreationEventSchema]:
        events = [
            CreationEventSchema(
                id=event_id,
                type=event_type,
                title=title,
                description=description,
                status="completed",
                department=department,
                timestamp=timestamp,
            )
            for event_id, event_type, title, description, department in _CREATION_EVENT_DEFINITIONS
        ]

        first_task = session.workflow.next_available_tasks()[0]
        events.append(
            CreationEventSchema(
                id="first-task-ready",
                type="FIRST_TASK_READY",
                title=first_task.title,
                description="Ready to execute",
                status="completed",
                department=_department_id(first_task.department),
                timestamp=timestamp,
            ),
        )
        return events


def _department_id(department: DepartmentName) -> str:
    return _DEPARTMENT_IDS.get(department, department.value.lower())


def _format_mission_status(status: MissionStatus) -> str:
    return status.value.replace("_", " ").title()


def _format_task_status(status: TaskStatus, *, is_current: bool) -> str:
    if is_current and status in {TaskStatus.CREATED, TaskStatus.QUEUED}:
        return "Ready to execute"
    if status is TaskStatus.QUEUED:
        return "Queued"
    if status is TaskStatus.IN_PROGRESS:
        return "In progress"
    if status is TaskStatus.COMPLETED:
        return "Completed"
    if status is TaskStatus.WAITING_APPROVAL:
        return "Waiting approval"
    if status is TaskStatus.CANCELLED:
        return "Cancelled"
    return status.value.replace("_", " ").title()
