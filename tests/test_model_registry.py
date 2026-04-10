from __future__ import annotations

import unittest

from tests import bootstrap  # noqa: F401

from esco_contracts import DEFAULT_FALLBACK_MODEL_ID, DEFAULT_PRIMARY_MODEL_ID
from esco_runtime.registry import LocalModelRegistry


class ModelRegistryTests(unittest.TestCase):
    def test_default_registry_uses_locked_phase_zero_models(self) -> None:
        registry = LocalModelRegistry.build_default()
        self.assertEqual(registry.get_primary().model_id, DEFAULT_PRIMARY_MODEL_ID)
        self.assertEqual(registry.get_fallback().model_id, DEFAULT_FALLBACK_MODEL_ID)

    def test_registry_falls_back_when_ram_is_too_low(self) -> None:
        registry = LocalModelRegistry.build_default()
        self.assertEqual(registry.choose_for_available_ram(8).model_id, DEFAULT_FALLBACK_MODEL_ID)
        self.assertEqual(registry.choose_for_available_ram(32).model_id, DEFAULT_PRIMARY_MODEL_ID)


if __name__ == "__main__":
    unittest.main()
