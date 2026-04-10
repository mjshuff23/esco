"""Phase 0 public contracts promoted into code constants."""

from typing import Final

SUPPORT_PROFILE_ROUTE: Final = "Support Profile"
EXPLORATION_ROUTE: Final = "Exploration"
CLARIFICATION_ROUTE: Final = "Clarification"
CONSEQUENCES_MODE: Final = "What happens if this is false?"

SUPPORT_PROFILE_FIELDS: Final = (
    "premise_validity",
    "source_convergence",
    "temporal_relevance",
    "internal_consistency",
    "counterevidence_presence",
)

DEFAULT_PRIMARY_MODEL_ID: Final = "ministral-8b-instruct"
DEFAULT_FALLBACK_MODEL_ID: Final = "gemma-4-e4b"

PROMPT_INJECTION_PATTERNS: Final = (
    "ignore previous instructions",
    "ignore prior instructions",
    "system prompt",
    "tool call",
    "developer message",
)
