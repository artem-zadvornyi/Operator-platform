from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest

from app.domain import DepartmentName, ExecutionMode, Task, TaskPriority
from app.domain.execution_strategy import ExecutionPlan
from app.providers import (
    AIProvider,
    GenerationRequest,
    GenerationResponse,
    ProviderHealth,
    ProviderRegistry,
    TokenUsage,
)
from app.providers.base import FUTURE_PROVIDER_NAMES


def _timestamp() -> datetime:
    return datetime(2027, 1, 1, 9, 0, tzinfo=UTC)


def _task() -> Task:
    return Task.create(
        title="Research niche",
        description="Validate audience demand and competitor landscape.",
        department=DepartmentName.RESEARCH,
        priority=TaskPriority.HIGH,
        created_at=_timestamp(),
    )


def _execution_plan(task: Task, employee_id: UUID | None = None) -> ExecutionPlan:
    employee_uuid = employee_id or uuid4()
    return ExecutionPlan.create(
        task=task,
        employee_id=employee_uuid,
        strategy_name="deterministic",
        execution_mode=ExecutionMode.DETERMINISTIC,
        estimated_duration=timedelta(minutes=20),
        requires_memory=True,
        requires_human_review=False,
        artifact_type="research_brief",
    )


def _generation_request(**overrides: object) -> GenerationRequest:
    task = _task()
    employee_id = uuid4()
    defaults: dict[str, object] = {
        "mission_context": "Build a finance media business on YouTube.",
        "employee_context": "Research Analyst — Audience Researcher",
        "memory_context": "Prior research notes on personal finance audiences.",
        "task": task,
        "execution_plan": _execution_plan(task, employee_id),
        "temperature": 0.2,
        "max_tokens": 1024,
    }
    defaults.update(overrides)
    return GenerationRequest(**defaults)


class _StubProvider(AIProvider):
    """Test double implementing the provider protocol."""

    def __init__(self, provider_name: str, *, supported_modes: set[ExecutionMode]) -> None:
        self._name = provider_name
        self._supported_modes = supported_modes

    def name(self) -> str:
        return self._name

    def supports_execution_mode(self, mode: ExecutionMode) -> bool:
        return mode in self._supported_modes

    def generate(self, request: GenerationRequest) -> GenerationResponse:
        return GenerationResponse(
            content=f"Generated output for {request.task.title}",
            usage=TokenUsage(prompt_tokens=10, completion_tokens=20, total_tokens=30),
            latency_ms=120,
            provider_name=self._name,
            model_name=f"{self._name}-test-model",
            metadata={"artifact_type": request.execution_plan.artifact_type},
        )

    def health(self) -> ProviderHealth:
        return ProviderHealth(
            provider=self._name,
            available=True,
            reason="",
            checked_at=_timestamp(),
        )


def test_ai_provider_protocol_validation() -> None:
    provider = _StubProvider("mock", supported_modes={ExecutionMode.LLM})

    assert isinstance(provider, AIProvider)
    assert provider.name() == "mock"
    assert provider.supports_execution_mode(ExecutionMode.LLM) is True
    assert provider.supports_execution_mode(ExecutionMode.DETERMINISTIC) is False

    response = provider.generate(_generation_request())
    assert response.provider_name == "mock"
    assert response.model_name == "mock-test-model"

    health = provider.health()
    assert health.available is True
    assert health.provider == "mock"


def test_provider_registry_registration_and_lookup() -> None:
    registry = ProviderRegistry()
    provider = _StubProvider("mock", supported_modes={ExecutionMode.LLM, ExecutionMode.HYBRID})

    registry.register(provider)

    assert len(registry) == 1
    assert registry.names() == ("mock",)
    assert registry.lookup("mock") is provider


def test_provider_registry_duplicate_protection() -> None:
    registry = ProviderRegistry()
    registry.register(_StubProvider("mock", supported_modes={ExecutionMode.LLM}))

    with pytest.raises(ValueError, match="already registered"):
        registry.register(_StubProvider("mock", supported_modes={ExecutionMode.LLM}))


def test_provider_registry_lookup_missing_provider() -> None:
    registry = ProviderRegistry()

    with pytest.raises(KeyError, match="not registered"):
        registry.lookup("openai")


def test_generation_request_validation() -> None:
    request = _generation_request()

    assert request.mission_context.startswith("Build a finance")
    assert request.task.department is DepartmentName.RESEARCH
    assert request.execution_plan.task_id == request.task.id


def test_generation_request_rejects_invalid_temperature() -> None:
    with pytest.raises(ValueError, match="Temperature"):
        _generation_request(temperature=2.5)


def test_generation_request_rejects_invalid_max_tokens() -> None:
    with pytest.raises(ValueError, match="Max tokens"):
        _generation_request(max_tokens=0)


def test_generation_request_rejects_task_plan_mismatch() -> None:
    task = _task()
    mismatched_plan = _execution_plan(_task())

    with pytest.raises(ValueError, match="task_id must match"):
        GenerationRequest(
            mission_context="Mission",
            employee_context="Employee",
            memory_context="Memory",
            task=task,
            execution_plan=mismatched_plan,
            temperature=0.2,
            max_tokens=512,
        )


def test_generation_response_validation() -> None:
    response = GenerationResponse(
        content="Research brief content",
        usage=TokenUsage(prompt_tokens=5, completion_tokens=15, total_tokens=20),
        latency_ms=95,
        provider_name="mock",
        model_name="mock-v1",
        metadata={"mode": "llm"},
    )

    assert response.metadata["mode"] == "llm"
    assert response.usage.total_tokens == 20


def test_generation_response_rejects_invalid_usage() -> None:
    with pytest.raises(ValueError, match="Total tokens"):
        TokenUsage(prompt_tokens=5, completion_tokens=15, total_tokens=21)


def test_provider_health_creation() -> None:
    available = ProviderHealth(
        provider="mock",
        available=True,
        reason="",
        checked_at=_timestamp(),
    )
    unavailable = ProviderHealth(
        provider="openai",
        available=False,
        reason="API key not configured",
        checked_at=_timestamp(),
    )

    assert available.available is True
    assert unavailable.reason == "API key not configured"


def test_provider_health_rejects_unavailable_without_reason() -> None:
    with pytest.raises(ValueError, match="must include a reason"):
        ProviderHealth(
            provider="openai",
            available=False,
            reason=" ",
            checked_at=_timestamp(),
        )


def test_future_provider_names_document_planned_integrations() -> None:
    assert FUTURE_PROVIDER_NAMES == ("openai", "claude", "gemini", "local", "mock")
