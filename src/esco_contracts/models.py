"""Typed contracts mirrored from the Phase 0 documentation."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal, Mapping

from .constants import SUPPORT_PROFILE_FIELDS, SUPPORT_PROFILE_ROUTE

ActorDomain = Literal[
    "gateway",
    "runtime",
    "retrieval",
    "verifier",
    "policy",
    "audit",
    "memory",
    "orchestrator",
    "search",
    "domain_bot",
    "human_review",
]
ActorType = Literal["user", "assistant", "system", "service", "reviewer", "external_source"]
EventType = Literal[
    "claim.created",
    "evidence.ingested",
    "evidence.retrieved",
    "support_profile.generated",
    "ethics.decision_made",
    "audit.entry_created",
    "memory.consent_recorded",
    "memory.write_skipped",
    "memory.write_completed",
    "policy.abstention_emitted",
    "policy.escalation_triggered",
    "search.request_blocked",
    "search.content_sanitized",
    "output.user_visible",
]
EntityType = Literal[
    "claim",
    "evidence_record",
    "support_profile",
    "ethics_decision",
    "audit_entry",
    "memory_consent_record",
    "user_visible_output",
]
RoutingMode = Literal["Support Profile", "Exploration", "Clarification"]
ScoreBand = Literal["low", "mixed", "moderate", "high"]
PolicyOutcome = Literal["allow", "soften", "abstain", "block", "escalate"]


def _require_text(value: str, field_name: str) -> None:
    if not value or not value.strip():
        raise ValueError(f"{field_name} must not be empty")


@dataclass(frozen=True)
class ActorRef:
    actor_type: ActorType
    actor_id: str
    actor_domain: ActorDomain

    def __post_init__(self) -> None:
        _require_text(self.actor_id, "actor_id")


@dataclass(frozen=True)
class SourceRef:
    channel: str
    origin: str
    request_id: str | None = None

    def __post_init__(self) -> None:
        _require_text(self.channel, "channel")
        _require_text(self.origin, "origin")


@dataclass(frozen=True)
class SubjectRef:
    entity_type: EntityType
    entity_id: str

    def __post_init__(self) -> None:
        _require_text(self.entity_id, "entity_id")


@dataclass(frozen=True)
class EventEnvelope:
    schema_version: str
    event_id: str
    event_type: EventType
    occurred_at: datetime
    trace_id: str
    session_id: str
    sequence: int
    actor: ActorRef
    source: SourceRef
    subject: SubjectRef
    payload: object
    append_only: bool = True

    def __post_init__(self) -> None:
        _require_text(self.schema_version, "schema_version")
        _require_text(self.event_id, "event_id")
        _require_text(self.trace_id, "trace_id")
        _require_text(self.session_id, "session_id")
        if self.sequence < 1:
            raise ValueError("sequence must be >= 1")
        if not self.append_only:
            raise ValueError("EventEnvelope must remain append-only")


@dataclass(frozen=True)
class ProvenanceMetadata:
    canonical_url: str
    source_domain: str
    content_sha256: str
    retrieved_at: datetime
    source_type: str
    license_ref: str
    publication_date: str | None = None
    raw_artifact_uri: str | None = None

    def __post_init__(self) -> None:
        _require_text(self.canonical_url, "canonical_url")
        _require_text(self.source_domain, "source_domain")
        _require_text(self.content_sha256, "content_sha256")
        _require_text(self.source_type, "source_type")
        _require_text(self.license_ref, "license_ref")


@dataclass(frozen=True)
class QualityFlags:
    primary_source: bool
    contains_opinion: bool
    peer_reviewed: bool = False
    official_docs: bool = False
    contains_prompt_injection_patterns: bool = False


@dataclass(frozen=True)
class Claim:
    claim_id: str
    claim_text: str
    claim_kind: str
    specificity: Literal["specific", "underspecified"]
    externally_verifiable: bool

    def __post_init__(self) -> None:
        _require_text(self.claim_id, "claim_id")
        _require_text(self.claim_text, "claim_text")
        _require_text(self.claim_kind, "claim_kind")


@dataclass(frozen=True)
class EvidenceRecord:
    evidence_id: str
    doc_id: str
    chunk_id: str
    excerpt: str
    publisher: str
    provenance: ProvenanceMetadata
    quality_flags: QualityFlags

    def __post_init__(self) -> None:
        _require_text(self.evidence_id, "evidence_id")
        _require_text(self.doc_id, "doc_id")
        _require_text(self.chunk_id, "chunk_id")
        _require_text(self.excerpt, "excerpt")
        _require_text(self.publisher, "publisher")


@dataclass(frozen=True)
class SupportMetric:
    score_band: ScoreBand
    rationale: str
    evidence_refs: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        _require_text(self.rationale, "rationale")


@dataclass(frozen=True)
class SupportProfile:
    support_profile_id: str
    claim_id: str
    metrics: Mapping[str, SupportMetric]
    overall_posture: Literal["supported", "mixed", "weak", "insufficient", "conflicted"]
    caveats: tuple[str, ...] = field(default_factory=tuple)
    counterevidence_refs: tuple[str, ...] = field(default_factory=tuple)
    mode: RoutingMode = SUPPORT_PROFILE_ROUTE

    def __post_init__(self) -> None:
        _require_text(self.support_profile_id, "support_profile_id")
        _require_text(self.claim_id, "claim_id")
        missing = [field_name for field_name in SUPPORT_PROFILE_FIELDS if field_name not in self.metrics]
        if missing:
            raise ValueError(f"SupportProfile is missing required metrics: {', '.join(missing)}")


@dataclass(frozen=True)
class EthicsDecision:
    ethics_decision_id: str
    action_requested: str
    outcome: PolicyOutcome
    policy_refs: tuple[str, ...]
    rationale_summary: str
    visibility: Literal["internal", "external_summary"]
    escalation_required: bool
    support_profile_id: str | None = None
    evidence_refs: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        _require_text(self.ethics_decision_id, "ethics_decision_id")
        _require_text(self.action_requested, "action_requested")
        _require_text(self.rationale_summary, "rationale_summary")
        if not self.policy_refs:
            raise ValueError("policy_refs must contain at least one reference")


@dataclass(frozen=True)
class AuditEntry:
    audit_entry_id: str
    event_id: str
    category: str
    visibility: Literal["public_summary", "internal_restricted"]
    redaction_level: Literal["none", "internal_only", "core_private"]
    summary: str
    linked_ids: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        _require_text(self.audit_entry_id, "audit_entry_id")
        _require_text(self.event_id, "event_id")
        _require_text(self.category, "category")
        _require_text(self.summary, "summary")


@dataclass(frozen=True)
class MemoryConsentRecord:
    memory_consent_id: str
    subject_actor_id: str
    consent_state: Literal["opt_in", "opt_out", "revoked"]
    scope: Literal["none", "session", "domain", "global"]
    effective_at: datetime
    write_enabled: bool = False
    domain_ids: tuple[str, ...] = field(default_factory=tuple)
    expires_at: datetime | None = None

    def __post_init__(self) -> None:
        _require_text(self.memory_consent_id, "memory_consent_id")
        _require_text(self.subject_actor_id, "subject_actor_id")
        if self.consent_state != "opt_in" and self.write_enabled:
            raise ValueError("write_enabled may only be true for opt-in consent")
        if self.scope == "none" and self.write_enabled:
            raise ValueError("scope 'none' cannot enable writes")
