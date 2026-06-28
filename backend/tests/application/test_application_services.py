from datetime import UTC, datetime, timedelta

import pytest

from app.application import (
    CompanyService,
    ExecutionService,
    MissionService,
)
from app.domain import (
    BusinessStatus,
    DecisionStatus,
    DepartmentName,
    DepartmentStatus,
    ExecutionStatus,
    MissionStatus,
    TaskStatus,
)


def _timestamp(offset_minutes: int = 0) -> datetime:
    return datetime(2027, 2, 1, 8, 0, tzinfo=UTC) + timedelta(minutes=offset_minutes)


def _company_kwargs() -> dict[str, object]:
    return {
        "company_name": "Northline Media",
        "business_goal": "Build a profitable faceless finance channel on YouTube.",
        "target_audience": "Young professionals learning personal finance.",
        "platforms": ("YouTube", "TikTok"),
        "content_style": "Educational short-form explainers with clean motion graphics.",
        "languages": ("English",),
        "tone_of_voice": "Clear, confident, and practical.",
        "publishing_frequency": "Three videos per week.",
        "created_at": _timestamp(),
    }


def _mission_kwargs() -> dict[str, object]:
    return {
        "title": "Build a finance media business",
        "description": "Create a durable content company around personal finance education.",
        "goal": "Reach 100k subscribers and sustainable ad revenue within 18 months.",
        "target_audience": "Young professionals learning money management.",
        "primary_platforms": ("YouTube", "TikTok"),
        "languages": ("English",),
        "status": MissionStatus.ACTIVE,
        "created_at": _timestamp(),
        "updated_at": _timestamp(),
    }


def test_company_service_builds_company() -> None:
    service = CompanyService()

    setup = service.create_company(**_company_kwargs())

    assert setup.blueprint.company_name == "Northline Media"
    assert setup.blueprint.business_status is BusinessStatus.PLANNING
    assert len(setup.departments) == len(setup.blueprint.departments)
    assert all(
        department.current_status is DepartmentStatus.ACTIVE for department in setup.departments
    )
    assert setup.blueprint.ceo.department is DepartmentName.CEO


def test_company_service_initialize_departments_preserves_domain_structure() -> None:
    service = CompanyService()
    blueprint = service.create_blueprint(**_company_kwargs())

    departments = service.initialize_departments(blueprint)

    assert len(departments) == 7
    assert {department.name for department in departments} == {
        department.name for department in blueprint.departments
    }


def test_mission_service_starts_company() -> None:
    mission_service = MissionService()
    mission = mission_service.create_mission(**_mission_kwargs())
    ceo = mission_service.create_ceo("AI CEO", created_at=_timestamp())

    result = mission_service.start_company(
        mission=mission,
        ceo=ceo,
        updated_at=_timestamp(1),
    )

    assert result.decision.status is DecisionStatus.APPROVED
    assert result.decision.id in result.mission.decision_ids
    assert result.ceo.current_mission_id == mission.id
    assert result.ceo.decision_ids == (result.decision.id,)


def test_execution_service_produces_first_execution() -> None:
    mission_service = MissionService()
    execution_service = ExecutionService()
    company_service = CompanyService()

    company = company_service.create_company(**_company_kwargs())
    mission = mission_service.create_mission(**_mission_kwargs())
    ceo = mission_service.create_ceo("AI CEO", created_at=_timestamp())
    start = mission_service.start_company(
        mission=mission,
        ceo=ceo,
        updated_at=_timestamp(1),
    )
    research_employee = company.blueprint.get_department(DepartmentName.RESEARCH).employees[0]

    result = execution_service.run_first_task_demo(
        mission=start.mission,
        decision=start.decision,
        employee=research_employee,
        started_at=_timestamp(2),
    )

    assert len(result.plan.steps) == 6
    assert result.task.status is TaskStatus.COMPLETED
    assert result.execution.status is ExecutionStatus.SUCCEEDED
    assert result.execution.result is not None
    assert result.task.result_reference == result.execution.result.artifact_reference
    assert result.execution_plan.employee_id == research_employee.id


def test_execution_service_create_workflow_delegates_to_pipeline() -> None:
    mission_service = MissionService()
    execution_service = ExecutionService()

    mission = mission_service.create_mission(**_mission_kwargs())
    ceo = mission_service.create_ceo("AI CEO", created_at=_timestamp())
    start = mission_service.start_company(
        mission=mission,
        ceo=ceo,
        updated_at=_timestamp(1),
    )

    workflow_setup = execution_service.create_workflow(start.decision)

    assert len(workflow_setup.workflow.tasks) == len(workflow_setup.plan.steps)
    assert workflow_setup.workflow.next_available_tasks()[0].department is DepartmentName.RESEARCH


def test_application_layer_does_not_duplicate_domain_validation() -> None:
    mission_service = MissionService()
    company_service = CompanyService()
    execution_service = ExecutionService()

    with pytest.raises(ValueError, match="Mission title must not be empty"):
        mission_service.create_mission(
            title=" ",
            description="Description",
            goal="Goal",
            target_audience="Audience",
            primary_platforms=("YouTube",),
            languages=("English",),
        )

    with pytest.raises(ValueError, match="Company name must not be empty"):
        company_service.create_blueprint(
            company_name=" ",
            business_goal="Goal",
            target_audience="Audience",
            platforms=("YouTube",),
            content_style="Style",
            languages=("English",),
            tone_of_voice="Tone",
            publishing_frequency="Weekly",
        )

    mission = mission_service.create_mission(**_mission_kwargs())
    ceo = mission_service.create_ceo("AI CEO", created_at=_timestamp())
    start = mission_service.start_company(
        mission=mission,
        ceo=ceo,
        updated_at=_timestamp(1),
    )
    brand_employee = (
        company_service.create_company(**_company_kwargs())
        .blueprint.get_department(DepartmentName.BRAND)
        .employees[0]
    )
    workflow = execution_service.create_workflow(start.decision).workflow
    research_task = workflow.next_available_tasks()[0]

    with pytest.raises(ValueError, match="belongs to"):
        execution_service.prepare_execution(research_task, brand_employee)
