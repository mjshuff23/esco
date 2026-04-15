from __future__ import annotations

import unittest
from datetime import datetime, timezone

from tests import bootstrap  # noqa: F401

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


class OrchestratorServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        retrieval = RetrievalService(
            repository=InMemoryDocumentRepository(),
            embedder=DeterministicEmbedder(),
            vector_store=InMemoryVectorStore(),
            chunker=SimpleParagraphChunker(),
        )
        retrieval.ingest_document(
            IngestionArtifact(
                raw_text=(
                    "ESCO keeps web search disabled in the early local-first MVP.\n\n"
                    "Phase 2 includes verification, claim routing, and policy gating."
                ),
                canonical_url="https://example.org/esco-status",
                publisher="Example Org",
                source_type="official_docs",
                license_ref="CC-BY-4.0",
                retrieved_at=datetime.now(timezone.utc),
                artifact_uri="file:///tmp/esco-status.md",
            )
        )
        self.service = OrchestratorService(
            retrieval=retrieval,
            verifier=VerificationService(),
            policy=PolicyService(),
            runtime=GroundedDraftAdapter(config=build_grounded_demo_config()),
        )

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


if __name__ == "__main__":
    unittest.main()
