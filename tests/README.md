# `tests/`

This directory explains **what we are testing right now** and **why those tests exist**.

Since the codebase is still early, our tests are not trying to prove that the whole product works. They are trying to prove that the **foundation is stable**.

## Current test files

- `test_contracts.py`
- `test_retrieval_service.py`
- `test_model_registry.py`
- `test_verifier_service.py`
- `test_policy_service.py`
- `bootstrap.py`

## Why these tests exist

At this stage, there are five big risks:

1. we accidentally change a public ESCO contract
2. we build the retrieval flow in a way that breaks provenance or hides bad input
3. we let model defaults drift away from the decisions we already locked in docs
4. we let routing logic drift away from the locked Phase 2 contract
5. we let policy outcomes become more assertive than the evidence allows

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

## `test_verifier_service.py`

This file protects the first executable version of the **Phase 2 routing contract**.

What it checks:

- specific factual claims route to `Support Profile`
- relational or internal-state claims route to `Exploration`
- underspecified empirical claims route to `Clarification`
- prompts without assertive claims stay conversational
- mixed prompts still route the first empirical claim
- Support Profiles contain the locked metrics
- conflicting evidence surfaces counterevidence and a conflicted posture
- consequences mode returns structured downstream effects

Why that matters:

- the project now has a real routing layer, not just documentation
- we want deterministic behavior before introducing model-assisted routing
- these tests keep the first verification rules inspectable while the system is still young

## `test_policy_service.py`

This file protects the first executable version of the **policy gate**.

What it checks:

- conversational prompts are allowed to stay conversational
- Exploration is allowed
- Clarification softens
- Support Profile with no evidence abstains
- high-impact unsupported claims block
- supported profiles allow
- high-impact conflicted profiles escalate

Why that matters:

- ESCO's design depends on evidence and policy constraining the final answer
- this is the first place where the repo enforces "do not bluff"
- the tests make sure policy outcomes stay aligned with the Phase 2 contract

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
- audit event emission for verifier and policy decisions
- OPA or Rego-backed policy enforcement
- end-to-end user request flows

So the current tests are not "the whole system works" tests.

They are "the foundation is not drifting while we build" tests.
