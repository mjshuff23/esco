"""Unit tests for the `esco_audit` package."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from uuid import uuid4

import pytest

from esco_audit.testing import InMemoryAuditStore
from esco_audit.service import AuditService
from esco_contracts.models import AuditEntry


def make_entry(id: str | None = None) -> AuditEntry:
    return AuditEntry(
        audit_entry_id=id or str(uuid4()),
        event_id=str(uuid4()),
        category="test",
        visibility="internal_restricted",
        redaction_level="none",
        summary="unit test entry",
    )


def test_record_and_query_roundtrip() -> None:
    store = InMemoryAuditStore()
    svc = AuditService(store=store)
    entry = make_entry()
    svc.record(entry)
    items = store.list()
    assert len(items) == 1
    assert items[0].audit_entry_id == entry.audit_entry_id


def test_prevent_duplicate_append() -> None:
    store = InMemoryAuditStore()
    entry = make_entry("dup-id")
    store.append(entry)
    with pytest.raises(ValueError):
        store.append(entry)


def test_audit_entry_is_frozen() -> None:
    entry = make_entry()
    with pytest.raises(FrozenInstanceError):
        setattr(entry, "summary", "new summary")
