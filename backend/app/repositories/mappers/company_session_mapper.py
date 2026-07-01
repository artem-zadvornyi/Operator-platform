"""Maps between domain company sessions and SQLAlchemy persistence records."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from app.domain.assignment import Assignment
from app.domain.blueprint import CompanyBlueprint
from app.domain.ceo import AICEO, CEOStatus, StrategyMode
from app.domain.company import BusinessStatus
from app.domain.decision import Confidence, Decision, DecisionStatus, RiskLevel
from app.domain.department import Department, DepartmentName, DepartmentStatus
from app.domain.employee import Employee, EmployeeStatus
from app.domain.mission import Mission, MissionPriority, MissionStatus
from app.domain.plan import Plan, PlanStatus, PlanStep
from app.domain.task import Task, TaskPriority, TaskStatus
from app.domain.workflow import Workflow
from app.models.company_persistence import (
    CeoRecord,
    CompanyRecord,
    DecisionRecord,
    DepartmentRecord,
    MissionRecord,
    PlanRecord,
    PlanStepRecord,
    WorkflowAssignmentRecord,
    WorkflowRecord,
    WorkflowTaskRecord,
)
from app.stores.company_session import CompanySession


class CompanySessionPersistenceMapper:
    """Translates company sessions to and from ORM aggregates."""

    def to_record(self, session: CompanySession) -> CompanyRecord:
        company_id = session.company_id
        blueprint = session.blueprint

        record = CompanyRecord(
            id=company_id,
            company_name=blueprint.company_name,
            business_goal=blueprint.business_goal,
            target_audience=blueprint.target_audience,
            platforms=list(blueprint.platforms),
            content_style=blueprint.content_style,
            languages=list(blueprint.languages),
            tone_of_voice=blueprint.tone_of_voice,
            publishing_frequency=blueprint.publishing_frequency,
            business_status=blueprint.business_status.value,
            started=session.started,
            created_at=session.created_at,
            departments=[
                self._department_to_record(department, company_id)
                for department in session.departments
            ],
            mission=self._mission_to_record(session.mission, company_id),
            ceo=self._ceo_to_record(session.ceo, company_id),
            decision=self._decision_to_record(session.decision, company_id),
            plan=self._plan_to_record(session.plan, company_id),
            workflow=self._workflow_to_record(session.workflow, company_id),
        )
        return record

    def to_session(self, record: CompanyRecord) -> CompanySession:
        departments = tuple(self._department_from_record(item) for item in record.departments)
        blueprint = CompanyBlueprint(
            id=record.id,
            company_name=record.company_name,
            business_goal=record.business_goal,
            target_audience=record.target_audience,
            platforms=tuple(record.platforms),
            content_style=record.content_style,
            languages=tuple(record.languages),
            tone_of_voice=record.tone_of_voice,
            publishing_frequency=record.publishing_frequency,
            business_status=BusinessStatus(record.business_status),
            departments=departments,
            created_at=_ensure_utc(record.created_at),
        )

        if record.mission is None or record.ceo is None or record.decision is None:
            msg = f"Persisted company {record.id} is missing required aggregate data."
            raise ValueError(msg)
        if record.plan is None or record.workflow is None:
            msg = f"Persisted company {record.id} is missing plan or workflow data."
            raise ValueError(msg)

        return CompanySession(
            company_id=record.id,
            blueprint=blueprint,
            departments=departments,
            mission=self._mission_from_record(record.mission),
            ceo=self._ceo_from_record(record.ceo),
            decision=self._decision_from_record(record.decision),
            plan=self._plan_from_record(record.plan),
            workflow=self._workflow_from_record(record.workflow),
            started=record.started,
            created_at=_ensure_utc(record.created_at),
        )

    def _department_to_record(
        self,
        department: Department,
        company_id: uuid.UUID,
    ) -> DepartmentRecord:
        return DepartmentRecord(
            id=uuid.uuid4(),
            company_id=company_id,
            name=department.name.value,
            purpose=department.purpose,
            responsibilities=list(department.responsibilities),
            current_status=department.current_status.value,
            employees=[_employee_to_document(employee) for employee in department.employees],
        )

    def _department_from_record(self, record: DepartmentRecord) -> Department:
        return Department(
            name=DepartmentName(record.name),
            purpose=record.purpose,
            responsibilities=tuple(record.responsibilities),
            current_status=DepartmentStatus(record.current_status),
            employees=tuple(_employee_from_document(item) for item in record.employees),
        )

    def _mission_to_record(self, mission: Mission, company_id: uuid.UUID) -> MissionRecord:
        return MissionRecord(
            id=mission.id,
            company_id=company_id,
            title=mission.title,
            description=mission.description,
            goal=mission.goal,
            target_audience=mission.target_audience,
            primary_platforms=list(mission.primary_platforms),
            languages=list(mission.languages),
            priority=mission.priority.value,
            status=mission.status.value,
            decision_ids=[str(decision_id) for decision_id in mission.decision_ids],
            created_at=mission.created_at,
            updated_at=mission.updated_at,
        )

    def _mission_from_record(self, record: MissionRecord) -> Mission:
        return Mission(
            id=record.id,
            title=record.title,
            description=record.description,
            goal=record.goal,
            target_audience=record.target_audience,
            primary_platforms=tuple(record.primary_platforms),
            languages=tuple(record.languages),
            priority=MissionPriority(record.priority),
            status=MissionStatus(record.status),
            created_at=_ensure_utc(record.created_at),
            updated_at=_ensure_utc(record.updated_at),
            decision_ids=tuple(uuid.UUID(value) for value in record.decision_ids),
        )

    def _ceo_to_record(self, ceo: AICEO, company_id: uuid.UUID) -> CeoRecord:
        return CeoRecord(
            id=ceo.id,
            company_id=company_id,
            name=ceo.name,
            status=ceo.status.value,
            strategy_mode=ceo.strategy_mode.value,
            current_mission_id=ceo.current_mission_id,
            decision_ids=[str(decision_id) for decision_id in ceo.decision_ids],
            created_at=ceo.created_at,
            updated_at=ceo.updated_at,
        )

    def _ceo_from_record(self, record: CeoRecord) -> AICEO:
        return AICEO(
            id=record.id,
            name=record.name,
            status=CEOStatus(record.status),
            strategy_mode=StrategyMode(record.strategy_mode),
            created_at=_ensure_utc(record.created_at),
            updated_at=_ensure_utc(record.updated_at),
            current_mission_id=record.current_mission_id,
            decision_ids=tuple(uuid.UUID(value) for value in record.decision_ids),
        )

    def _decision_to_record(
        self,
        decision: Decision,
        company_id: uuid.UUID,
    ) -> DecisionRecord:
        return DecisionRecord(
            id=decision.id,
            company_id=company_id,
            title=decision.title,
            context=decision.context,
            rationale=decision.rationale,
            confidence_value=decision.confidence.value,
            risk_level=decision.risk_level.value,
            expected_outcome=decision.expected_outcome,
            status=decision.status.value,
            created_at=decision.created_at,
        )

    def _decision_from_record(self, record: DecisionRecord) -> Decision:
        return Decision(
            id=record.id,
            title=record.title,
            context=record.context,
            rationale=record.rationale,
            confidence=Confidence.create(record.confidence_value),
            risk_level=RiskLevel(record.risk_level),
            expected_outcome=record.expected_outcome,
            created_at=_ensure_utc(record.created_at),
            status=DecisionStatus(record.status),
        )

    def _plan_to_record(self, plan: Plan, company_id: uuid.UUID) -> PlanRecord:
        return PlanRecord(
            id=plan.id,
            company_id=company_id,
            decision_id=plan.decision_id,
            title=plan.title,
            summary=plan.summary,
            status=plan.status.value,
            created_at=plan.created_at,
            steps=[
                PlanStepRecord(
                    id=step.id,
                    plan_id=plan.id,
                    title=step.title,
                    description=step.description,
                    target_department=step.target_department.value,
                    priority=step.priority.value,
                    depends_on=[str(dependency) for dependency in step.depends_on],
                    position=index,
                )
                for index, step in enumerate(plan.steps)
            ],
        )

    def _plan_from_record(self, record: PlanRecord) -> Plan:
        return Plan(
            id=record.id,
            decision_id=record.decision_id,
            title=record.title,
            summary=record.summary,
            steps=tuple(self._plan_step_from_record(step) for step in record.steps),
            created_at=_ensure_utc(record.created_at),
            status=PlanStatus(record.status),
        )

    def _plan_step_from_record(self, record: PlanStepRecord) -> PlanStep:
        return PlanStep(
            id=record.id,
            title=record.title,
            description=record.description,
            target_department=DepartmentName(record.target_department),
            priority=TaskPriority(record.priority),
            depends_on=tuple(uuid.UUID(value) for value in record.depends_on),
        )

    def _workflow_to_record(
        self,
        workflow: Workflow,
        company_id: uuid.UUID,
    ) -> WorkflowRecord:
        return WorkflowRecord(
            id=workflow.id,
            company_id=company_id,
            created_at=workflow.created_at,
            tasks=[
                WorkflowTaskRecord(
                    id=task.id,
                    workflow_id=workflow.id,
                    title=task.title,
                    description=task.description,
                    created_at=task.created_at,
                    updated_at=task.updated_at,
                    status=task.status.value,
                    priority=task.priority.value,
                    department=task.department.value,
                    assigned_employee_id=task.assigned_employee,
                    depends_on=[str(dependency) for dependency in task.depends_on],
                    result_reference=task.result_reference,
                    position=index,
                )
                for index, task in enumerate(workflow.tasks)
            ],
            assignments=[
                WorkflowAssignmentRecord(
                    id=uuid.uuid4(),
                    workflow_id=workflow.id,
                    employee_id=assignment.employee,
                    task_id=assignment.task,
                    assigned_at=assignment.assigned_at,
                    accepted=assignment.accepted,
                )
                for assignment in workflow.assignments
            ],
        )

    def _workflow_from_record(self, record: WorkflowRecord) -> Workflow:
        workflow = Workflow(
            id=record.id,
            tasks=tuple(self._task_from_record(task) for task in record.tasks),
            assignments=tuple(self._assignment_from_record(item) for item in record.assignments),
            created_at=_ensure_utc(record.created_at),
        )
        workflow.validate_dependencies()
        return workflow

    def _task_from_record(self, record: WorkflowTaskRecord) -> Task:
        return Task(
            id=record.id,
            title=record.title,
            description=record.description,
            created_at=_ensure_utc(record.created_at),
            updated_at=_ensure_utc(record.updated_at),
            status=TaskStatus(record.status),
            priority=TaskPriority(record.priority),
            department=DepartmentName(record.department),
            assigned_employee=record.assigned_employee_id,
            depends_on=tuple(uuid.UUID(value) for value in record.depends_on),
            result_reference=record.result_reference,
        )

    def _assignment_from_record(self, record: WorkflowAssignmentRecord) -> Assignment:
        return Assignment(
            employee=record.employee_id,
            task=record.task_id,
            assigned_at=_ensure_utc(record.assigned_at),
            accepted=record.accepted,
        )


def _employee_to_document(employee: Employee) -> dict[str, str]:
    return {
        "id": str(employee.id),
        "name": employee.name,
        "department": employee.department.value,
        "role": employee.role,
        "status": employee.status.value,
        "memory_reference": employee.memory_reference,
        "created_at": employee.created_at.isoformat(),
    }


def _employee_from_document(document: dict[str, str]) -> Employee:
    return Employee(
        id=uuid.UUID(document["id"]),
        name=document["name"],
        department=DepartmentName(document["department"]),
        role=document["role"],
        status=EmployeeStatus(document["status"]),
        memory_reference=document["memory_reference"],
        created_at=datetime.fromisoformat(document["created_at"]),
    )


def _ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value
