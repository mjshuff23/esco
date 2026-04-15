"""Structured results for the local orchestration layer."""

from __future__ import annotations

from dataclasses import dataclass, field

from esco_contracts.models import EthicsDecision, EvidenceRecord
from esco_runtime.models import GenerationRequest, GenerationResponse
from esco_verifier.models import VerificationOutcome


@dataclass(frozen=True)
class OrchestratorOutcome:
    prompt: str
    verification: VerificationOutcome
    ethics_decision: EthicsDecision
    evidence_records: tuple[EvidenceRecord, ...] = field(default_factory=tuple)
    generation_request: GenerationRequest | None = None
    generation_response: GenerationResponse | None = None

    @property
    def answer_text(self) -> str:
        if self.generation_response is None:
            return ""
        return self.generation_response.text
