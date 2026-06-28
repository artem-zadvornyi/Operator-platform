"""Registry for discovering and resolving AI provider implementations."""

from dataclasses import dataclass, field

from app.providers.base import AIProvider


@dataclass
class ProviderRegistry:
    """In-memory registry mapping provider names to provider instances."""

    _providers: dict[str, AIProvider] = field(default_factory=dict)

    def register(self, provider: AIProvider) -> None:
        """Register a provider by its declared name."""
        provider_name = provider.name().strip()
        if not provider_name:
            msg = "Provider name must not be empty."
            raise ValueError(msg)
        if provider_name in self._providers:
            msg = f"Provider '{provider_name}' is already registered."
            raise ValueError(msg)
        self._providers[provider_name] = provider

    def lookup(self, name: str) -> AIProvider:
        """Return a registered provider by name."""
        provider_name = name.strip()
        provider = self._providers.get(provider_name)
        if provider is None:
            msg = f"Provider '{provider_name}' is not registered."
            raise KeyError(msg)
        return provider

    def names(self) -> tuple[str, ...]:
        """Return registered provider names in insertion order."""
        return tuple(self._providers.keys())

    def __len__(self) -> int:
        return len(self._providers)
