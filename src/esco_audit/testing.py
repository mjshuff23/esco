"""In-memory test doubles for the audit store."""

from __future__ import annotations

from typing import List, Tuple

from esco_contracts.models import AuditEntry


class InMemoryAuditStore:
    """Simple append-only in-memory audit store used for tests.

    - `append` raises `ValueError` on duplicate `audit_entry_id`.
    - `list` returns newest-first entries.
    """

    def __init__(self) -> None:
        self._entries: List[AuditEntry] = []

    def append(self, entry: AuditEntry) -> None:
        if any(e.audit_entry_id == entry.audit_entry_id for e in self._entries):
            raise ValueError("duplicate audit_entry_id")
        self._entries.append(entry)

    def list(self, *, limit: int = 100, offset: int = 0) -> Tuple[AuditEntry, ...]:
        # Return newest-first slice
        if offset < 0:
            offset = 0
        start = offset
        end = offset + limit
        return tuple(self._entries[::-1][start:end])
