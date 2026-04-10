# ESCO Agent Guide

This file is the quick-start guide for any human or coding agent working in this repository.

Use it as the repo-local source of truth for:

- what ESCO is trying to become
- what phase the codebase is currently in
- where the architectural decisions live
- how to work safely without drifting from the roadmap

## Project Purpose

ESCO stands for ethics, sovereignty, and coherence.

The project goal is to build a local-first, evidence-governed AI platform that routes claims carefully, surfaces inspectable support, and applies policy before asserting anything as fact.

The long-term platform supports multiple domain bots, but the shared ESCO platform comes first.

## Current Build Stage

The repository is still in the early platform phases.

Current order of work:

1. Phase 0: architecture and governance baseline
2. Phase 1: local inference, corpus, and retrieval foundation
3. Phase 2: verification, policy, and claim routing
4. Phase 3: audit, evaluation, secure retrieval, memory, and orchestration
5. Phase 4: SocraBot pilot
6. Phase 5: BillBot pilot
7. Phase 6: expansion planning

Important constraint:

- do not start domain-bot implementation before the shared platform baseline is stable

## Core Working Agreements

- Build the platform before the bots.
- Keep ESCO local-first and evidence-governed.
- Treat the kernel, policy layer, audit spine, memory consent, orchestration, retrieval, provenance, and evaluation harness as shared platform work.
- Keep the private-core versus transparent-surface split aligned with the ADRs.
- No web search in the MVP until the roadmap says it is time.
- Prefer small, teachable changes over large opaque ones.

The user prefers a teach-mode style when learning:

- intent
- code
- line-by-line explanation
- micro-test
- short quiz or recap when helpful

That teaching preference matters most when introducing new Python patterns or architecture.

## Repository Map

### Product and architecture docs

- `README.md`
  - project overview and resource links
- `resources/README.md`
  - large project context, goals, and historical design notes
- `resources/roadmaps/esco-implementation-plan.md`
  - current execution order and delivery rules
- `resources/roadmaps/esco-phased-roadmap.md`
  - phased architecture roadmap

### Source-of-truth architecture artifacts

- `resources/adrs/`
  - architecture decisions
- `resources/schemas/`
  - JSON schemas for stable records
- `resources/contracts/`
  - platform contracts that code should follow
- `resources/validation/`
  - validation matrix for locked assumptions and scenarios

### Python code

- `src/esco_contracts/`
  - typed shared records and constants
- `src/esco_retrieval/`
  - ingestion, retrieval, and provenance seams
- `src/esco_runtime/`
  - local model registry and runtime adapter seams

### Infrastructure and examples

- `infra/compose.yaml`
  - local Postgres and Qdrant stack
- `corpus/starter/`
  - starter corpus placeholder
- `resources/diagrams/`
  - exported architecture and roadmap diagrams

### Tests

- `tests/`
  - foundation checks for contracts, retrieval behavior, and runtime defaults

## Read Order For New Contributors

If you are new to the repo, read in this order:

1. `README.md`
2. `resources/README.md`
3. `resources/roadmaps/esco-implementation-plan.md`
4. `resources/adrs/0001-private-core-vs-transparent-surface.md`
5. `resources/contracts/`
6. `src/README.md`
7. package-specific README files in `src/`
8. `tests/README.md`

That order gives you the "why" before the "how".

## Local Development Workflow

Use a Python virtual environment.

Recommended setup from the repo root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

The codebase currently uses a `src/` layout.

That means local commands usually need `PYTHONPATH=src` unless the package is installed in editable mode.

Useful commands:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
python3 -m mypy src tests
pnpm test
docker compose -f infra/compose.yaml up -d
```

## Coding Expectations

- Prefer clear dataclasses and typed interfaces over clever abstractions.
- Preserve the stable public contract shapes defined in `resources/contracts/` and `resources/schemas/`.
- If you change a contract, update the matching documentation and tests in the same slice of work.
- Keep provenance attached to evidence; do not introduce "magic text" without source metadata.
- Favor append-only and inspectable records for audit-relevant data.
- If a behavior is temporary or heuristic, say so in code comments or nearby docs.

## Documentation Sync Rules

When a change affects architecture or workflow, update the relevant docs in the same PR:

- architecture choice -> `resources/adrs/`
- schema or record shape -> `resources/schemas/`
- behavior contract -> `resources/contracts/`
- package behavior -> package `README.md`
- test intent -> `tests/README.md`
- high-level project state -> `README.md` or roadmap docs

If Figma diagrams change, keep the exported assets in `resources/diagrams/` and keep the top-level `README.md` links current.

## Tracker Workflow

Use Linear, GitHub, and Notion together rather than treating the repo as the only source of planning truth.

Expected workflow:

1. Move the active Linear ticket to `In Progress` before implementation starts.
2. Keep the matching GitHub issue aligned with the implementation scope.
3. Open a PR as soon as the slice is reviewable.
4. Move the Linear ticket to `In Review` when the PR is opened.
5. Close or complete the GitHub issue and Linear ticket only after the PR is merged and the tracker state matches reality.
6. Update the ESCO Notion planning page when roadmap-level status changes or new major artifacts are added.

## Design Constraints That Should Not Drift Quietly

- ESCO is local-first before it is web-enabled.
- Support Profile is the inspectable evidentiary header.
- Required Support Profile metrics are:
  - `premise_validity`
  - `source_convergence`
  - `temporal_relevance`
  - `internal_consistency`
  - `counterevidence_presence`
- Claim routing modes are:
  - `Support Profile`
  - `Exploration`
  - `Clarification`
- "What happens if this is false?" is a first-class mode, not a side feature.
- The private-core versus transparent-surface boundary is intentional and should not be casually collapsed.

## If You Are Unsure

- prefer the roadmap and contracts over ad hoc interpretation
- prefer small, reversible steps over broad rewrites
- prefer updating docs and tests together with code
- preserve user changes unless explicitly told otherwise

When in doubt, pause and align the implementation with the current phase instead of jumping ahead to a later-layer feature.
