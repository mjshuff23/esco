# `tests/`

This directory explains **what we are testing right now** and **why those tests exist**.

Since the codebase is still early, our tests are not trying to prove that the whole product works. They are trying to prove that the **foundation is stable**.

## Current test files

- `test_contracts.py`
- `test_retrieval_service.py`
- `test_model_registry.py`
- `bootstrap.py`

## Why these tests exist

At this stage, there are three big risks:

1. we accidentally change a public ESCO contract
2. we build the retrieval flow in a way that breaks provenance or hides bad input
3. we let model defaults drift away from the decisions we already locked in docs

Each test file protects one of those areas.

## `test_contracts.py`

This file protects the **shared language** of the system.

What it checks:

- the public route names stay locked
- a `SupportProfile` must contain every required metric
- an `EventEnvelope` stays append-only

Why that matters:

- if route names drift, later packages stop agreeing about behavior
- if Support Profile fields drift, the user-facing evidence output becomes unstable
- if event envelopes stop being append-only, the audit story becomes weaker

## `test_retrieval_service.py`

This file protects the **offline evidence lane**.

What it checks:

- ingestion works for a valid document
- retrieval returns evidence with provenance
- provenance resolution maps evidence back to a source domain
- ingestion fails when required provenance is missing
- suspicious prompt-injection text gets flagged

Why that matters:

- ESCO should never treat evidence as magic text with no source
- provenance is central to the whole project
- failing closed on missing provenance is safer than silently accepting bad documents
- prompt-injection markers need to survive retrieval so later layers can respond safely

## `test_model_registry.py`

This file protects the **local model defaults**.

What it checks:

- the registry uses the locked primary and fallback models
- RAM-based fallback behavior works as expected

Why that matters:

- we made explicit model decisions in Phase 0 and Phase 1 docs
- tests make sure the code keeps honoring those decisions

## `bootstrap.py`

This small helper makes the `src` layout work in tests by adding `src/` to `sys.path`.

That lets test files import packages like:

- `esco_contracts`
- `esco_retrieval`
- `esco_runtime`

without needing a full install step first.

## How to run the tests

From the repo root:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Or through the existing package script:

```bash
pnpm test
```

## Why we use `unittest` right now

We are using Python's built-in `unittest` module for now because:

- it keeps the dependency surface tiny
- it is enough for the current size of the project
- it is good for learning and early scaffolding

Later we may move to `pytest` if the suite grows and we want richer fixtures or parametrization.

## What is not tested yet

These are still future concerns:

- real Postgres integration
- real Qdrant integration
- real embedding models
- real local inference
- routing and policy logic
- end-to-end user request flows

So the current tests are not "the whole system works" tests.

They are "the foundation is not drifting while we build" tests.
