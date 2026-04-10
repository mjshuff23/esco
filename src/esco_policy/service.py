"""First-pass evidence-governed policy decisions."""

from __future__ import annotations

from dataclasses import dataclass
from esco_contracts import CLARIFICATION_ROUTE, EXPLORATION_ROUTE
from esco_contracts.models import EthicsDecision, PolicyOutcome
from uuid import uuid4

from .models import PolicyContext

HIGH_IMPACT_TERMS = (
    "medical",
    "doctor",
    "prescription",
    "suicide",
    "legal",
    "law",
    "criminal",
    "harm",
    "danger",
)


@dataclass(slots=True)
class PolicyService:
    service_name: str = "esco-policy"

    def evaluate(self, context: PolicyContext) -> EthicsDecision:
        policy_refs: list[str]
        rationale: str
        outcome: PolicyOutcome
        escalation_required = False

        if context.claim is None or context.route is None:
            policy_refs = ["mode.conversational.no_assertive_claim"]
            rationale = "No assertive claim was detected, so ESCO may remain conversational."
            outcome = "allow"
        elif context.route == EXPLORATION_ROUTE:
            policy_refs = ["mode.exploration.non_verifiable"]
            rationale = "The claim is interpretive or relational, so ESCO should explore without claiming external verification."
            outcome = "allow"
        elif context.route == CLARIFICATION_ROUTE:
            policy_refs = ["mode.clarification.insufficient_specificity"]
            rationale = "The claim may be verifiable, but it needs more detail before honest scoring is possible."
            outcome = "soften"
        else:
            evidence_count = len(context.evidence_records)
            high_impact = context.high_impact or self._is_high_impact(context.claim.claim_text)
            posture = context.support_profile.overall_posture if context.support_profile is not None else "insufficient"

            if evidence_count == 0:
                policy_refs = ["policy.no_claim_without_evidence", "policy.structured_abstention"]
                rationale = "No evidence was retrieved for a factual claim, so ESCO must abstain rather than bluff."
                outcome = "block" if high_impact else "abstain"
            elif posture in {"mixed", "conflicted"}:
                policy_refs = ["policy.counterevidence_visible", "policy.soften_on_conflict"]
                rationale = "The evidence set is conflicted or mixed, so ESCO should avoid overstating certainty."
                outcome = "escalate" if high_impact else "soften"
                escalation_required = high_impact
            elif posture == "supported":
                policy_refs = ["policy.evidence_required", "policy.allow_when_supported"]
                rationale = "The claim has enough specific support to answer within the evidence boundary."
                outcome = "allow"
            else:
                policy_refs = ["policy.structured_abstention"]
                rationale = "The evidence base is present but still too weak for a strong assertion."
                outcome = "soften"

        return EthicsDecision(
            ethics_decision_id=str(uuid4()),
            action_requested="answer_claim",
            outcome=outcome,
            policy_refs=tuple(policy_refs),
            rationale_summary=rationale,
            visibility="external_summary",
            escalation_required=escalation_required,
            support_profile_id=context.support_profile.support_profile_id if context.support_profile is not None else None,
            evidence_refs=tuple(record.evidence_id for record in context.evidence_records),
        )

    def _is_high_impact(self, claim_text: str) -> bool:
        lowered = claim_text.lower()
        return any(term in lowered for term in HIGH_IMPACT_TERMS)
