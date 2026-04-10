"""Typed inputs for the policy layer."""

from __future__ import annotations

from dataclasses import dataclass, field

from esco_contracts.models import Claim, EvidenceRecord, RoutingMode, SupportProfile


@dataclass(frozen=True)
class PolicyContext:
    claim: Claim | None
    route: RoutingMode | None
    evidence_records: tuple[EvidenceRecord, ...] = field(default_factory=tuple)
    support_profile: SupportProfile | None = None
    high_impact: bool = False
