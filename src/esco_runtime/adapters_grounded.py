"""Deterministic grounded adapter for the offline interactive lane.

This adapter is intentionally not a substitute for a real model runner. Its job
is to turn the current verification and policy state into a small, grounded
answer so the repo can exercise an end-to-end local interaction path before a
heavier local model is wired in.
"""

from __future__ import annotations

from dataclasses import dataclass
import re

from esco_contracts import CLARIFICATION_ROUTE, EXPLORATION_ROUTE, SUPPORT_PROFILE_ROUTE

from .models import GenerationRequest, GenerationResponse, ModelRuntimeConfig


def build_grounded_demo_config() -> ModelRuntimeConfig:
    """Return the lightweight config used by the demo-only grounded adapter."""
    return ModelRuntimeConfig(
        model_id="esco-grounded-template-v1",
        family="ESCO",
        role="demo",
        license_name="Repository-local",
        quantization="n/a",
        min_recommended_ram_gb=1,
        context_window_tokens=4096,
        notes=(
            "Deterministic local adapter for the offline interactive lane.",
            "Replace with a real local model adapter once runtime wiring is ready.",
        ),
    )


@dataclass(slots=True)
class GroundedDraftAdapter:
    """Small deterministic adapter used by the local CLI demo path."""

    config: ModelRuntimeConfig

    def generate(self, request: GenerationRequest) -> GenerationResponse:
        if request.route == SUPPORT_PROFILE_ROUTE:
            text = self._support_profile_text(request)
        elif request.route == EXPLORATION_ROUTE:
            text = self._exploration_text(request)
        elif request.route == CLARIFICATION_ROUTE:
            text = self._clarification_text(request)
        else:
            text = self._conversational_text(request)
        return GenerationResponse(model_id=self.config.model_id, text=text)

    def _support_profile_text(self, request: GenerationRequest) -> str:
        evidence = self._join_excerpts(request.evidence_excerpts)
        caveats = self._join_caveats(request.caveats)
        posture = request.support_posture or "insufficient"
        policy = request.policy_outcome or "allow"

        if not evidence:
            return (
                "I cannot support that claim from the current local corpus. "
                "The safest next step is to add a stronger local source or narrow the claim."
            )

        if policy in {"block", "abstain"}:
            return (
                "I do not have enough grounded local support to answer that as fact. "
                f"The closest relevant local material says: {evidence}. "
                f"Caveats: {caveats or 'evidence remains too thin for a trustworthy assertion.'}"
            )

        if policy in {"soften", "escalate"} or posture in {"mixed", "weak", "conflicted"}:
            return (
                "From the current local corpus, I can only offer a cautious read. "
                f"Relevant passages point to: {evidence}. "
                f"Caveats: {caveats or 'support is partial and should not be overstated.'}"
            )

        return (
            "The current local evidence supports a grounded answer. "
            f"Relevant passages point to: {evidence}. "
            f"Caveats: {caveats or 'none surfaced in the current local slice.'}"
        )

    def _exploration_text(self, request: GenerationRequest) -> str:
        return (
            "This reads more like an interpretation or internal-state claim than a clean external fact. "
            "I can help explore it, but I should not pretend the local corpus can verify it."
        )

    def _clarification_text(self, request: GenerationRequest) -> str:
        missing = ", ".join(request.missing_details) if request.missing_details else "key specifics"
        return (
            "I need a little more detail before I can score this honestly. "
            f"Please clarify: {missing}."
        )

    def _conversational_text(self, request: GenerationRequest) -> str:
        evidence = self._join_excerpts(request.evidence_excerpts)
        if evidence:
            return (
                "I do not see a checkable claim yet, but the closest local material says: "
                f"{evidence}. If you want a scored Support Profile, restate it as a concrete factual claim."
            )
        return (
            "I do not see a checkable claim yet. If you want a grounded answer, give me a concrete factual claim "
            "or ask a repo-specific question I can route through the local corpus."
        )

    def _join_excerpts(self, excerpts: tuple[str, ...]) -> str:
        cleaned = [self._clean_excerpt(excerpt) for excerpt in excerpts[:2] if excerpt.strip()]
        return " ".join(cleaned)

    def _join_caveats(self, caveats: tuple[str, ...]) -> str:
        cleaned = [self._clean_excerpt(caveat, max_length=140) for caveat in caveats[:2] if caveat.strip()]
        return " ".join(cleaned)

    def _clean_excerpt(self, text: str, *, max_length: int = 200) -> str:
        collapsed = re.sub(r"\s+", " ", text).strip()
        if len(collapsed) <= max_length:
            return collapsed
        return f"{collapsed[: max_length - 3].rstrip()}..."
