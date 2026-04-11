"""Adapter to run Gemma-family models locally (optional runtime).

This adapter is intentionally lightweight and performs lazy imports so the
project does not require `transformers`/`torch` at install time. If those
libraries are not present, the adapter raises a clear RuntimeError explaining
what to install.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Any
import importlib

from esco_runtime.adapters import LocalModelAdapter
from esco_runtime.models import GenerationRequest, GenerationResponse, ModelRuntimeConfig


@dataclass
class GemmaLocalAdapter(LocalModelAdapter):
    config: ModelRuntimeConfig
    model_id: Optional[str] = None
    _processor: Any | None = None
    _model: Any | None = None

    def _ensure_loaded(self) -> None:
        if self._model is not None and self._processor is not None:
            return
        try:
            transformers = importlib.import_module("transformers")
            AutoProcessor = getattr(transformers, "AutoProcessor")
            AutoModelForCausalLM = getattr(transformers, "AutoModelForCausalLM")
            torch = importlib.import_module("torch")
        except Exception as exc:  # pragma: no cover - runtime dependency check
            raise RuntimeError(
                "To use Gemma adapter install `transformers` and `torch` (and optionally `accelerate`)."
            ) from exc

        model_id = self.model_id or self.config.model_id
        # Load processor and model lazily. Caller should ensure hardware availability.
        processor = AutoProcessor.from_pretrained(model_id)
        model = AutoModelForCausalLM.from_pretrained(model_id, device_map="auto")
        # call eval() on the concrete model local variable to avoid optional-member warnings
        model.eval()
        self._processor = processor
        self._model = model

    def generate(self, request: GenerationRequest) -> GenerationResponse:
        """Generate text for a simple chat-style prompt.

        This method uses the Gemma chat template shown in the official model
        cards. It's a minimal implementation intended for integration testing
        and examples; production usage should handle streaming, error cases,
        device placement, and batching.
        """
        self._ensure_loaded()
        assert self._processor is not None and self._model is not None

        messages = [
            {"role": "system", "content": "You are an assistant."},
            {"role": "user", "content": request.user_prompt},
        ]

        text = self._processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True, enable_thinking=False)
        inputs = self._processor(text=text, return_tensors="pt").to(self._model.device)
        input_len = inputs["input_ids"].shape[-1]
        outputs = self._model.generate(**inputs, max_new_tokens=512)
        response = self._processor.decode(outputs[0][input_len:], skip_special_tokens=False)
        parsed = self._processor.parse_response(response)
        # parsed may be a dict or string depending on the processor implementation
        text_out = parsed if isinstance(parsed, str) else parsed.get("response", str(parsed))
        return GenerationResponse(model_id=self.config.model_id, text=text_out)
