"""Company-level domain concepts for Operator workspaces."""

from enum import StrEnum


class BusinessStatus(StrEnum):
    """Lifecycle state of a content business within Operator."""

    DRAFT = "draft"
    PLANNING = "planning"
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"
