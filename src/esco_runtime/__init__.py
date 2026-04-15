"""ESCO local runtime scaffolding."""

from .adapters import LocalModelAdapter, StubLocalModelAdapter
from .adapters_grounded import GroundedDraftAdapter, build_grounded_demo_config
from .models import GenerationRequest, GenerationResponse, ModelRuntimeConfig
from .registry import LocalModelRegistry

__all__ = [
    "GenerationRequest",
    "GenerationResponse",
    "GroundedDraftAdapter",
    "LocalModelAdapter",
    "LocalModelRegistry",
    "ModelRuntimeConfig",
    "StubLocalModelAdapter",
    "build_grounded_demo_config",
]
