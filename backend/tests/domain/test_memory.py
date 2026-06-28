from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from app.domain import (
    CompanyMemory,
    DepartmentMemory,
    DepartmentName,
    EmployeeMemory,
    MemoryEntry,
    MemoryImportance,
)


def _timestamp(offset_minutes: int = 0) -> datetime:
    return datetime(2026, 9, 1, 10, 0, tzinfo=UTC) + timedelta(minutes=offset_minutes)


def _entry(**overrides: object) -> MemoryEntry:
    defaults: dict[str, object] = {
        "title": "Audience research summary",
        "content": "Finance beginners respond best to short explainers under 8 minutes.",
        "category": "research",
        "importance": MemoryImportance.MEDIUM,
        "tags": ("audience", "youtube"),
        "created_at": _timestamp(),
        "updated_at": _timestamp(),
    }
    defaults.update(overrides)
    return MemoryEntry.create(**defaults)


def test_memory_entry_creation() -> None:
    entry = _entry()

    assert entry.title == "Audience research summary"
    assert entry.tags == ("audience", "youtube")


def test_memory_entry_rejects_empty_content() -> None:
    with pytest.raises(ValueError, match="content"):
        _entry(content="   ")


def test_memory_entry_rejects_duplicate_tags() -> None:
    with pytest.raises(ValueError, match="tags must be unique"):
        _entry(tags=("audience", "audience"))


def test_company_memory_add_and_find_by_tag() -> None:
    memory = CompanyMemory.create()
    entry = _entry(tags=("kpi", "revenue"))
    memory = memory.add_entry(entry)

    results = memory.find_by_tag("kpi")
    assert len(results) == 1
    assert results[0].id == entry.id


def test_department_memory_find_by_category() -> None:
    memory = DepartmentMemory.create(DepartmentName.BRAND)
    entry = _entry(category="brand-guidelines")
    memory = memory.add_entry(entry)

    results = memory.find_by_category("brand-guidelines")
    assert len(results) == 1
    assert results[0].category == "brand-guidelines"


def test_employee_memory_high_priority_entries() -> None:
    memory = EmployeeMemory.create(employee_id=uuid4())
    low = _entry(title="Minor note", importance=MemoryImportance.LOW)
    high = _entry(title="Key lesson", importance=MemoryImportance.HIGH)
    critical = _entry(title="Critical rule", importance=MemoryImportance.CRITICAL)
    memory = memory.add_entry(low).add_entry(high).add_entry(critical)

    prioritized = memory.high_priority_entries()
    assert [entry.importance for entry in prioritized] == [
        MemoryImportance.CRITICAL,
        MemoryImportance.HIGH,
    ]


def test_memory_rejects_duplicate_entry_ids() -> None:
    entry_id = uuid4()
    entry = _entry(entry_id=entry_id)
    memory = CompanyMemory.create().add_entry(entry)

    duplicate = _entry(entry_id=entry_id, title="Duplicate")
    with pytest.raises(ValueError, match="already exists"):
        memory.add_entry(duplicate)


def test_critical_entry_cannot_be_removed_without_force() -> None:
    entry = _entry(importance=MemoryImportance.CRITICAL)
    memory = CompanyMemory.create().add_entry(entry)

    with pytest.raises(ValueError, match="cannot be removed without force"):
        memory.remove_entry(entry.id)

    updated = memory.remove_entry(entry.id, force=True)
    assert updated.entries == ()


def test_non_critical_entry_can_be_removed() -> None:
    entry = _entry(importance=MemoryImportance.HIGH)
    memory = DepartmentMemory.create(DepartmentName.RESEARCH).add_entry(entry)

    updated = memory.remove_entry(entry.id)
    assert updated.entries == ()


def test_tag_search_is_case_insensitive() -> None:
    entry = _entry(tags=("BrandVoice",))
    memory = EmployeeMemory.create(employee_id=uuid4()).add_entry(entry)

    results = memory.find_by_tag("brandvoice")
    assert len(results) == 1
