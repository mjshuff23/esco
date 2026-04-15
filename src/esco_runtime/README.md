# `esco_runtime`

This package is the start of the local model lane.

Right now it does not run a real model yet. That is intentional. The goal of this package in the current phase is to lock how the rest of the system will *talk to* a local model runner before we choose the exact execution stack.

## The job of this package

The runtime layer will eventually answer questions like:

- which local model are we using?
- what is the fallback if the primary model is too heavy?
- what shape should a generation request take?
- what should a model response return back to the caller?

## Files in this package

- `models.py`
  - typed data structures for runtime config and generation I/O
- `adapters.py`
  - the interface for model runners and the current stub implementation
- `adapters_grounded.py`
  - a deterministic grounded adapter for the local CLI demo lane
- `adapters_gemma.py`
  - an optional Gemma-family adapter that lazy-loads heavyweight runtime deps
- `registry.py`
  - the default model registry for the offline MVP
- `__init__.py`
  - re-exports the package's main symbols

## `models.py`: the data layer

This file contains three simple records:

- `ModelRuntimeConfig`
  - describes one local model option
  - includes family, license, quantization, context window, and RAM guidance
- `GenerationRequest`
  - the input we will eventually pass to a local model
  - includes the route, user prompt, evidence refs, evidence excerpts, and response guidance from policy and verification
- `GenerationResponse`
  - the output a model runner should return
  - includes model id, generated text, and whether a fallback was used

These are small on purpose. The current goal is to make the interface obvious before we make it powerful.

## `adapters.py`: the abstraction seam

This file uses a `Protocol` again.

- `LocalModelAdapter`
  - anything that implements `generate(...)` with the right signature can act as a runtime adapter
- `StubLocalModelAdapter`
  - the placeholder implementation for now
  - it raises `NotImplementedError` so we do not accidentally pretend the model lane exists before it really does

This is a useful pattern when learning:

- define the shape first
- plug in a fake implementation
- replace it later with the real one

## `adapters_grounded.py`: the bridge adapter

This file exists so the repo can exercise an end-to-end local interaction path
before a heavier runtime dependency is required.

- `GroundedDraftAdapter`
  - builds a cautious answer from the current route, policy outcome, caveats,
    and evidence excerpts
- `build_grounded_demo_config()`
  - returns the lightweight runtime config used by the local CLI demo

This adapter is useful for:

- local orchestration and CLI demos
- deterministic tests
- proving the runtime seam before a real model runner is ready

It is not meant to be the long-term inference layer.

## `adapters_gemma.py`: the optional real runner

This file is the first adapter that points toward actual local inference.

It lazy-loads `transformers` and `torch` so the repo does not need those
dependencies just to run the scaffold or the CLI demo.

## `registry.py`: picking defaults

This file answers the question: "What local models are we expecting to use right now?"

Current defaults:

- primary: `ministral-8b-instruct`
- fallback: `gemma-4-e4b`

The registry is a very small manager around those configs.

Useful methods:

- `build_default()`
  - create the default registry
- `get_primary()`
  - return the preferred model config
- `get_fallback()`
  - return the fallback model config
- `choose_for_available_ram()`
  - simple RAM-based choice between the primary and fallback

## Why this package matters already

Even before real inference exists, this package gives the project:

- one place to lock model defaults
- one place to describe the request and response shape
- one seam where a future llama.cpp, Ollama, vLLM, or other local runner can plug in
- one lightweight adapter that keeps the current local orchestrator usable

That keeps model decisions from leaking all over the codebase.

## What is missing on purpose

This package does **not** yet include:

- a production-ready local inference backend
- prompt construction
- multi-model orchestration
- streaming responses
- hardware probing
- fallback decisions based on real benchmarking

Those are later steps.

## Mental model

If `esco_contracts` defines the nouns and `esco_retrieval` gathers evidence, then `esco_runtime` is where a local model will eventually consume that evidence and generate text in a controlled shape.
