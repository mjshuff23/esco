# ADR 0001: Private Core vs Transparent Surface

Date: 2026-04-10
Status: Accepted

## Context

ESCO is intentionally hybrid-open.

The project vision in `README.md` and `resources/README.md` is consistent on three points:

1. The symbolic and ethical core should not be exposed as a copyable recipe.
2. The user-facing evidence, explanations, and audit artifacts should remain inspectable.
3. The platform must support review, provenance, and human stewardship without revealing the private decision logic that gives ESCO its identity.

Phase 0 therefore needs a stable boundary between what remains private, what is shared only with trusted contributors, and what is intentionally visible to users and reviewers.

## Decision

ESCO will use three visibility bands:

1. `core_private`
   - logic that is not exposed through public documentation, public APIs, or user-visible traces
   - only available to vetted maintainers
2. `internal_restricted`
   - implementation details that can be shared with trusted contributors and operators
   - never required for user-facing explanation
3. `transparent_surface`
   - artifacts designed to be inspectable by users, reviewers, and future transparent UI layers

## Boundary By Capability

| Capability | Visibility band | Notes |
| --- | --- | --- |
| Symbolic comparator heuristics | `core_private` | Keep the scoring and contradiction logic private even when its outcomes are visible. |
| Ethics gate rules implementation | `core_private` | Policy outcomes are inspectable; the internal rule composition is not. |
| Leak-review thresholds and internal comparison heuristics | `core_private` | Only the resulting decision and explanation summary are surfaced. |
| Prompt builder internals and orchestration heuristics | `core_private` | The model adapter interface is stable, but prompt internals are not public API. |
| Abuse, misuse, and clone-detection heuristics | `core_private` | Defer detailed design to a later security ADR. |
| Retrieval ranking implementation details | `internal_restricted` | Evidence references are visible; ranking and weighting details are not contractually public. |
| Model runtime configuration and hardware validation notes | `internal_restricted` | Safe to document for the team without making them user-visible behavior. |
| Steward review procedures | `internal_restricted` | User-visible escalations exist, but reviewer procedures stay internal. |
| Support Profile output | `transparent_surface` | This is a first-class inspectable artifact. |
| Evidence citations and provenance summaries | `transparent_surface` | Users must be able to inspect what evidence supported an answer. |
| Audit summaries and decision outcomes | `transparent_surface` | The system should show what happened without exposing private scoring logic. |
| Clarification, Exploration, and consequences-mode outputs | `transparent_surface` | Modes are part of the public contract. |
| Steward-review artifacts intended for the user | `transparent_surface` | Surface the escalation and its reason, not the hidden internals behind it. |

## Public Contract Rules

The following items are public contract and may not be changed casually in later phases:

- the names and meaning of the primary routing modes: `Support Profile`, `Exploration`, and `Clarification`
- the existence of a first-class consequences mode: `What happens if this is false?`
- the Support Profile metric set:
  - `premise_validity`
  - `source_convergence`
  - `temporal_relevance`
  - `internal_consistency`
  - `counterevidence_presence`
- the existence of append-only audit events
- the existence of opt-in, domain-scoped memory consent

## Consequences

Positive consequences:

- ESCO can remain inspectable at the user surface without publishing the logic it considers sacred.
- Later tickets can expose evidence and decisions safely because the visibility bands are already named.
- The audit contract can explain what happened without reproducing private policy code.

Negative consequences:

- Some internal decisions will only be explainable through summaries and references, not full algorithmic disclosure.
- Team onboarding requires explicit trust and access management.

## Deferred Work

These items are intentionally not locked in this ADR:

- the final anti-cloning or misuse-detection mechanism
- the exact human steward operating model
- whether graph-native storage is needed later for reasoning traces

Those decisions must preserve the visibility bands defined here.
