"""Audit store interfaces and protocols."""

from __future__ import annotations

from typing import Protocol, Tuple
from datetime import datetime

from esco_contracts.models import AuditEntry


class AuditStore(Protocol):
    """Protocol describing an append-only audit store.

    Implementations must ensure entries cannot be modified or deleted once
    appended.
    """

    def append(self, entry: AuditEntry) -> None:
        """Append an audit entry to the store.

        Implementations should raise on duplicate `audit_entry_id`.
        """

    def list(self, *, limit: int = 100, offset: int = 0) -> Tuple[AuditEntry, ...]:
        """List audit entries (newest first).

        Pagination is optional for simple in-memory implementations.
        """
