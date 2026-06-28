"""Immutable value objects for AI provider requests and responses."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from types import MappingProxyType

from app.domain.execution_strategy import ExecutionPlan
from app.domain.task import Task

MAX_GENERATION_TEMPERATURE = 2.0


@dataclass(frozen=True, slots=True)
class TokenUsage:
    """Token accounting returned by a provider generation call."""

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

    def __post_init__(self) -> None:
        if self.prompt_tokens < 0:
            msg = "Prompt token count must not be negative."
            raise ValueError(msg)
        if self.completion_tokens < 0:
            msg = "Completion token count must not be negative."
            raise ValueError(msg)
        if self.total_tokens < 0:
            msg = "Total token count must not be negative."
            raise ValueError(msg)
        if self.total_tokens != self.prompt_tokens + self.completion_tokens:
            msg = "Total tokens must equal prompt tokens plus completion tokens."
            raise ValueError(msg)


@dataclass(frozen=True, slots=True)
class GenerationRequest:
    """Immutable input passed to a provider for content generation."""

    mission_context: str
    employee_context: str
    memory_context: str
    task: Task
    execution_plan: ExecutionPlan
    temperature: float
    max_tokens: int

    def __post_init__(self) -> None:
        if not 0.0 <= self.temperature <= MAX_GENERATION_TEMPERATURE:
            msg = f"Temperature must be between 0.0 and {MAX_GENERATION_TEMPERATURE}."
            raise ValueError(msg)
        if self.max_tokens <= 0:
            msg = "Max tokens must be a positive integer."
            raise ValueError(msg)
        if self.execution_plan.task_id != self.task.id:
            msg = "Execution plan task_id must match the request task."
            raise ValueError(msg)


@dataclass(frozen=True, slots=True)
class GenerationResponse:
    """Immutable output returned by a provider generation call."""

    content: str
    usage: TokenUsage
    latency_ms: int
    provider_name: str
    model_name: str
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))
        if not self.content.strip():
            msg = "Generation response content must not be empty."
            raise ValueError(msg)
        if not self.provider_name.strip():
            msg = "Generation response provider name must not be empty."
            raise ValueError(msg)
        if not self.model_name.strip():
            msg = "Generation response model name must not be empty."
            raise ValueError(msg)
        if self.latency_ms < 0:
            msg = "Generation response latency must not be negative."
            raise ValueError(msg)


@dataclass(frozen=True, slots=True)
class ProviderHealth:
    """Availability snapshot for a registered provider."""

    provider: str
    available: bool
    reason: str
    checked_at: datetime

    def __post_init__(self) -> None:
        if not self.provider.strip():
            msg = "Provider health provider name must not be empty."
            raise ValueError(msg)
        if not self.available and not self.reason.strip():
            msg = "Unavailable provider health must include a reason."
            raise ValueError(msg)
