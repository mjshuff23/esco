# `src/` Overview

This directory is the Python application layer for ESCO.

If you have not touched Python in a while, the important thing to know is that we are using a **`src` layout**. That means our importable Python packages live under `src/` instead of at the repo root.

Today, the codebase is still in the **foundation** stage. We are not building the full product yet. We are creating the stable pieces that later features will plug into without forcing a rewrite.

## Current packages

- `esco_contracts`
  - the shared language of the system
  - typed records, constants, and validation rules
  - this is where ESCO's Phase 0 contracts become code
- `esco_retrieval`
  - the offline-first evidence lane
  - ingestion, chunking, embeddings, vector lookup, and provenance resolution
  - currently uses in-memory test implementations so we can validate the shape before wiring real infrastructure
- `esco_runtime`
  - the local model lane
  - model configs, request and response types, and the adapter seam that future local inference runners will implement

## How these packages fit together

The current shape is:

1. `esco_contracts` defines the records everyone agrees on.
2. `esco_retrieval` uses those records to ingest and retrieve evidence.
3. `esco_runtime` is where a local model will eventually consume routed prompts and evidence-aware requests.

In other words:

- `esco_contracts` answers: "What is a claim, evidence record, or audit event?"
- `esco_retrieval` answers: "How do we get evidence and provenance?"
- `esco_runtime` answers: "How do we plug in a local model without hardcoding one runner everywhere?"

## Read this first

If you are learning the project as you go, this order will make the most sense:

1. `src/esco_contracts/README.md`
2. `src/esco_retrieval/README.md`
3. `src/esco_runtime/README.md`

Then come back to the code itself.

## Python concepts used here

These are the main Python ideas in the current scaffold:

- `dataclass`
  - a lightweight way to define data containers without writing a lot of boilerplate
  - used for records like `Claim`, `SupportProfile`, and `ModelRuntimeConfig`
- `Protocol`
  - a typing feature that says "anything with these methods is good enough"
  - used so the retrieval service can depend on interfaces instead of concrete implementations
- `__init__.py`
  - marks a directory as a Python package and often re-exports the important symbols
- `__future__.annotations`
  - lets us write modern type hints cleanly without worrying about forward references as much

## Why this structure matters

We are trying to avoid a very common early-project mistake: putting business rules, infrastructure decisions, and experimental code all in one place.

This layout keeps:

- contracts separate from behavior
- behavior separate from infrastructure
- test doubles separate from production code

That separation is what will let us move from stubs to real Postgres, Qdrant, and local model execution without tearing everything apart.

## Running code locally

The simplest current workflow is:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
PYTHONPATH=src python -m unittest discover -s tests -v
```

Later we will likely move to editable installs and a fuller dependency set, but this is enough for the current scaffold.
