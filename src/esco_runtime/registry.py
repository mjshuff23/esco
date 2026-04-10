"""Default local model registry for the offline MVP."""

from __future__ import annotations

from dataclasses import dataclass

from esco_contracts.constants import DEFAULT_FALLBACK_MODEL_ID, DEFAULT_PRIMARY_MODEL_ID

from .models import ModelRuntimeConfig


def _default_configs() -> dict[str, ModelRuntimeConfig]:
    return {
        DEFAULT_PRIMARY_MODEL_ID: ModelRuntimeConfig(
            model_id=DEFAULT_PRIMARY_MODEL_ID,
            family="Ministral",
            role="primary",
            license_name="Apache-2.0",
            quantization="Q4_K_M",
            min_recommended_ram_gb=16,
            context_window_tokens=131072,
            notes=(
                "Default local-first baseline for the offline MVP.",
                "Use unless hardware validation proves it too heavy.",
            ),
        ),
        DEFAULT_FALLBACK_MODEL_ID: ModelRuntimeConfig(
            model_id=DEFAULT_FALLBACK_MODEL_ID,
            family="Gemma 4",
            role="fallback",
            license_name="Apache-2.0",
            quantization="Q4_K_M",
            min_recommended_ram_gb=8,
            context_window_tokens=131072,
            notes=(
                "Fallback when the primary model starves retrieval or audit services.",
            ),
        ),
    }


@dataclass
class LocalModelRegistry:
    models: dict[str, ModelRuntimeConfig]

    @classmethod
    def build_default(cls) -> "LocalModelRegistry":
        return cls(models=_default_configs())

    def get(self, model_id: str) -> ModelRuntimeConfig:
        return self.models[model_id]

    def get_primary(self) -> ModelRuntimeConfig:
        return self.get(DEFAULT_PRIMARY_MODEL_ID)

    def get_fallback(self) -> ModelRuntimeConfig:
        return self.get(DEFAULT_FALLBACK_MODEL_ID)

    def choose_for_available_ram(self, available_ram_gb: int) -> ModelRuntimeConfig:
        primary = self.get_primary()
        if available_ram_gb >= primary.min_recommended_ram_gb:
            return primary
        return self.get_fallback()
