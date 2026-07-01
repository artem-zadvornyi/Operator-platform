"""Maps a free-form business idea into structured company and mission inputs."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class IdeaMapping:
    """Structured inputs derived from a user's business idea."""

    company_name: str
    business_goal: str
    target_audience: str
    platforms: tuple[str, ...]
    content_style: str
    languages: tuple[str, ...]
    tone_of_voice: str
    publishing_frequency: str
    mission_title: str
    mission_description: str
    mission_goal: str
    mission_target_audience: str


MOCK_FAILURE_IDEA = "__operator_fail__"


def map_idea(idea: str) -> IdeaMapping:
    """Convert a single idea string into domain-ready company and mission fields."""
    trimmed = idea.strip()

    return IdeaMapping(
        company_name=_truncate(trimmed, 80) or "New Company",
        business_goal=f"Build a content business around: {trimmed}",
        target_audience="Audience aligned with the stated business idea.",
        platforms=("YouTube", "TikTok"),
        content_style="Educational short-form content with clear, practical delivery.",
        languages=("English",),
        tone_of_voice="Clear, confident, and practical.",
        publishing_frequency="Three posts per week.",
        mission_title=trimmed,
        mission_description=f"Operator will assemble an AI company around: {trimmed}",
        mission_goal=f"Launch and grow a content business for: {trimmed}",
        mission_target_audience="Audience aligned with the stated business idea.",
    )


def _truncate(value: str, max_length: int) -> str:
    if len(value) <= max_length:
        return value
    return value[: max_length - 3].rstrip() + "..."
