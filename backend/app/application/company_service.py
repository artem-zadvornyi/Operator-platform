"""Company application service — orchestrates blueprint and department setup."""

from dataclasses import dataclass
from datetime import datetime

from app.domain.blueprint import CompanyBlueprint
from app.domain.company import BusinessStatus
from app.domain.department import Department, DepartmentStatus


@dataclass(frozen=True, slots=True)
class CompanySetup:
    """Result of creating and initializing a company."""

    blueprint: CompanyBlueprint
    departments: tuple[Department, ...]


@dataclass(frozen=True, slots=True)
class CompanyService:
    """Orchestrates company blueprint creation and department initialization."""

    def create_company(
        self,
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
        created_at: datetime | None = None,
    ) -> CompanySetup:
        """Create a company blueprint and initialize its departments."""
        blueprint = self.create_blueprint(
            company_name=company_name,
            business_goal=business_goal,
            target_audience=target_audience,
            platforms=platforms,
            content_style=content_style,
            languages=languages,
            tone_of_voice=tone_of_voice,
            publishing_frequency=publishing_frequency,
            business_status=business_status,
            created_at=created_at,
        )
        departments = self.initialize_departments(blueprint)
        return CompanySetup(blueprint=blueprint, departments=departments)

    def create_blueprint(
        self,
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
        created_at: datetime | None = None,
    ) -> CompanyBlueprint:
        """Delegate company structure creation to the domain blueprint."""
        return CompanyBlueprint.create(
            company_name=company_name,
            business_goal=business_goal,
            target_audience=target_audience,
            platforms=platforms,
            content_style=content_style,
            languages=languages,
            tone_of_voice=tone_of_voice,
            publishing_frequency=publishing_frequency,
            business_status=business_status,
            created_at=created_at,
        )

    def initialize_departments(self, blueprint: CompanyBlueprint) -> tuple[Department, ...]:
        """Activate every department defined on the company blueprint."""
        return tuple(
            Department(
                name=department.name,
                purpose=department.purpose,
                responsibilities=department.responsibilities,
                current_status=DepartmentStatus.ACTIVE,
                employees=department.employees,
            )
            for department in blueprint.departments
        )
