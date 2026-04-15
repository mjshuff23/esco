"""Local-first orchestration for retrieval, routing, policy, and response."""

from __future__ import annotations

from dataclasses import dataclass

from esco_contracts import SUPPORT_PROFILE_ROUTE
from esco_contracts.models import EvidenceRecord
from esco_policy import PolicyContext, PolicyService
from esco_retrieval import RetrievalQuery, RetrievalService
from esco_runtime import GenerationRequest, LocalModelAdapter
from esco_verifier import VerificationService

from .models import OrchestratorOutcome


@dataclass(slots=True)
class OrchestratorService:
    retrieval: RetrievalService
    verifier: VerificationService
    policy: PolicyService
    runtime: LocalModelAdapter
    default_retrieval_limit: int = 3

    def handle_prompt(
        self,
        prompt: str,
        *,
        include_consequences: bool = True,
        retrieval_limit: int | None = None,
    ) -> OrchestratorOutcome:
        if not prompt.strip():
            raise ValueError("prompt must not be empty")

        preflight_claims = self.verifier.extract_claims(prompt)
        preflight_route = self.verifier.route_claims(preflight_claims)

        evidence_records: tuple[EvidenceRecord, ...] = tuple()
        if preflight_route.route == SUPPORT_PROFILE_ROUTE and preflight_route.claim is not None:
            evidence_records = self.retrieval.retrieve_evidence(
                RetrievalQuery(
                    claim_text=preflight_route.claim.claim_text,
                    limit=retrieval_limit or self.default_retrieval_limit,
                )
            )
        elif preflight_route.conversational and prompt.strip().endswith("?"):
            evidence_records = self.retrieval.retrieve_evidence(
                RetrievalQuery(
                    claim_text=prompt,
                    limit=retrieval_limit or self.default_retrieval_limit,
                )
            )

        verification = self.verifier.evaluate_prompt(
            prompt,
            evidence_records=evidence_records,
            include_consequences=include_consequences,
        )
        ethics_decision = self.policy.evaluate(
            PolicyContext(
                claim=verification.route_decision.claim,
                route=verification.route_decision.route,
                evidence_records=evidence_records,
                support_profile=verification.support_profile,
            )
        )

        generation_request = GenerationRequest(
            route=verification.route_decision.route or "Conversational",
            user_prompt=prompt,
            evidence_refs=tuple(record.evidence_id for record in evidence_records),
            evidence_excerpts=tuple(record.excerpt for record in evidence_records),
            policy_outcome=ethics_decision.outcome,
            support_posture=(
                verification.support_profile.overall_posture
                if verification.support_profile is not None
                else None
            ),
            missing_details=verification.route_decision.missing_details,
            caveats=(
                verification.support_profile.caveats
                if verification.support_profile is not None
                else tuple()
            ),
            response_guidance=(verification.route_decision.rationale, ethics_decision.rationale_summary),
        )
        generation_response = self.runtime.generate(generation_request)

        return OrchestratorOutcome(
            prompt=prompt,
            verification=verification,
            ethics_decision=ethics_decision,
            evidence_records=evidence_records,
            generation_request=generation_request,
            generation_response=generation_response,
        )
