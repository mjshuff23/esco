# ESCO

ESCO stands for ethics, sovereignty, and coherence.

This repository is the build-out of a local-first, evidence-governed AI platform. The long-term goal is not just to run a model locally. The goal is to build a system that:

- routes claims carefully instead of bluffing
- separates evidence from interpretation
- surfaces inspectable support through a Support Profile
- applies policy before asserting something as fact
- stays modular enough to support later domain bots such as SocraBot and BillBot

## What We Are Aiming For

The target system shape is a platform with these layers:

1. local inference
2. corpus and retrieval
3. verification and claim routing
4. policy and ethics gating
5. audit, evaluation, memory, and orchestration
6. domain-specific bots built on top of the shared platform

The platform comes before the bots. That is a deliberate design choice.

Today the repo is focused on making the platform contracts executable and testable before any polished product surface exists.

## Where The Project Is Right Now

As of 2026-04-10, the project is in the foundation-to-kernel transition:

- Phase 0 is done
  - architecture decisions, schemas, and contracts are written under `resources/`
- Phase 1 is implemented in the repo
  - shared contracts, retrieval seams, local model registry, local infra scaffolding, and foundation tests exist
- Phase 2 is implemented in the repo
  - verification, claim routing, and policy gating are now part of the executable platform baseline
- Phase 3 is next
  - audit, evaluation, secure retrieval, memory consent, and orchestration are the next build target

In practical terms, the repo already has the beginnings of:

- `esco_contracts`
  - shared types and constants
- `esco_retrieval`
  - ingestion, retrieval, provenance, and test doubles
- `esco_runtime`
  - local model config and adapter seams
- `esco_verifier`
  - deterministic routing and Support Profile logic
- `esco_policy`
  - deterministic evidence-governed policy outcomes
- `esco_audit`
  - append-only audit entry scaffolding
- `esco_orchestrator`
  - a local-only orchestration seam and CLI demo path

## What Comes Next

The next major step is Phase 3:

- audit logging
- evaluation harnesses
- secure retrieval and prompt-injection containment
- memory consent handling
- orchestration between retrieval, verification, policy, and runtime

Only after the shared platform is stable do we move into the first domain pilots:

1. SocraBot
2. BillBot

MedBot, ArchiveBot, Light Web, and other expansion work stay later on purpose.

## Repo Map

### Code

- `src/esco_contracts/`
  - shared typed records and locked public constants
- `src/esco_retrieval/`
  - retrieval interfaces, service logic, and in-memory testing helpers
- `src/esco_runtime/`
  - local model configuration and runtime seams
- `src/esco_audit/`
  - append-only audit entry scaffolding
- `src/esco_orchestrator/`
  - local orchestration and CLI demo helpers

### Architecture and planning

- `resources/adrs/`
  - architecture decisions
- `resources/contracts/`
  - locked behavior contracts
- `resources/schemas/`
  - JSON schemas for stable records
- `resources/roadmaps/`
  - current phased roadmap and implementation plan
- `resources/validation/`
  - validation matrix for early architecture assumptions

### Diagrams

- `resources/diagrams/`
  - exported architecture and roadmap diagrams

## How To Get Oriented Quickly

Recommended read order:

1. `resources/roadmaps/esco-implementation-plan.md`
2. `resources/roadmaps/esco-phased-roadmap.md`
3. `resources/contracts/verification-and-policy-contract.md`
4. `src/README.md`
5. `tests/README.md`

If you are new to the Python side of the repo, `src/README.md` is the fastest way to understand how the packages fit together.

## Local Workflow

Set up a Python virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

Run the current checks from the repo root:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
python3 -m mypy src tests
pnpm test
```

Bring up the local infra stack when needed:

```bash
docker compose -f infra/compose.yaml up -d
```

Try the current local demo lane:

```bash
PYTHONPATH=src python -m esco_cli "Phase 2 is implemented in the repo."
```

## Key Resources

### Roadmaps and formal docs

- [Implementation Plan](resources/roadmaps/esco-implementation-plan.md)
- [Phased Roadmap](resources/roadmaps/esco-phased-roadmap.md)
- [Verification and Policy Contract](resources/contracts/verification-and-policy-contract.md)
- [Private Core vs Transparent Surface ADR](resources/adrs/0001-private-core-vs-transparent-surface.md)

### Figma diagrams

Repo-local exported snapshots in `resources/diagrams/` are the tracked references used in this repository.

The links below are the original 2026-04-10 Figma `create-diagram` URLs and should be replaced with stable board URLs before they are treated as the canonical live references.

- [ESCO Current Architecture Foundation](https://www.figma.com/online-whiteboard/create-diagram/f8865f06-009f-4070-9056-879ff579dc12?utm_source=other&utm_content=edit_in_figjam&oai_id=&request_id=4d1f5606-1065-4ce8-9baa-80ed1d6e6398)
- [ESCO Target Architecture By Phase](https://www.figma.com/online-whiteboard/create-diagram/ae4ecbe1-d192-4213-be91-8e3bcc7bd7ad?utm_source=other&utm_content=edit_in_figjam&oai_id=&request_id=d80e93df-f6bb-40ec-9e32-e108b7369335)
- [ESCO Near-Term Roadmap Zoom In](https://www.figma.com/online-whiteboard/create-diagram/ea6f696b-539e-4804-b942-31cce51256dc?utm_source=other&utm_content=edit_in_figjam&oai_id=&request_id=809ce14a-d494-4a30-bc4b-94824c388a81)

### Archived root README

The previous long-form root README has been archived here:

- [2026-04-10 root README archive](resources/archive/2026-04-10-root-readme-archive.md)
