"""AI provider protocol — contract for all provider implementations."""

from abc import ABC, abstractmethod

from app.domain.execution_strategy import ExecutionMode
from app.providers.types import GenerationRequest, GenerationResponse, ProviderHealth

FUTURE_PROVIDER_NAMES: tuple[str, ...] = (
    "openai",
    "claude",
    "gemini",
    "local",
    "mock",
)


class AIProvider(ABC):
    """Abstract contract every AI provider must implement."""

    @abstractmethod
    def name(self) -> str:
        """Return the stable registry identifier for this provider."""

    @abstractmethod
    def supports_execution_mode(self, mode: ExecutionMode) -> bool:
        """Return whether this provider can serve the given execution mode."""

    @abstractmethod
    def generate(self, request: GenerationRequest) -> GenerationResponse:
        """Generate content for a prepared execution request."""

    @abstractmethod
    def health(self) -> ProviderHealth:
        """Return the current availability status of this provider."""
