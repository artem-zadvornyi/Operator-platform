from datetime import UTC, datetime
from uuid import uuid4

import pytest

from app.domain import (
    STANDARD_DEPARTMENT_NAMES,
    BusinessStatus,
    CompanyBlueprint,
    Department,
    DepartmentName,
    DepartmentStatus,
    Employee,
    EmployeeStatus,
)


def _blueprint_kwargs() -> dict[str, object]:
    return {
        "company_name": "Northline Media",
        "business_goal": "Build a profitable faceless finance channel on YouTube.",
        "target_audience": "Young professionals learning personal finance.",
        "platforms": ("YouTube", "TikTok"),
        "content_style": "Educational short-form explainers with clean motion graphics.",
        "languages": ("English",),
        "tone_of_voice": "Clear, confident, and practical.",
        "publishing_frequency": "Three videos per week.",
    }


def test_blueprint_create_generates_standard_structure() -> None:
    blueprint = CompanyBlueprint.create(**_blueprint_kwargs())

    assert blueprint.company_name == "Northline Media"
    assert blueprint.business_status is BusinessStatus.PLANNING
    assert len(blueprint.departments) == len(STANDARD_DEPARTMENT_NAMES)
    department_names = {department.name for department in blueprint.departments}
    assert department_names == set(STANDARD_DEPARTMENT_NAMES)


def test_blueprint_create_assigns_metadata_fields() -> None:
    created_at = datetime(2026, 1, 15, 12, 0, tzinfo=UTC)
    blueprint_id = uuid4()

    blueprint = CompanyBlueprint.create(
        **_blueprint_kwargs(),
        business_status=BusinessStatus.ACTIVE,
        blueprint_id=blueprint_id,
        created_at=created_at,
    )

    assert blueprint.id == blueprint_id
    assert blueprint.created_at == created_at
    assert blueprint.business_status is BusinessStatus.ACTIVE
    assert blueprint.platforms == ("YouTube", "TikTok")
    assert blueprint.languages == ("English",)
    assert blueprint.publishing_frequency == "Three videos per week."


def test_department_creation_includes_purpose_and_responsibilities() -> None:
    blueprint = CompanyBlueprint.create(**_blueprint_kwargs())
    research = blueprint.get_department(DepartmentName.RESEARCH)

    assert research.name is DepartmentName.RESEARCH
    assert research.purpose
    assert len(research.responsibilities) >= 1
    assert research.current_status is DepartmentStatus.IDLE


def test_employee_creation_for_each_department() -> None:
    blueprint = CompanyBlueprint.create(**_blueprint_kwargs())

    assert len(blueprint.employees) == len(STANDARD_DEPARTMENT_NAMES)

    for department in blueprint.departments:
        assert department.employee_count == 1
        employee = department.employees[0]
        assert employee.department is department.name
        assert employee.status is EmployeeStatus.IDLE
        assert employee.memory_reference == ""
        assert employee.created_at == blueprint.created_at


def test_blueprint_has_exactly_one_ceo() -> None:
    blueprint = CompanyBlueprint.create(**_blueprint_kwargs())
    ceo = blueprint.ceo

    assert ceo.department is DepartmentName.CEO
    assert ceo.name == "AI CEO"
    assert ceo.role == "Chief Executive Officer"


def test_employee_department_relationship_is_enforced() -> None:
    timestamp = datetime(2026, 1, 15, 12, 0, tzinfo=UTC)
    employee = Employee(
        id=uuid4(),
        name="Research Employee",
        department=DepartmentName.RESEARCH,
        role="Research Specialist",
        status=EmployeeStatus.IDLE,
        memory_reference="",
        created_at=timestamp,
    )

    with pytest.raises(ValueError, match="belongs to"):
        Department(
            name=DepartmentName.BRAND,
            purpose="Own brand identity.",
            responsibilities=("Maintain guidelines",),
            current_status=DepartmentStatus.IDLE,
            employees=(employee,),
        )


def test_blueprint_rejects_missing_standard_department() -> None:
    timestamp = datetime(2026, 1, 15, 12, 0, tzinfo=UTC)
    incomplete_department = Department(
        name=DepartmentName.CEO,
        purpose="Lead the company.",
        responsibilities=("Set strategy",),
        current_status=DepartmentStatus.IDLE,
        employees=(
            Employee(
                id=uuid4(),
                name="AI CEO",
                department=DepartmentName.CEO,
                role="Chief Executive Officer",
                status=EmployeeStatus.IDLE,
                memory_reference="",
                created_at=timestamp,
            ),
        ),
    )

    with pytest.raises(ValueError, match="standard Operator departments"):
        CompanyBlueprint(
            id=uuid4(),
            company_name="Northline Media",
            business_goal="Grow on YouTube.",
            target_audience="Creators",
            platforms=("YouTube",),
            content_style="Educational",
            languages=("English",),
            tone_of_voice="Direct",
            publishing_frequency="Weekly",
            business_status=BusinessStatus.PLANNING,
            departments=(incomplete_department,),
            created_at=timestamp,
        )


def test_blueprint_rejects_empty_company_name() -> None:
    kwargs = _blueprint_kwargs()
    kwargs["company_name"] = "   "

    with pytest.raises(ValueError, match="Company name"):
        CompanyBlueprint.create(**kwargs)
