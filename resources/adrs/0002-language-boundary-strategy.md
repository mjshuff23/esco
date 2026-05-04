# ADR 0002: Language Boundary Strategy

Date: 2026-05-04
Status: Accepted

## Context

ESCO is moving from an executable Python scaffold into the larger Phase 3
platform: audit, evaluation, secure retrieval, memory consent, and orchestration.

The project needs high performance eventually, but the current bottleneck is not
raw runtime speed. The current bottleneck is making the platform rules,
schemas, audit events, and evaluation behavior stable enough that later
optimized services can be swapped in without changing the public contract.

The language strategy therefore needs to support two goals at the same time:

1. Keep the current platform easy to inspect, teach, and revise while the
   contracts are still settling.
2. Name the future boundaries where Go, Rust, and TypeScript should be used once
   a module has stable behavior and a clear performance or safety reason to
   leave the Python reference path.

## Decision

ESCO will use a contract-first, multi-language boundary strategy.

The default Phase 3 reference implementation remains Python. Other languages
may be introduced behind stable contracts when they have a clear ownership role:

- Python = logic prototyping and reference control plane
- Go = I/O scaling and service coordination
- Rust = safety kernels and deterministic rule engines
- TypeScript = transparent surface and interactive product experience

This is not a mandate to rewrite existing Python packages. It is a boundary
decision for when a package or module is ready to be promoted into a more
specialized implementation.

## Boundary By Language

| Language | ESCO role | Good fit | Not the default for |
| --- | --- | --- | --- |
| Python | Logic prototyping and reference control plane | Contracts, orchestration, verification heuristics, policy prototypes, evaluation harnesses, local demos, test doubles | High-throughput storage ingestion, browser-local kernels, latency-critical services after profiling proves the need |
| Go | I/O scaling and service coordination | Audit ingestion services, retrieval/search gateway, streaming API edges, runtime coordination, Postgres/Qdrant workers, Connect/gRPC or HTTP service boundaries | Core symbolic reasoning before rule semantics are stable |
| Rust | Safety kernels and deterministic rule engines | Fallacy scoring kernels, policy/rule evaluation kernels, contradiction/coherence checks, prompt-injection classifiers, browser-local WASM modules | Rapidly changing orchestration logic or UI state |
| TypeScript | Transparent surface and interactive product experience | Next.js UI, Evidence Inspector, chat console, reasoning trace graph, review tools, browser WASM host integration | Private-core policy logic or storage-heavy backend workers |

## Promotion Rules

A Python module may be promoted to Go or Rust only when all of the following are
true:

1. The input and output contract is stable in `resources/contracts/`,
   `resources/schemas/`, or an ADR.
2. The behavior has regression tests or evaluation fixtures that can run against
   both the Python reference path and the promoted implementation.
3. There is a named reason for promotion:
   - throughput or concurrent I/O pressure for Go
   - safety, determinism, or WASM-local execution for Rust
4. The Python reference path remains available until the replacement has
   equivalent coverage and replayable audit behavior.
5. The promoted implementation does not weaken the private-core versus
   transparent-surface boundary from ADR 0001.

## Initial Application

For Phase 3:

- Keep `esco_orchestrator`, `esco_verifier`, `esco_policy`, `esco_audit`, and
  `esco_retrieval` in Python while contracts and evaluation fixtures are still
  being refined.
- Build the frontend/API surface as TypeScript plus a small Python API first,
  so the Evidence Inspector and chat console exercise the audited Python
  reference path directly.
- Treat persistent audit storage and evaluation fixtures as higher priority than
  a service rewrite.

For later scaling:

- Consider Go for audit and retrieval workers once Postgres/Qdrant persistence,
  event volume, and streaming needs are real.
- Consider Rust for SocraBot fallacy scoring after the taxonomy, thresholds,
  reset behavior, and audit events have stable fixtures.
- Consider Rust/WASM for browser-local fallacy feedback only after the same
  kernel has server-side regression coverage.
- Keep TypeScript at the product edge, not as the authority for policy or
  verification decisions.

## Consequences

Positive consequences:

- ESCO can optimize without turning language choice into architecture drift.
- The current Python code stays valuable as a readable reference model instead
  of becoming throwaway scaffolding.
- Go and Rust enter the system where they have measurable leverage.
- TypeScript can move quickly on the transparent user surface without owning
  private-core logic.

Negative consequences:

- ESCO will temporarily duplicate some behavior when a Python reference module
  is promoted to Go or Rust.
- Cross-language contracts require stricter schema discipline and test fixtures.
- The fastest-looking implementation language may be deferred until the module's
  semantics are stable enough to preserve.

## Deferred Work

This ADR does not decide:

- the final local model runner stack
- whether service boundaries use Connect, gRPC, plain HTTP, or another transport
- whether Rust policy kernels are compiled into the server, browser WASM, or both
- when SocraBot or BillBot domain modules begin implementation

Those decisions must preserve the Phase 3 platform-first roadmap and the
visibility boundary from ADR 0001.
