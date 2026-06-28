"""Company blueprint aggregate — the source of truth for an Operator workspace."""

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4

from app.domain.company import BusinessStatus
from app.domain.department import (
    STANDARD_DEPARTMENT_DEFINITIONS,
    STANDARD_DEPARTMENT_NAMES,
    Department,
    DepartmentDefinition,
    DepartmentName,
    DepartmentStatus,
)
from app.domain.employee import Employee, EmployeeStatus


@dataclass(frozen=True, slots=True)
class CompanyBlueprint:
    """Aggregate root describing a complete AI-operated content business."""

    id: UUID
    company_name: str
    business_goal: str
    target_audience: str
    platforms: tuple[str, ...]
    content_style: str
    languages: tuple[str, ...]
    tone_of_voice: str
    publishing_frequency: str
    business_status: BusinessStatus
    departments: tuple[Department, ...]
    created_at: datetime

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "platforms",
            tuple(platform.strip() for platform in self.platforms),
        )
        object.__setattr__(
            self,
            "languages",
            tuple(language.strip() for language in self.languages),
        )
        object.__setattr__(self, "departments", tuple(self.departments))
        self._validate()

    @classmethod
    def create(
        cls,
        *,
        company_name: str,
        business_goal: str,
        target_audience: str,
        platforms: tuple[str, ...],
        content_style: str,
        languages: tuple[str, ...],
        tone_of_voice: str,
        publishing_frequency: str,
        business_status: BusinessStatus = BusinessStatus.PLANNING,
        blueprint_id: UUID | None = None,
        created_at: datetime | None = None,
    ) -> "CompanyBlueprint":
        """Generate a new business blueprint with the standard company structure."""
        timestamp = created_at or datetime.now(UTC)
        identifier = blueprint_id or uuid4()
        departments = _build_standard_departments(timestamp)

        return cls(
            id=identifier,
            company_name=company_name.strip(),
            business_goal=business_goal.strip(),
            target_audience=target_audience.strip(),
            platforms=platforms,
            content_style=content_style.strip(),
            languages=languages,
            tone_of_voice=tone_of_voice.strip(),
            publishing_frequency=publishing_frequency.strip(),
            business_status=business_status,
            departments=departments,
            created_at=timestamp,
        )

    @property
    def ceo(self) -> Employee:
        """Return the single CEO employee for this company."""
        ceo_department = self.get_department(DepartmentName.CEO)
        if len(ceo_department.employees) != 1:
            msg = "Company blueprint must contain exactly one CEO employee."
            raise ValueError(msg)
        return ceo_department.employees[0]

    @property
    def employees(self) -> tuple[Employee, ...]:
        """Return every employee across all departments."""
        return tuple(
            employee for department in self.departments for employee in department.employees
        )

    def get_department(self, name: DepartmentName) -> Department:
        """Return a department by its canonical name."""
        for department in self.departments:
            if department.name is name:
                return department
        msg = f"Department {name.value} not found in blueprint."
        raise KeyError(msg)

    def _validate(self) -> None:
        if not self.company_name.strip():
            msg = "Company name must not be empty."
            raise ValueError(msg)
        if not self.business_goal.strip():
            msg = "Business goal must not be empty."
            raise ValueError(msg)
        if not self.target_audience.strip():
            msg = "Target audience must not be empty."
            raise ValueError(msg)
        if not self.platforms:
            msg = "At least one platform must be defined."
            raise ValueError(msg)
        if not self.content_style.strip():
            msg = "Content style must not be empty."
            raise ValueError(msg)
        if not self.languages:
            msg = "At least one language must be defined."
            raise ValueError(msg)
        if not self.tone_of_voice.strip():
            msg = "Tone of voice must not be empty."
            raise ValueError(msg)
        if not self.publishing_frequency.strip():
            msg = "Publishing frequency must not be empty."
            raise ValueError(msg)

        department_names = {department.name for department in self.departments}
        if department_names != set(STANDARD_DEPARTMENT_NAMES):
            msg = "Blueprint must contain exactly the standard Operator departments."
            raise ValueError(msg)

        ceo_employees = [
            employee for employee in self.employees if employee.department is DepartmentName.CEO
        ]
        if len(ceo_employees) != 1:
            msg = "Blueprint must contain exactly one CEO employee."
            raise ValueError(msg)


def _build_standard_departments(created_at: datetime) -> tuple[Department, ...]:
    return tuple(
        _build_department(definition, created_at)
        for definition in STANDARD_DEPARTMENT_DEFINITIONS.values()
    )


def _build_department(definition: DepartmentDefinition, created_at: datetime) -> Department:
    employee = _build_default_employee(definition.name, created_at)
    return Department(
        name=definition.name,
        purpose=definition.purpose,
        responsibilities=definition.responsibilities,
        current_status=DepartmentStatus.IDLE,
        employees=(employee,),
    )


def _build_default_employee(department: DepartmentName, created_at: datetime) -> Employee:
    role_by_department: dict[DepartmentName, str] = {
        DepartmentName.CEO: "Chief Executive Officer",
        DepartmentName.RESEARCH: "Research Specialist",
        DepartmentName.BRAND: "Brand Strategist",
        DepartmentName.SCRIPTS: "Script Writer",
        DepartmentName.VIDEO: "Video Producer",
        DepartmentName.PUBLISHING: "Publishing Coordinator",
        DepartmentName.GROWTH: "Growth Analyst",
    }
    name_by_department: dict[DepartmentName, str] = {
        DepartmentName.CEO: "AI CEO",
        DepartmentName.RESEARCH: "Research Employee",
        DepartmentName.BRAND: "Brand Employee",
        DepartmentName.SCRIPTS: "Script Employee",
        DepartmentName.VIDEO: "Video Employee",
        DepartmentName.PUBLISHING: "Publishing Employee",
        DepartmentName.GROWTH: "Growth Employee",
    }

    return Employee(
        id=uuid4(),
        name=name_by_department[department],
        department=department,
        role=role_by_department[department],
        status=EmployeeStatus.IDLE,
        memory_reference="",
        created_at=created_at,
    )
