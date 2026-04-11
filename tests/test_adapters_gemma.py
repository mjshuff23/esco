"""Tests for the Gemma adapter scaffold.

These tests perform a focused import smoke test and a lazy-load unit test
which simulates missing runtime dependencies (`transformers` / `torch`).
"""

import builtins

import pytest

from esco_runtime import adapters_gemma
from esco_runtime.adapters_gemma import GemmaLocalAdapter
from esco_runtime.models import ModelRuntimeConfig


def test_import_adapter():
    # Basic smoke import: module and class should import cleanly (no heavy imports).
    assert hasattr(adapters_gemma, "GemmaLocalAdapter")
    assert GemmaLocalAdapter is not None


def test_lazy_load_raises_when_transformers_missing(monkeypatch):
    real_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "transformers" or name.startswith("transformers."):
            raise ImportError("mocked missing transformers")
        if name == "torch" or name.startswith("torch."):
            raise ImportError("mocked missing torch")
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    cfg = ModelRuntimeConfig(
        model_id="google/gemma-4-26B-it",
        family="gemma",
        role="inference",
        license_name="Apache-2.0",
        quantization="fp16",
        min_recommended_ram_gb=16,
        context_window_tokens=32768,
    )
    adapter = GemmaLocalAdapter(config=cfg)
    with pytest.raises(RuntimeError):
        adapter._ensure_loaded()
