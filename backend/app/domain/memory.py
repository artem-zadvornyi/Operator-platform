"""Memory domain model for hierarchical business knowledge in Operator."""

from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import TypeVar
from uuid import UUID, uuid4

from app.domain.department import DepartmentName


class MemoryImportance(StrEnum):
    """Relative significance of a memory entry."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


HIGH_PRIORITY_IMPORTANCE: frozenset[MemoryImportance] = frozenset(
    {MemoryImportance.HIGH, MemoryImportance.CRITICAL}
)

IMPORTANCE_ORDER: tuple[MemoryImportance, ...] = (
    MemoryImportance.CRITICAL,
    MemoryImportance.HIGH,
    MemoryImportance.MEDIUM,
    MemoryImportance.LOW,
)


@dataclass(frozen=True, slots=True)
class MemoryEntry:
    """A single knowledge item stored in company, department, or employee memory."""

    id: UUID
    title: str
    content: str
    category: str
    importance: MemoryImportance
    created_at: datetime
    updated_at: datetime
    tags: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "tags", tuple(tag.strip().lower() for tag in self.tags))
        if not self.title.strip():
            msg = "Memory entry title must not be empty."
            raise ValueError(msg)
        if not self.content.strip():
            msg = "Memory entry content must not be empty."
            raise ValueError(msg)
        if not self.category.strip():
            msg = "Memory entry category must not be empty."
            raise ValueError(msg)
        if len(self.tags) != len(set(self.tags)):
            msg = "Memory entry tags must be unique."
            raise ValueError(msg)

    @classmethod
    def create(
        cls,
        *,
        title: str,
        content: str,
        category: str,
        importance: MemoryImportance = MemoryImportance.MEDIUM,
        tags: tuple[str, ...] = (),
        entry_id: UUID | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> "MemoryEntry":
        """Create a validated memory entry."""
        timestamp = created_at or datetime.now(UTC)
        update_timestamp = updated_at or timestamp
        return cls(
            id=entry_id or uuid4(),
            title=title.strip(),
            content=content.strip(),
            category=category.strip(),
            importance=importance,
            created_at=timestamp,
            updated_at=update_timestamp,
            tags=tags,
        )


MemoryT = TypeVar("MemoryT", "CompanyMemory", "DepartmentMemory", "EmployeeMemory")


def _validate_unique_entry_ids(entries: tuple[MemoryEntry, ...]) -> None:
    entry_ids = [entry.id for entry in entries]
    if len(entry_ids) != len(set(entry_ids)):
        msg = "Memory entries must have unique identifiers."
        raise ValueError(msg)


def _add_entry(
    entries: tuple[MemoryEntry, ...],
    entry: MemoryEntry,
) -> tuple[MemoryEntry, ...]:
    if any(existing.id == entry.id for existing in entries):
        msg = f"Memory entry {entry.id} already exists."
        raise ValueError(msg)
    updated = (*entries, entry)
    _validate_unique_entry_ids(updated)
    return updated


def _remove_entry(
    entries: tuple[MemoryEntry, ...],
    entry_id: UUID,
    *,
    force: bool = False,
) -> tuple[MemoryEntry, ...]:
    entry = _get_entry(entries, entry_id)

    if entry.importance is MemoryImportance.CRITICAL and not force:
        msg = f"Critical memory entry {entry_id} cannot be removed without force."
        raise ValueError(msg)

    return tuple(existing for existing in entries if existing.id != entry_id)


def _get_entry(entries: tuple[MemoryEntry, ...], entry_id: UUID) -> MemoryEntry:
    for entry in entries:
        if entry.id == entry_id:
            return entry
    msg = f"Memory entry {entry_id} not found."
    raise KeyError(msg)


def _find_by_tag(entries: tuple[MemoryEntry, ...], tag: str) -> tuple[MemoryEntry, ...]:
    normalized_tag = tag.strip().lower()
    return tuple(entry for entry in entries if normalized_tag in entry.tags)


def _find_by_category(
    entries: tuple[MemoryEntry, ...],
    category: str,
) -> tuple[MemoryEntry, ...]:
    normalized_category = category.strip().lower()
    return tuple(
        entry for entry in entries if entry.category.strip().lower() == normalized_category
    )


def _high_priority_entries(entries: tuple[MemoryEntry, ...]) -> tuple[MemoryEntry, ...]:
    prioritized = [entry for entry in entries if entry.importance in HIGH_PRIORITY_IMPORTANCE]
    return tuple(sorted(prioritized, key=lambda entry: IMPORTANCE_ORDER.index(entry.importance)))


@dataclass(frozen=True, slots=True)
class CompanyMemory:
    """Company-wide memory for business knowledge, KPIs, CEO decisions, and global rules."""

    id: UUID
    entries: tuple[MemoryEntry, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "entries", tuple(self.entries))
        _validate_unique_entry_ids(self.entries)

    @classmethod
    def create(cls, memory_id: UUID | None = None) -> "CompanyMemory":
        """Create empty company memory."""
        return cls(id=memory_id or uuid4(), entries=())

    def add_entry(self, entry: MemoryEntry) -> "CompanyMemory":
        """Add a knowledge entry to company memory."""
        return CompanyMemory(id=self.id, entries=_add_entry(self.entries, entry))

    def remove_entry(self, entry_id: UUID, *, force: bool = False) -> "CompanyMemory":
        """Remove an entry from company memory."""
        return CompanyMemory(
            id=self.id,
            entries=_remove_entry(self.entries, entry_id, force=force),
        )

    def find_by_tag(self, tag: str) -> tuple[MemoryEntry, ...]:
        """Return entries matching a tag."""
        return _find_by_tag(self.entries, tag)

    def find_by_category(self, category: str) -> tuple[MemoryEntry, ...]:
        """Return entries matching a category."""
        return _find_by_category(self.entries, category)

    def high_priority_entries(self) -> tuple[MemoryEntry, ...]:
        """Return high and critical importance entries."""
        return _high_priority_entries(self.entries)

    def get_entry(self, entry_id: UUID) -> MemoryEntry:
        """Return a single entry by identifier."""
        return _get_entry(self.entries, entry_id)


@dataclass(frozen=True, slots=True)
class DepartmentMemory:
    """Department-scoped memory for knowledge, best practices, and reusable assets."""

    id: UUID
    department: DepartmentName
    entries: tuple[MemoryEntry, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "entries", tuple(self.entries))
        _validate_unique_entry_ids(self.entries)

    @classmethod
    def create(
        cls,
        department: DepartmentName,
        memory_id: UUID | None = None,
    ) -> "DepartmentMemory":
        """Create empty department memory."""
        return cls(id=memory_id or uuid4(), department=department, entries=())

    def add_entry(self, entry: MemoryEntry) -> "DepartmentMemory":
        """Add a knowledge entry to department memory."""
        return DepartmentMemory(
            id=self.id,
            department=self.department,
            entries=_add_entry(self.entries, entry),
        )

    def remove_entry(self, entry_id: UUID, *, force: bool = False) -> "DepartmentMemory":
        """Remove an entry from department memory."""
        return DepartmentMemory(
            id=self.id,
            department=self.department,
            entries=_remove_entry(self.entries, entry_id, force=force),
        )

    def find_by_tag(self, tag: str) -> tuple[MemoryEntry, ...]:
        """Return entries matching a tag."""
        return _find_by_tag(self.entries, tag)

    def find_by_category(self, category: str) -> tuple[MemoryEntry, ...]:
        """Return entries matching a category."""
        return _find_by_category(self.entries, category)

    def high_priority_entries(self) -> tuple[MemoryEntry, ...]:
        """Return high and critical importance entries."""
        return _high_priority_entries(self.entries)

    def get_entry(self, entry_id: UUID) -> MemoryEntry:
        """Return a single entry by identifier."""
        return _get_entry(self.entries, entry_id)


@dataclass(frozen=True, slots=True)
class EmployeeMemory:
    """Employee-scoped memory for experience, outputs, lessons, and preferences."""

    id: UUID
    employee_id: UUID
    entries: tuple[MemoryEntry, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "entries", tuple(self.entries))
        _validate_unique_entry_ids(self.entries)

    @classmethod
    def create(
        cls,
        employee_id: UUID,
        memory_id: UUID | None = None,
    ) -> "EmployeeMemory":
        """Create empty employee memory."""
        return cls(id=memory_id or uuid4(), employee_id=employee_id, entries=())

    def add_entry(self, entry: MemoryEntry) -> "EmployeeMemory":
        """Add a knowledge entry to employee memory."""
        return EmployeeMemory(
            id=self.id,
            employee_id=self.employee_id,
            entries=_add_entry(self.entries, entry),
        )

    def remove_entry(self, entry_id: UUID, *, force: bool = False) -> "EmployeeMemory":
        """Remove an entry from employee memory."""
        return EmployeeMemory(
            id=self.id,
            employee_id=self.employee_id,
            entries=_remove_entry(self.entries, entry_id, force=force),
        )

    def find_by_tag(self, tag: str) -> tuple[MemoryEntry, ...]:
        """Return entries matching a tag."""
        return _find_by_tag(self.entries, tag)

    def find_by_category(self, category: str) -> tuple[MemoryEntry, ...]:
        """Return entries matching a category."""
        return _find_by_category(self.entries, category)

    def high_priority_entries(self) -> tuple[MemoryEntry, ...]:
        """Return high and critical importance entries."""
        return _high_priority_entries(self.entries)

    def get_entry(self, entry_id: UUID) -> MemoryEntry:
        """Return a single entry by identifier."""
        return _get_entry(self.entries, entry_id)
