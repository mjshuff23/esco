"""First-pass claim extraction, routing, and Support Profile construction."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime
from typing import Literal
from uuid import uuid4

from esco_contracts import CLARIFICATION_ROUTE, EXPLORATION_ROUTE, SUPPORT_PROFILE_ROUTE
from esco_contracts.models import Claim, EvidenceRecord, RoutingMode, ScoreBand, SupportMetric, SupportProfile

from .models import ConsequenceAnalysis, RouteDecision, VerificationOutcome

QUESTION_WORDS = ("who", "what", "when", "where", "why", "how", "can", "should", "could", "would", "is", "are", "do", "does")
ASSERTIVE_CUES = (" is ", " are ", " was ", " were ", " can ", " should ", " must ", " has ", " have ", " means ", " causes ", " feels ", " seems ", " approved ")
PERSONAL_CUES = ("i feel", "i think", "my friend", "my partner", "my boss", "my family", "i am", "i'm", "me ")
GENERIC_SUBJECTS = ("they", "it", "this", "that", "someone", "something")
TIME_WORDS = ("today", "yesterday", "tomorrow", "week", "month", "year", "202", "199", "200")
NEGATION_CUES = (" not ", " no ", " never ", " false", " incorrect", " lacks ", " failed ", " inaccurate", " contradicted", " conflict")
SupportPosture = Literal["supported", "mixed", "weak", "insufficient", "conflicted"]
Specificity = Literal["specific", "underspecified"]


@dataclass(slots=True)
class VerificationService:
    service_name: str = "esco-verifier"

    def evaluate_prompt(
        self,
        prompt: str,
        evidence_records: tuple[EvidenceRecord, ...] = (),
        *,
        include_consequences: bool = False,
    ) -> VerificationOutcome:
        claims = self.extract_claims(prompt)
        route_decision = self.route_claims(claims)
        support_profile = None
        if route_decision.route == SUPPORT_PROFILE_ROUTE and route_decision.claim is not None:
            support_profile = self.build_support_profile(route_decision.claim, evidence_records)
        consequences = None
        if include_consequences and route_decision.route is not None and route_decision.claim is not None:
            consequences = self.analyze_consequences(route_decision.claim, route_decision.route)
        return VerificationOutcome(
            extracted_claims=claims,
            route_decision=route_decision,
            support_profile=support_profile,
            consequences=consequences,
        )

    def extract_claims(self, prompt: str) -> tuple[Claim, ...]:
        segments = [segment.strip() for segment in re.split(r"[.?!]\s*", prompt) if segment.strip()]
        claims: list[Claim] = []
        for segment in segments:
            lowered = segment.lower()
            if prompt.strip().endswith("?") and lowered.startswith(QUESTION_WORDS):
                continue
            if not any(cue in f" {lowered} " for cue in ASSERTIVE_CUES):
                continue
            claim_kind = self._classify_claim_kind(lowered)
            externally_verifiable = claim_kind == "empirical"
            specificity: Specificity = "specific" if self._is_specific(segment, lowered) else "underspecified"
            claims.append(
                Claim(
                    claim_id=str(uuid4()),
                    claim_text=segment,
                    claim_kind=claim_kind,
                    specificity=specificity,
                    externally_verifiable=externally_verifiable,
                )
            )
        return tuple(claims)

    def route_claims(self, claims: tuple[Claim, ...]) -> RouteDecision:
        if not claims:
            return RouteDecision(
                claim=None,
                route=None,
                rationale="No assertive claim detected; ESCO can stay conversational.",
                conversational=True,
            )

        primary_claim = next((claim for claim in claims if claim.claim_kind == "empirical"), claims[0])
        if not primary_claim.externally_verifiable:
            return RouteDecision(
                claim=primary_claim,
                route=EXPLORATION_ROUTE,
                rationale="The claim centers on interpretation, meaning, or a non-verifiable internal state.",
            )

        if primary_claim.specificity == "underspecified":
            return RouteDecision(
                claim=primary_claim,
                route=CLARIFICATION_ROUTE,
                rationale="The claim might be verifiable, but it is missing enough detail that ESCO should clarify before scoring.",
                missing_details=self._missing_specificity_details(primary_claim.claim_text),
            )

        return RouteDecision(
            claim=primary_claim,
            route=SUPPORT_PROFILE_ROUTE,
            rationale="The claim is externally verifiable and specific enough for Support Profile analysis.",
        )

    def build_support_profile(self, claim: Claim, evidence_records: tuple[EvidenceRecord, ...]) -> SupportProfile:
        evidence_count = len(evidence_records)
        unique_domains = {record.provenance.source_domain for record in evidence_records}
        counterevidence = tuple(
            record.evidence_id
            for record in evidence_records
            if any(cue in f" {record.excerpt.lower()} " for cue in NEGATION_CUES)
        )

        metrics = {
            "premise_validity": self._metric_from_evidence(
                score_band=self._score_from_count(evidence_count),
                rationale="Based on how much retrieved evidence exists for the claim premise.",
                evidence_records=evidence_records,
            ),
            "source_convergence": self._metric_from_evidence(
                score_band=self._score_from_domains(len(unique_domains)),
                rationale="Based on how many distinct source domains appear in the evidence set.",
                evidence_records=evidence_records,
            ),
            "temporal_relevance": self._metric_from_evidence(
                score_band=self._score_from_temporal_relevance(evidence_records),
                rationale="Based on whether the retrieved evidence appears current enough to rely on.",
                evidence_records=evidence_records,
            ),
            "internal_consistency": self._metric_from_evidence(
                score_band="mixed" if counterevidence else ("moderate" if evidence_records else "low"),
                rationale="Based on whether the retrieved evidence conflicts internally.",
                evidence_records=evidence_records,
            ),
            "counterevidence_presence": self._metric_from_evidence(
                score_band="high" if counterevidence else "low",
                rationale="Tracks whether plausible counterevidence is present in the retrieved set.",
                evidence_records=tuple(record for record in evidence_records if record.evidence_id in counterevidence),
            ),
        }

        caveats: list[str] = []
        if evidence_count == 0:
            caveats.append("No supporting evidence was retrieved.")
        if evidence_count == 1:
            caveats.append("Only one evidence record was retrieved, so corroboration is limited.")
        if len(unique_domains) <= 1 and evidence_count > 1:
            caveats.append("The current evidence set does not yet show broad source-domain convergence.")
        if any(record.provenance.publication_date is None for record in evidence_records):
            caveats.append("Some retrieved evidence does not include a publication date.")

        overall_posture: SupportPosture
        if evidence_count == 0:
            overall_posture = "insufficient"
        elif counterevidence:
            overall_posture = "conflicted"
        elif evidence_count >= 2 and len(unique_domains) >= 2:
            overall_posture = "supported"
        elif evidence_count == 1:
            overall_posture = "weak"
        else:
            overall_posture = "mixed"

        return SupportProfile(
            support_profile_id=str(uuid4()),
            claim_id=claim.claim_id,
            metrics=metrics,
            overall_posture=overall_posture,
            caveats=tuple(caveats),
            counterevidence_refs=counterevidence,
        )

    def analyze_consequences(self, claim: Claim, route: RoutingMode) -> ConsequenceAnalysis:
        downstream_effects: tuple[str, ...]
        affected_actors: tuple[str, ...]
        evidence_gaps: tuple[str, ...]
        if route == SUPPORT_PROFILE_ROUTE:
            downstream_effects = (
                "A user could act on a factual claim that turns out to be weak or wrong.",
                "Later recommendations or decisions could inherit the same flawed premise.",
            )
            affected_actors = ("user", "verification layer", "policy layer")
            evidence_gaps = ("independent corroboration", "broader source coverage", "more current evidence")
        elif route == EXPLORATION_ROUTE:
            downstream_effects = (
                "An interpretation could harden into a shared fact without external grounding.",
                "Relational conclusions could escalate from a mistaken assumption.",
            )
            affected_actors = ("user", "conversation partner")
            evidence_gaps = ("clarified personal context", "observable behaviors", "scope of interpretation")
        else:
            downstream_effects = (
                "The system could score a claim before the important details are actually known.",
                "The response could sound more certain than the prompt supports.",
            )
            affected_actors = ("user", "verification layer")
            evidence_gaps = ("actors", "timeframe", "observable evidence")

        return ConsequenceAnalysis(
            claim_text=claim.claim_text,
            route=route,
            downstream_effects=downstream_effects,
            affected_actors=affected_actors,
            evidence_gaps=evidence_gaps,
        )

    def _classify_claim_kind(self, lowered: str) -> str:
        if any(cue in lowered for cue in PERSONAL_CUES):
            return "relational"
        if " should " in f" {lowered} " or " must " in f" {lowered} ":
            return "normative"
        return "empirical"

    def _is_specific(self, raw: str, lowered: str) -> bool:
        tokens = lowered.split()
        if len(tokens) < 4:
            return False
        if tokens and tokens[0] in GENERIC_SUBJECTS:
            return False
        if any(time_word in lowered for time_word in TIME_WORDS):
            return True
        if re.search(r"\d", raw):
            return True
        return any(token[:1].isupper() for token in raw.split()[1:])

    def _missing_specificity_details(self, claim_text: str) -> tuple[str, ...]:
        lowered = claim_text.lower()
        raw_tokens = claim_text.split()
        missing: list[str] = []
        if not raw_tokens or raw_tokens[0].lower() in GENERIC_SUBJECTS:
            missing.append("actors")
        if not any(time_word in lowered for time_word in TIME_WORDS) and not re.search(r"\d", claim_text):
            missing.append("timeframe")
        missing.append("observable evidence")
        return tuple(dict.fromkeys(missing))

    def _metric_from_evidence(
        self,
        *,
        score_band: ScoreBand,
        rationale: str,
        evidence_records: tuple[EvidenceRecord, ...],
    ) -> SupportMetric:
        return SupportMetric(
            score_band=score_band,
            rationale=rationale,
            evidence_refs=tuple(record.evidence_id for record in evidence_records),
        )

    def _score_from_count(self, evidence_count: int) -> ScoreBand:
        if evidence_count == 0:
            return "low"
        if evidence_count == 1:
            return "moderate"
        return "high"

    def _score_from_domains(self, domain_count: int) -> ScoreBand:
        if domain_count == 0:
            return "low"
        if domain_count == 1:
            return "mixed"
        return "high"

    def _score_from_temporal_relevance(self, evidence_records: tuple[EvidenceRecord, ...]) -> ScoreBand:
        if not evidence_records:
            return "low"
        dates = [self._parse_publication_date(record.provenance.publication_date) for record in evidence_records]
        if any(item is None for item in dates):
            return "mixed"
        known_dates = [item for item in dates if item is not None]
        current_year = date.today().year
        if all(current_year - item.year <= 5 for item in known_dates):
            return "high"
        return "moderate"

    def _parse_publication_date(self, publication_date: str | None) -> date | None:
        if publication_date is None:
            return None
        try:
            return datetime.strptime(publication_date, "%Y-%m-%d").date()
        except ValueError:
            return None
