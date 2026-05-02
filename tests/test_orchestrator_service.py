from __future__ import annotations

import unittest
from datetime import datetime, timezone
from typing import Iterable, cast

from tests import bootstrap  # noqa: F401

from esco_audit import AuditService
from esco_audit.models import build_audit_entry_from_event
from esco_audit.testing import InMemoryAuditStore
from esco_contracts.models import AuditEntry, EventEnvelope
from esco_orchestrator import OrchestratorService
from esco_policy import PolicyService
from esco_retrieval import IngestionArtifact, RetrievalService
from esco_retrieval.testing import (
    DeterministicEmbedder,
    InMemoryDocumentRepository,
    InMemoryVectorStore,
    SimpleParagraphChunker,
)
from esco_runtime import GroundedDraftAdapter, build_grounded_demo_config
from esco_verifier import VerificationService


class CapturingAuditService:
    def __init__(self) -> None:
        self.events: list[EventEnvelope] = []
        self.entries: list[AuditEntry] = []

    def record_from_event(
        self,
        event: EventEnvelope,
        *,
        category: str = "audit.entry_created",
        visibility: str = "internal_restricted",
        redaction_level: str = "none",
        summary: str | None = None,
        linked_ids: Iterable[str] | None = None,
    ) -> AuditEntry:
        self.events.append(event)
        entry = build_audit_entry_from_event(
            event,
            category=category,
            visibility=visibility,
            redaction_level=redaction_level,
            summary=summary,
            linked_ids=linked_ids,
        )
        self.entries.append(entry)
        return entry


class OrchestratorServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.retrieval = self._build_retrieval()
        self._seed_document(
            self.retrieval,
            (
                "ESCO keeps web search disabled in the early local-first MVP.\n\n"
                "Phase 2 includes verification, claim routing, and policy gating."
            ),
        )
        self.service = self._build_service(self.retrieval)

    def _build_retrieval(self) -> RetrievalService:
        return RetrievalService(
            repository=InMemoryDocumentRepository(),
            embedder=DeterministicEmbedder(),
            vector_store=InMemoryVectorStore(),
            chunker=SimpleParagraphChunker(),
        )

    def _build_service(
        self,
        retrieval: RetrievalService,
        *,
        audit: AuditService | None = None,
    ) -> OrchestratorService:
        return OrchestratorService(
            retrieval=retrieval,
            verifier=VerificationService(),
            policy=PolicyService(),
            runtime=GroundedDraftAdapter(config=build_grounded_demo_config()),
            audit=audit,
        )

    def _seed_document(self, retrieval: RetrievalService, raw_text: str) -> None:
        retrieval.ingest_document(
            IngestionArtifact(
                raw_text=raw_text,
                canonical_url="https://example.org/esco-status",
                publisher="Example Org",
                source_type="official_docs",
                license_ref="CC-BY-4.0",
                retrieved_at=datetime.now(timezone.utc),
                artifact_uri="file:///tmp/esco-status.md",
            )
        )

    def _build_audited_service(
        self,
        *,
        seed_text: str | None = (
            "ESCO keeps web search disabled in the early local-first MVP.\n\n"
            "Phase 2 includes verification, claim routing, and policy gating."
        ),
    ) -> tuple[OrchestratorService, InMemoryAuditStore]:
        retrieval = RetrievalService(
            repository=InMemoryDocumentRepository(),
            embedder=DeterministicEmbedder(),
            vector_store=InMemoryVectorStore(),
            chunker=SimpleParagraphChunker(),
        )
        if seed_text is not None:
            self._seed_document(retrieval, seed_text)
        audit_store = InMemoryAuditStore()
        return self._build_service(retrieval, audit=AuditService(audit_store)), audit_store

    def test_support_profile_prompt_returns_grounded_answer(self) -> None:
        outcome = self.service.handle_prompt("ESCO is local-first and web search is disabled in the MVP.")
        self.assertEqual(outcome.verification.route_decision.route, "Support Profile")
        self.assertGreaterEqual(len(outcome.evidence_records), 1)
        self.assertIn(outcome.ethics_decision.outcome, {"soften", "allow"})
        self.assertIn("current local corpus", outcome.answer_text.lower())

    def test_underspecified_claim_routes_to_clarification(self) -> None:
        outcome = self.service.handle_prompt("They approved it.")
        self.assertEqual(outcome.verification.route_decision.route, "Clarification")
        self.assertIn("Please clarify", outcome.answer_text)

    def test_repo_question_can_still_surface_local_evidence(self) -> None:
        outcome = self.service.handle_prompt("What phase is ESCO in right now?")
        self.assertIsNone(outcome.verification.route_decision.route)
        self.assertGreaterEqual(len(outcome.evidence_records), 1)
        self.assertIn("closest local material says", outcome.answer_text)

    def test_support_profile_prompt_records_audit_entries(self) -> None:
        service, audit_store = self._build_audited_service()

        outcome = service.handle_prompt("ESCO is local-first and web search is disabled in the MVP.")

        categories = tuple(entry.category for entry in outcome.audit_entries)
        self.assertEqual(
            categories,
            (
                "evidence_selection",
                "support_profile_generation",
                "policy_decision",
                "user_visible_output",
            ),
        )
        stored_entries = tuple(reversed(audit_store.list()))
        self.assertEqual(stored_entries, outcome.audit_entries)
        self.assertEqual(len({entry.event_id for entry in outcome.audit_entries}), 4)

    def test_orchestrator_audit_events_share_trace_and_monotonic_sequences(self) -> None:
        capturing_audit = CapturingAuditService()
        service = self._build_service(self.retrieval, audit=cast(AuditService, capturing_audit))

        outcome = service.handle_prompt("ESCO is local-first and web search is disabled in the MVP.")

        self.assertEqual(tuple(capturing_audit.entries), outcome.audit_entries)
        self.assertEqual(len({event.trace_id for event in capturing_audit.events}), 1)
        self.assertEqual([event.sequence for event in capturing_audit.events], [1, 2, 3, 4])

    def test_without_audit_service_returns_empty_audit_entries(self) -> None:
        outcome = self.service.handle_prompt("ESCO is local-first and web search is disabled in the MVP.")

        self.assertEqual(outcome.audit_entries, ())

    def test_abstention_records_extra_audit_entry(self) -> None:
        service, audit_store = self._build_audited_service(seed_text=None)

        outcome = service.handle_prompt("The FDA approved this product in 2024.")

        self.assertEqual(outcome.ethics_decision.outcome, "abstain")
        self.assertIn("abstention", tuple(entry.category for entry in outcome.audit_entries))
        self.assertEqual(tuple(reversed(audit_store.list())), outcome.audit_entries)

    def test_escalation_records_extra_audit_entry(self) -> None:
        service, audit_store = self._build_audited_service(
            seed_text=(
                "The medical treatment was approved in 2024.\n\n"
                "A later review says the medical treatment was not approved in 2024."
            )
        )

        outcome = service.handle_prompt("The medical treatment was approved in 2024.")

        self.assertEqual(outcome.ethics_decision.outcome, "escalate")
        self.assertIn("escalation", tuple(entry.category for entry in outcome.audit_entries))
        self.assertEqual(tuple(reversed(audit_store.list())), outcome.audit_entries)


if __name__ == "__main__":
    unittest.main()
