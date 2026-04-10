"""Typed results for ESCO verification and claim routing."""

from __future__ import annotations

from dataclasses import dataclass, field

from esco_contracts.models import Claim, RoutingMode, SupportProfile


@dataclass(frozen=True)
class RouteDecision:
    claim: Claim | None
    route: RoutingMode | None
    rationale: str
    conversational: bool = False
    missing_details: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ConsequenceAnalysis:
    claim_text: str
    route: RoutingMode
    downstream_effects: tuple[str, ...]
    affected_actors: tuple[str, ...]
    evidence_gaps: tuple[str, ...]


@dataclass(frozen=True)
class VerificationOutcome:
    extracted_claims: tuple[Claim, ...]
    route_decision: RouteDecision
    support_profile: SupportProfile | None = None
    consequences: ConsequenceAnalysis | None = None
