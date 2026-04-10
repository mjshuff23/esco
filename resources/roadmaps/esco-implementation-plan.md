# ESCO Implementation Plan

Date: 2026-04-10

## Core Decisions

1. We will start with the architecture baseline before building features.
2. We will build ESCO as a local-first, evidence-governed platform before branching into domain bots.
3. We will treat the ESCO kernel, policy and ethics layer, audit spine, memory consent system, model orchestration, retrieval layer, provenance schema, and evaluation harness as shared platform work.
4. We will move the active ticket to `In Progress` before implementation starts.
5. We will move the ticket to `In Review` once a PR is opened.
6. We will not start SocraBot or BillBot until the local-first evidence foundation, policy rules, and evaluation baseline are working.
7. We will use SocraBot and BillBot as the first domain proofs that the shared ESCO architecture can support different reasoning styles.
8. We will leave MedBot, ArchiveBot, and Light Web as expansion work until the platform and pilot bots are stable.

## Execution Order

1. Phase 0: Architecture and Governance Baseline
2. Phase 1: Local Inference, Corpus, and Retrieval Foundation
3. Phase 2: Verification, Policy, and Claim Routing
4. Phase 3: Audit, Evaluation, Secure Retrieval, Memory, and Orchestration
5. Phase 4: SocraBot Pilot
6. Phase 5: BillBot Pilot
7. Phase 6: Expansion Wave Planning

## Immediate Build Focus

The first implementation wave should produce four concrete artifacts:

- an ADR for the private-core versus transparent-surface split
- an event and metadata schema for evidence, support profiles, ethics decisions, and audit entries
- a local model selection note with runtime constraints
- a corpus and retrieval contract for the first offline-only MVP

## Artifact Locations

- ADRs: `resources/adrs/`
- Schemas: `resources/schemas/`
- Contracts: `resources/contracts/`
- Validation matrix: `resources/validation/phase-0-validation-matrix.md`

## Definition of “Ready to Build”

We can begin implementation when:

- the architecture baseline ticket is active in Linear
- the expected outputs for Phase 0 are named and scoped
- the matching GitHub issue is the repo-side source of truth
- the first PR can be opened against a clearly bounded artifact set
