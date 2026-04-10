from __future__ import annotations

import unittest
from datetime import datetime, timezone

from tests import bootstrap  # noqa: F401

from esco_contracts import CLARIFICATION_ROUTE, EXPLORATION_ROUTE, SUPPORT_PROFILE_ROUTE
from esco_contracts.models import EvidenceRecord, ProvenanceMetadata, QualityFlags
from esco_verifier.service import VerificationService


class VerificationServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = VerificationService()

    def _evidence(self, evidence_id: str, excerpt: str, *, domain: str, publication_date: str | None = "2025-01-01") -> EvidenceRecord:
        return EvidenceRecord(
            evidence_id=evidence_id,
            doc_id=f"doc-{evidence_id}",
            chunk_id=evidence_id,
            excerpt=excerpt,
            publisher="Example Publisher",
            provenance=ProvenanceMetadata(
                canonical_url=f"https://{domain}/doc/{evidence_id}",
                source_domain=domain,
                content_sha256="a" * 64,
                retrieved_at=datetime.now(timezone.utc),
                publication_date=publication_date,
                source_type="official_docs",
                license_ref="CC-BY-4.0",
            ),
            quality_flags=QualityFlags(primary_source=True, contains_opinion=False),
        )

    def test_routes_specific_empirical_claim_to_support_profile(self) -> None:
        outcome = self.service.evaluate_prompt("The FDA approved this drug in 2024.")
        self.assertEqual(outcome.route_decision.route, SUPPORT_PROFILE_ROUTE)

    def test_routes_relational_claim_to_exploration(self) -> None:
        outcome = self.service.evaluate_prompt("I feel my friend is upset with me.")
        self.assertEqual(outcome.route_decision.route, EXPLORATION_ROUTE)

    def test_routes_underspecified_empirical_claim_to_clarification(self) -> None:
        outcome = self.service.evaluate_prompt("They are lying.")
        self.assertEqual(outcome.route_decision.route, CLARIFICATION_ROUTE)
        self.assertIn("actors", outcome.route_decision.missing_details)

    def test_returns_conversational_when_no_assertive_claim_exists(self) -> None:
        outcome = self.service.evaluate_prompt("How are you today?")
        self.assertTrue(outcome.route_decision.conversational)
        self.assertIsNone(outcome.route_decision.route)

    def test_mixed_prompt_routes_first_empirical_claim(self) -> None:
        outcome = self.service.evaluate_prompt("I think my friend is upset with me. The FDA approved this drug in 2024.")
        self.assertGreaterEqual(len(outcome.extracted_claims), 2)
        self.assertEqual(outcome.route_decision.route, SUPPORT_PROFILE_ROUTE)
        assert outcome.route_decision.claim is not None
        self.assertEqual(outcome.route_decision.claim.claim_kind, "empirical")

    def test_builds_support_profile_with_counterevidence(self) -> None:
        records = (
            self._evidence("e-1", "The FDA approved the product in 2024.", domain="fda.gov"),
            self._evidence("e-2", "A later report says the earlier approval claim was not accurate.", domain="nih.gov"),
        )
        outcome = self.service.evaluate_prompt(
            "The FDA approved this product in 2024.",
            evidence_records=records,
        )
        self.assertIsNotNone(outcome.support_profile)
        assert outcome.support_profile is not None
        self.assertEqual(outcome.support_profile.mode, SUPPORT_PROFILE_ROUTE)
        self.assertEqual(outcome.support_profile.overall_posture, "conflicted")
        self.assertTrue(outcome.support_profile.counterevidence_refs)
        self.assertEqual(set(outcome.support_profile.metrics.keys()), set(("premise_validity", "source_convergence", "temporal_relevance", "internal_consistency", "counterevidence_presence")))

    def test_consequences_mode_returns_structured_output(self) -> None:
        outcome = self.service.evaluate_prompt(
            "The FDA approved this drug in 2024.",
            include_consequences=True,
        )
        self.assertIsNotNone(outcome.consequences)
        assert outcome.consequences is not None
        self.assertEqual(outcome.consequences.route, SUPPORT_PROFILE_ROUTE)
        self.assertTrue(outcome.consequences.evidence_gaps)


if __name__ == "__main__":
    unittest.main()
