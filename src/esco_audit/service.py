"""Audit service that writes audit entries to an AuditStore."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from esco_contracts.models import AuditEntry, EventEnvelope

from .interfaces import AuditStore
from .models import build_audit_entry_from_event


@dataclass(slots=True)
class AuditService:
    store: AuditStore
    service_actor_id: str = "esco-audit"

    def record(self, entry: AuditEntry) -> None:
        """Persist a pre-built `AuditEntry` to the underlying store."""
        self.store.append(entry)

    def record_from_event(
        self,
        event: EventEnvelope,
        *,
        category: str = "audit.entry_created",
        visibility: str = "internal_restricted",
        redaction_level: str = "none",
        summary: str | None = None,
        linked_ids: tuple[str, ...] | None = None,
    ) -> AuditEntry:
        """Build an `AuditEntry` from an `EventEnvelope` and persist it.

        Returns the created `AuditEntry` for downstream use.
        """
        entry = build_audit_entry_from_event(
            event,
            category=category,
            visibility=visibility,
            redaction_level=redaction_level,
            summary=summary,
            linked_ids=linked_ids,
        )
        self.record(entry)
        return entry
