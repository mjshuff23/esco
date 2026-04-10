# Phase 0 Validation Matrix

Date: 2026-04-10

## Capability To Module Mapping

Every current ESCO capability is assigned to one primary platform module so later phases do not compete for ownership.

| Capability | Source | Primary module |
| --- | --- | --- |
| API, auth, sessions, uploads, future app surfaces | `README.md`, roadmap | Interaction Gateway |
| Local open-weight model execution | `README.md`, `resources/README.md` | Local Inference Layer |
| Curated objective corpus and provenance-tracked ingestion | `README.md`, `resources/README.md` | Corpus and Retrieval Layer |
| Claim extraction | `README.md` | Verification and Claim Routing Kernel |
| Support Profile scoring | `README.md` | Verification and Claim Routing Kernel |
| Clarification Mode | `README.md` | Verification and Claim Routing Kernel |
| Exploration Mode | `README.md` | Verification and Claim Routing Kernel |
| "What happens if this is false?" mode | `README.md` | Verification and Claim Routing Kernel |
| Symbolic ethics gate | `README.md`, `resources/README.md` | Ethics and Policy Layer |
| Contradiction and coherence checks | `README.md` | Ethics and Policy Layer |
| Leak review and mediated large-model use | `README.md` | Model Orchestration Layer |
| Dual-model verification path | `resources/README.md` | Model Orchestration Layer |
| Web browsing, search, sanitization, injection containment | `resources/README.md` | Web Search and Sanitization Layer |
| Memory consent | `README.md` | Memory and Context Layer |
| Context reconstruction | roadmap | Memory and Context Layer |
| Emotional-state sensing and tone selection | `README.md` | Tone and State Layer |
| Immutable log and reasoning traces | `README.md`, `resources/README.md` | Transparency, Audit, and Evaluation Spine |
| Steward review | `README.md` | Transparency, Audit, and Evaluation Spine |
| Truthfulness, RAG, and injection benchmarks | `resources/README.md` | Transparency, Audit, and Evaluation Spine |
| SocraBot | `README.md` | Domain Modules |
| BillBot | `README.md` | Domain Modules |
| MedBot | `README.md` | Domain Modules |
| ArchiveBot / DeepFile | `README.md` | Domain Modules |
| Legal loophole module | `README.md` | Domain Modules |
| Light Web | `README.md` | Interaction Gateway |
| Misuse and clone-detection backlog | `README.md` | Transparency, Audit, and Evaluation Spine |

## Contract Validation Scenarios

| Scenario | Expected route or outcome | Contract sections exercised |
| --- | --- | --- |
| Grounded factual claim answered from local evidence only | `Support Profile` with provenance-backed evidence | Retrieval, Verification, Audit |
| Underspecified factual claim | `Clarification` | Verification |
| Personal or relational claim | `Exploration` | Verification |
| Claim with conflicting sources | `Support Profile` with `mixed` or `conflicted` posture and surfaced counterevidence | Retrieval, Verification, Audit |
| Retrieved page containing prompt injection text | Content is flagged and treated as tainted evidence, not instructions | Retrieval, Verification, Audit |
| Session with memory disabled | No memory write, `memory.write_skipped` event recorded | Memory, Audit |

## ESC-1 Exit Checks

- Phase 1 can implement ingestion, retrieval, and local inference without redefining schemas.
- Phase 2 can implement routing and Support Profile behavior without renaming any public output fields.
- Phase 3 can add search, sanitization, evaluation, and orchestration without changing the public contracts from Phase 0.
- `ESC-1` remains the only active implementation ticket until its first PR is opened.
