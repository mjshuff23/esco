"""Runtime-facing model configuration types."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ModelRuntimeConfig:
    model_id: str
    family: str
    role: str
    license_name: str
    quantization: str
    min_recommended_ram_gb: int
    context_window_tokens: int
    notes: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class GenerationRequest:
    route: str
    user_prompt: str
    evidence_refs: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class GenerationResponse:
    model_id: str
    text: str
    used_fallback: bool = False
