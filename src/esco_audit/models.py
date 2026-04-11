"""Helpers for creating audit entries from events."""

from __future__ import annotations

from uuid import uuid4
from typing import Iterable, Tuple

from esco_contracts.models import AuditEntry, EventEnvelope


def build_audit_entry_from_event(
    event: EventEnvelope,
    *,
    category: str = "audit.entry_created",
    visibility: str = "internal_restricted",
    redaction_level: str = "none",
    summary: str | None = None,
    linked_ids: Iterable[str] | None = None,
) -> AuditEntry:
    """Create an `AuditEntry` from an `EventEnvelope`.

    This is intentionally simple: audit entries are small, derived summaries
    of events that are safe to persist in an append-only store.
    """
    audit_id = str(uuid4())
    summary_text = summary or f"Audit entry for event {event.event_type}"
    linked: Tuple[str, ...] = tuple(linked_ids) if linked_ids else tuple()
    return AuditEntry(
        audit_entry_id=audit_id,
        event_id=event.event_id,
        category=category,
        visibility=visibility,  # type: ignore[arg-type]
        redaction_level=redaction_level,  # type: ignore[arg-type]
        summary=summary_text,
        linked_ids=linked,
    )
