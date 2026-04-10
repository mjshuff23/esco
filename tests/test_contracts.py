from __future__ import annotations

import unittest
from datetime import datetime, timezone

from tests import bootstrap  # noqa: F401

from esco_contracts import CLARIFICATION_ROUTE, EXPLORATION_ROUTE, SUPPORT_PROFILE_FIELDS, SUPPORT_PROFILE_ROUTE
from esco_contracts.models import (
    ActorRef,
    Claim,
    EventEnvelope,
    SourceRef,
    SubjectRef,
    SupportMetric,
    SupportProfile,
)


class ContractTests(unittest.TestCase):
    def test_public_routes_are_locked(self) -> None:
        self.assertEqual(SUPPORT_PROFILE_ROUTE, "Support Profile")
        self.assertEqual(EXPLORATION_ROUTE, "Exploration")
        self.assertEqual(CLARIFICATION_ROUTE, "Clarification")

    def test_support_profile_requires_all_locked_metrics(self) -> None:
        metrics = {
            field_name: SupportMetric(score_band="moderate", rationale=f"{field_name} rationale", evidence_refs=("e-1",))
            for field_name in SUPPORT_PROFILE_FIELDS
        }
        profile = SupportProfile(
            support_profile_id="sp-1",
            claim_id="claim-1",
            metrics=metrics,
            overall_posture="supported",
        )
        self.assertEqual(profile.mode, SUPPORT_PROFILE_ROUTE)
        self.assertEqual(tuple(profile.metrics.keys()), SUPPORT_PROFILE_FIELDS)

    def test_event_envelope_stays_append_only(self) -> None:
        claim = Claim(
            claim_id="claim-1",
            claim_text="ESCO is a local-first platform.",
            claim_kind="empirical",
            specificity="specific",
            externally_verifiable=True,
        )
        envelope = EventEnvelope(
            schema_version="1.0.0",
            event_id="event-1",
            event_type="claim.created",
            occurred_at=datetime.now(timezone.utc),
            trace_id="trace-1",
            session_id="session-1",
            sequence=1,
            actor=ActorRef(actor_type="service", actor_id="esco-verifier", actor_domain="verifier"),
            source=SourceRef(channel="api", origin="unit-test"),
            subject=SubjectRef(entity_type="claim", entity_id="claim-1"),
            payload=claim,
        )
        self.assertTrue(envelope.append_only)


if __name__ == "__main__":
    unittest.main()
