from __future__ import annotations

import unittest
from datetime import datetime, timezone
from typing import Literal

from tests import bootstrap  # noqa: F401

from esco_contracts import CLARIFICATION_ROUTE, EXPLORATION_ROUTE, SUPPORT_PROFILE_FIELDS, SUPPORT_PROFILE_ROUTE
from esco_contracts.models import Claim, EvidenceRecord, ProvenanceMetadata, QualityFlags, SupportMetric, SupportProfile
from esco_policy.models import PolicyContext
from esco_policy.service import PolicyService

SupportPosture = Literal["supported", "mixed", "weak", "insufficient", "conflicted"]


class PolicyServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = PolicyService()

    def _claim(self, text: str) -> Claim:
        return Claim(
            claim_id="claim-1",
            claim_text=text,
            claim_kind="empirical",
            specificity="specific",
            externally_verifiable=True,
        )

    def _support_profile(self, posture: SupportPosture) -> SupportProfile:
        metrics = {
            field_name: SupportMetric(score_band="moderate", rationale="ok", evidence_refs=("e-1",))
            for field_name in SUPPORT_PROFILE_FIELDS
        }
        return SupportProfile(
            support_profile_id="sp-1",
            claim_id="claim-1",
            metrics=metrics,
            overall_posture=posture,
        )

    def _evidence(self) -> EvidenceRecord:
        return EvidenceRecord(
            evidence_id="e-1",
            doc_id="doc-1",
            chunk_id="chunk-1",
            excerpt="The claim is supported by official guidance.",
            publisher="Example Publisher",
            provenance=ProvenanceMetadata(
                canonical_url="https://example.org/evidence",
                source_domain="example.org",
                content_sha256="a" * 64,
                retrieved_at=datetime.now(timezone.utc),
                publication_date="2025-01-01",
                source_type="official_docs",
                license_ref="CC-BY-4.0",
            ),
            quality_flags=QualityFlags(primary_source=True, contains_opinion=False),
        )

    def test_allows_conversational_no_claim_path(self) -> None:
        decision = self.service.evaluate(PolicyContext(claim=None, route=None))
        self.assertEqual(decision.outcome, "allow")

    def test_allows_exploration_route(self) -> None:
        decision = self.service.evaluate(
            PolicyContext(
                claim=self._claim("I feel my friend is upset with me."),
                route=EXPLORATION_ROUTE,
            )
        )
        self.assertEqual(decision.outcome, "allow")

    def test_softens_clarification_route(self) -> None:
        decision = self.service.evaluate(
            PolicyContext(
                claim=self._claim("They are lying."),
                route=CLARIFICATION_ROUTE,
            )
        )
        self.assertEqual(decision.outcome, "soften")

    def test_abstains_when_support_route_has_no_evidence(self) -> None:
        decision = self.service.evaluate(
            PolicyContext(
                claim=self._claim("The FDA approved this product in 2024."),
                route=SUPPORT_PROFILE_ROUTE,
            )
        )
        self.assertEqual(decision.outcome, "abstain")

    def test_blocks_high_impact_claim_without_evidence(self) -> None:
        decision = self.service.evaluate(
            PolicyContext(
                claim=self._claim("This medical treatment will cure cancer."),
                route=SUPPORT_PROFILE_ROUTE,
            )
        )
        self.assertEqual(decision.outcome, "block")

    def test_allows_supported_support_profile(self) -> None:
        decision = self.service.evaluate(
            PolicyContext(
                claim=self._claim("The FDA approved this product in 2024."),
                route=SUPPORT_PROFILE_ROUTE,
                evidence_records=(self._evidence(),),
                support_profile=self._support_profile("supported"),
            )
        )
        self.assertEqual(decision.outcome, "allow")

    def test_escalates_high_impact_conflicted_support_profile(self) -> None:
        decision = self.service.evaluate(
            PolicyContext(
                claim=self._claim("This medical treatment is guaranteed safe."),
                route=SUPPORT_PROFILE_ROUTE,
                evidence_records=(self._evidence(),),
                support_profile=self._support_profile("conflicted"),
            )
        )
        self.assertEqual(decision.outcome, "escalate")


if __name__ == "__main__":
    unittest.main()
