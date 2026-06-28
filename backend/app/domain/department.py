"""Department domain model for organizational units inside a company blueprint."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domain.employee import Employee


class DepartmentName(StrEnum):
    """Canonical departments that compose every Operator content business."""

    CEO = "CEO"
    RESEARCH = "Research"
    BRAND = "Brand"
    SCRIPTS = "Scripts"
    VIDEO = "Video"
    PUBLISHING = "Publishing"
    GROWTH = "Growth"


class DepartmentStatus(StrEnum):
    """Operational state of a department within the company blueprint."""

    IDLE = "idle"
    ACTIVE = "active"
    WAITING = "waiting"
    COMPLETE = "complete"


STANDARD_DEPARTMENT_NAMES: tuple[DepartmentName, ...] = tuple(DepartmentName)


@dataclass(frozen=True, slots=True)
class DepartmentDefinition:
    """Template describing the purpose and responsibilities of a standard department."""

    name: DepartmentName
    purpose: str
    responsibilities: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Department:
    """A department within a company blueprint, owning zero or more employees."""

    name: DepartmentName
    purpose: str
    responsibilities: tuple[str, ...]
    current_status: DepartmentStatus
    employees: tuple[Employee, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "employees", tuple(self.employees))
        if not self.purpose.strip():
            msg = "Department purpose must not be empty."
            raise ValueError(msg)
        if not self.responsibilities:
            msg = "Department must define at least one responsibility."
            raise ValueError(msg)
        for employee in self.employees:
            if employee.department is not self.name:
                msg = (
                    f"Employee {employee.name!r} belongs to {employee.department.value}, "
                    f"not {self.name.value}."
                )
                raise ValueError(msg)

    @property
    def employee_count(self) -> int:
        return len(self.employees)


STANDARD_DEPARTMENT_DEFINITIONS: dict[DepartmentName, DepartmentDefinition] = {
    DepartmentName.CEO: DepartmentDefinition(
        name=DepartmentName.CEO,
        purpose=(
            "Lead the content business and coordinate all departments toward the business goal."
        ),
        responsibilities=(
            "Define company strategy and priorities",
            "Delegate work across departments",
            "Review outcomes and adjust the operating plan",
        ),
    ),
    DepartmentName.RESEARCH: DepartmentDefinition(
        name=DepartmentName.RESEARCH,
        purpose="Discover niches, audiences, and opportunities that support the business goal.",
        responsibilities=(
            "Analyze market trends and competitors",
            "Validate target audience assumptions",
            "Produce research briefs for other departments",
        ),
    ),
    DepartmentName.BRAND: DepartmentDefinition(
        name=DepartmentName.BRAND,
        purpose="Establish and maintain a consistent brand identity across all content.",
        responsibilities=(
            "Define visual and verbal brand guidelines",
            "Ensure content aligns with brand positioning",
            "Maintain brand assets and style references",
        ),
    ),
    DepartmentName.SCRIPTS: DepartmentDefinition(
        name=DepartmentName.SCRIPTS,
        purpose="Create written content and scripts aligned with brand and audience strategy.",
        responsibilities=(
            "Draft scripts and written content",
            "Adapt messaging to each platform",
            "Iterate based on research and performance feedback",
        ),
    ),
    DepartmentName.VIDEO: DepartmentDefinition(
        name=DepartmentName.VIDEO,
        purpose="Produce video content from approved scripts and brand guidelines.",
        responsibilities=(
            "Transform scripts into video assets",
            "Apply brand and style standards to production",
            "Prepare deliverables for publishing review",
        ),
    ),
    DepartmentName.PUBLISHING: DepartmentDefinition(
        name=DepartmentName.PUBLISHING,
        purpose="Schedule and distribute content across selected platforms.",
        responsibilities=(
            "Prepare platform-specific publishing packages",
            "Manage publishing cadence",
            "Route content for approval before release",
        ),
    ),
    DepartmentName.GROWTH: DepartmentDefinition(
        name=DepartmentName.GROWTH,
        purpose="Identify and act on opportunities to grow reach, engagement, and revenue.",
        responsibilities=(
            "Monitor content performance signals",
            "Recommend experiments and optimizations",
            "Surface growth opportunities to the CEO",
        ),
    ),
}
