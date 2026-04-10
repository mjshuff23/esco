"""Model adapter seam for later local inference integration."""

from __future__ import annotations

from typing import Protocol

from .models import GenerationRequest, GenerationResponse, ModelRuntimeConfig


class LocalModelAdapter(Protocol):
    config: ModelRuntimeConfig

    def generate(self, request: GenerationRequest) -> GenerationResponse:
        """Generate a response using a local model runner."""


class StubLocalModelAdapter:
    """Placeholder adapter until the actual local runner is wired in."""

    def __init__(self, config: ModelRuntimeConfig) -> None:
        self.config = config

    def generate(self, request: GenerationRequest) -> GenerationResponse:
        raise NotImplementedError(
            f"Local inference for {self.config.model_id} is not wired yet. "
            "Phase 1 currently locks the registry and adapter seam only."
        )
