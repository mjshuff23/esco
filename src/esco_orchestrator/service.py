"""Local-first orchestration for retrieval, routing, policy, and response."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

from esco_audit import AuditService
from esco_contracts import SUPPORT_PROFILE_ROUTE
from esco_contracts.models import ActorRef, AuditEntry, EventEnvelope, EvidenceRecord, SourceRef, SubjectRef
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
    audit: AuditService | None = None
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

        trace_id = str(uuid4())
        audit_entries: list[AuditEntry] = []
        audit_sequence = 1

        def record_audit(
            *,
            event_type: str,
            subject_type: str,
            subject_id: str,
            category: str,
            summary: str,
            payload: object,
            linked_ids: tuple[str, ...] = (),
            visibility: str = "internal_restricted",
        ) -> None:
            nonlocal audit_sequence
            if self.audit is None:
                return
            event = self._build_audit_event(
                event_type=event_type,
                subject_type=subject_type,
                subject_id=subject_id,
                trace_id=trace_id,
                sequence=audit_sequence,
                payload=payload,
            )
            audit_entries.append(
                self.audit.record_from_event(
                    event,
                    category=category,
                    visibility=visibility,
                    summary=summary,
                    linked_ids=linked_ids,
                )
            )
            audit_sequence += 1

        preflight_claims = self.verifier.extract_claims(prompt)
        preflight_route = self.verifier.route_claims(preflight_claims)

        evidence_records: tuple[EvidenceRecord, ...] = tuple()
        retrieval_attempted = False
        retrieval_claim_text = ""
        if preflight_route.route == SUPPORT_PROFILE_ROUTE and preflight_route.claim is not None:
            retrieval_attempted = True
            retrieval_claim_text = preflight_route.claim.claim_text
            evidence_records = self.retrieval.retrieve_evidence(
                RetrievalQuery(
                    claim_text=preflight_route.claim.claim_text,
                    limit=retrieval_limit or self.default_retrieval_limit,
                )
            )
        elif preflight_route.conversational and prompt.strip().endswith("?"):
            retrieval_attempted = True
            retrieval_claim_text = prompt
            evidence_records = self.retrieval.retrieve_evidence(
                RetrievalQuery(
                    claim_text=prompt,
                    limit=retrieval_limit or self.default_retrieval_limit,
                )
            )
        if retrieval_attempted:
            evidence_ids = tuple(record.evidence_id for record in evidence_records)
            record_audit(
                event_type="evidence.retrieved",
                subject_type="evidence_record",
                subject_id=evidence_ids[0] if evidence_ids else "empty",
                category="evidence_selection",
                summary=f"Retrieved {len(evidence_records)} evidence record(s) for orchestration.",
                payload={
                    "claim_text": retrieval_claim_text,
                    "result_count": len(evidence_records),
                    "evidence_ids": evidence_ids,
                },
                linked_ids=evidence_ids,
            )

        verification = self.verifier.evaluate_prompt(
            prompt,
            evidence_records=evidence_records,
            include_consequences=include_consequences,
        )
        if verification.support_profile is not None:
            record_audit(
                event_type="support_profile.generated",
                subject_type="support_profile",
                subject_id=verification.support_profile.support_profile_id,
                category="support_profile_generation",
                summary=f"Generated Support Profile with posture {verification.support_profile.overall_posture}.",
                payload={
                    "route": verification.route_decision.route,
                    "support_profile_id": verification.support_profile.support_profile_id,
                    "overall_posture": verification.support_profile.overall_posture,
                    "counterevidence_refs": verification.support_profile.counterevidence_refs,
                },
                linked_ids=(verification.support_profile.support_profile_id,),
            )
        ethics_decision = self.policy.evaluate(
            PolicyContext(
                claim=verification.route_decision.claim,
                route=verification.route_decision.route,
                evidence_records=evidence_records,
                support_profile=verification.support_profile,
            )
        )
        record_audit(
            event_type="ethics.decision_made",
            subject_type="ethics_decision",
            subject_id=ethics_decision.ethics_decision_id,
            category="policy_decision",
            summary=f"Policy outcome was {ethics_decision.outcome}.",
            payload={
                "outcome": ethics_decision.outcome,
                "policy_refs": ethics_decision.policy_refs,
                "rationale_summary": ethics_decision.rationale_summary,
            },
            linked_ids=(ethics_decision.ethics_decision_id,),
        )
        if ethics_decision.outcome == "abstain":
            record_audit(
                event_type="policy.abstention_emitted",
                subject_type="ethics_decision",
                subject_id=ethics_decision.ethics_decision_id,
                category="abstention",
                summary="Policy emitted structured abstention.",
                payload={
                    "outcome": ethics_decision.outcome,
                    "policy_refs": ethics_decision.policy_refs,
                },
                linked_ids=(ethics_decision.ethics_decision_id,),
            )
        elif ethics_decision.outcome == "escalate":
            record_audit(
                event_type="policy.escalation_triggered",
                subject_type="ethics_decision",
                subject_id=ethics_decision.ethics_decision_id,
                category="escalation",
                summary="Policy triggered escalation.",
                payload={
                    "outcome": ethics_decision.outcome,
                    "policy_refs": ethics_decision.policy_refs,
                },
                linked_ids=(ethics_decision.ethics_decision_id,),
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
        record_audit(
            event_type="output.user_visible",
            subject_type="user_visible_output",
            subject_id=str(uuid4()),
            category="user_visible_output",
            summary="Generated user-visible output from mediated orchestration.",
            payload={
                "route": generation_request.route,
                "policy_outcome": ethics_decision.outcome,
                "evidence_refs": generation_request.evidence_refs,
                "model_id": generation_response.model_id,
            },
            linked_ids=tuple(record.evidence_id for record in evidence_records),
            visibility="public_summary",
        )

        return OrchestratorOutcome(
            prompt=prompt,
            verification=verification,
            ethics_decision=ethics_decision,
            evidence_records=evidence_records,
            audit_entries=tuple(audit_entries),
            generation_request=generation_request,
            generation_response=generation_response,
        )

    def _build_audit_event(
        self,
        *,
        event_type: str,
        subject_type: str,
        subject_id: str,
        trace_id: str,
        sequence: int,
        payload: object,
    ) -> EventEnvelope:
        return EventEnvelope(
            schema_version="1.0.0",
            event_id=str(uuid4()),
            event_type=event_type,  # type: ignore[arg-type]
            occurred_at=datetime.now(timezone.utc),
            trace_id=trace_id,
            session_id=trace_id,
            sequence=sequence,
            actor=ActorRef(actor_type="service", actor_id="esco-orchestrator", actor_domain="orchestrator"),
            source=SourceRef(channel="orchestrator", origin="OrchestratorService"),
            subject=SubjectRef(entity_type=subject_type, entity_id=subject_id),  # type: ignore[arg-type]
            payload=payload,
        )
