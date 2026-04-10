# ESCO Phased Roadmap

Date: 2026-04-10

## Architecture Confidence

Yes, I feel confident developing an architecture here.

The repository still does not contain implementation code, but `resources/README.md` makes the starting path much more concrete. The project is no longer just a high-level ESCO concept map; it now has a practical starter shape:

- a local-first inference lane
- a provenance-tracked corpus and RAG lane
- a policy and verification lane
- a browsing and prompt-injection defense lane
- an evaluation and reproducibility lane
- the ESCO-specific memory, tone, audit, and domain-bot layers on top

What is still under-specified is not the overall architecture. The main open questions are implementation choices inside that architecture:

- which permissively licensed local model becomes the first baseline
- which UI stack should front the system
- whether the policy layer starts with OPA, Cedar, or a thinner custom rules adapter
- which embedding model and vector store become the first default
- whether the audit graph stays in Postgres first or gets a dedicated graph projection later
- how much of the inner core remains private versus mirrored through transparent adapters
- when web search should be enabled relative to the offline MVP

## Recommended System Shape

The cleanest starting shape for ESCO is a modular, local-first platform with a private inner core, transparent outer surfaces, and an evidence gate between the model and the final answer.

### Core platform layers

1. Interaction Gateway
   - API, auth, session handling, user preference intake, file upload entrypoints
   - routes all user requests into the orchestrator and ESCO kernel

2. Local Inference Layer
   - local LLM runtime
   - quantized model runner or serving stack
   - permissively licensed baseline model selection

3. Corpus and Retrieval Layer
   - curated local corpus
   - provenance-tracked raw document store
   - chunking and metadata pipeline
   - embeddings plus vector index
   - retrieval with metadata filtering

4. Verification and Claim Routing Kernel
   - claim extraction
   - intent clarification
   - evidence check
   - support-profile routing
   - exploration-mode routing
   - clarification-mode routing
   - "what happens if this is false?" consequences mode

5. Ethics and Policy Layer
   - policy engine
   - symbolic rule enforcement
   - contradiction detector
   - coherence scoring
   - action authorization for retrieval, browsing, and tool use
   - steward escalation rules

6. Model Orchestration Layer
   - prompt builder
   - model adapter interface
   - dual-model verification
   - leak-review comparison flow

7. Web Search and Sanitization Layer
   - web search adapter
   - allowlisted sources
   - query caching
   - web content sanitizer
   - prompt-injection containment

8. Memory and Context Layer
   - opt-in memory consent
   - context reconstruction
   - per-domain memory policies
   - document state storage

9. Tone and State Layer
   - user-selected tone target: blunt, balanced, gentle
   - emotional state classifier
   - distress and escalation detection
   - tone router that cannot override truth constraints

10. Transparency, Audit, and Evaluation Spine
   - immutable decision log
   - reasoning trace graph
   - human steward review queue
   - explainable output surface
   - factuality benchmarks
   - RAG evaluation harness
   - prompt-injection and jailbreak regression tests

11. Domain Modules
   - SocraBot
   - BillBot
   - later: MedBot, ArchiveBot, Legal Loophole Bot, Light Web services

### Suggested implementation boundary

- Private core:
  - ethics rules
  - contradiction logic
  - leak-review policy
  - sensitive routing heuristics
- Transparent outer layer:
  - UI
  - support profile output
  - audit traces
  - steward review artifacts
  - domain-specific reports

### Suggested data architecture

- Postgres as the initial source of truth
  - users
  - sessions
  - claims
  - support profiles
  - ethics decisions
  - review tasks
  - memory consent records
  - immutable audit entries
- Object storage or filesystem-backed document store for raw corpus inputs, WARC captures, PDFs, and OCR artifacts
- Vector search as an early capability, not a late optimization
- Metadata store with provenance, source quality flags, and retrieval policy fields
- Graph projection later for reasoning traces and entity relationships if Postgres tables become too limiting

### Suggested service split

- `esco-gateway`
- `esco-runtime`
- `esco-retrieval`
- `esco-verifier`
- `esco-policy`
- `esco-audit-eval`
- `esco-memory`
- `esco-search`
- `esco-model-orchestrator`
- `escobot-socrabot`
- `escobot-billbot`

Monorepo is the right starting point. Separate services can be promoted later only when traffic, privacy boundaries, or compute isolation makes it necessary.

## Phased Roadmap

### Phase 0: Architecture and Governance Baseline

Goal:
Define the non-negotiable platform contract before building features.

Deliverables:

- architecture decision record set
- module boundary map
- domain glossary for ESCO terms
- event schema for claims, evidence, support profiles, ethics decisions, audit entries, and steward review
- closed-core versus open-surface policy
- security and misuse threat model for the platform
- benchmark and evaluation contract for factuality, RAG quality, and injection resistance

Exit criteria:

- every future feature can be placed into a named module
- audit events and review triggers have a stable schema
- the team can explain which parts are private, public, or user-visible

### Phase 1: Local Inference, Corpus, and Retrieval Foundation

Goal:
Stand up the local-first evidence foundation before domain specialization.

Deliverables:

- one permissively licensed local baseline model
- local runtime path with quantized inference
- curated starter corpus
- provenance and metadata schema
- chunking and embedding pipeline
- vector index and retrieval API
- offline-only execution path that works without web search

Exit criteria:

- the system can retrieve grounded local evidence with traceable provenance
- the MVP can answer from the local corpus without external browsing
- the build works in a local-first mode suitable for demos and controlled testing

### Phase 2: Verification, Policy, and Claim Routing

Goal:
Make ESCO assert only when evidence and policy allow it.

Deliverables:

- claim extraction pipeline
- intent clarifier
- verifier path for evidence checking
- support profile model
- clarification mode
- exploration mode
- consequences mode for false-claim tracing
- policy rules such as:
  - no claim without evidence
  - structured abstention on insufficient evidence
  - higher confidence only with corroboration
- baseline contradiction and coherence checks

Exit criteria:

- a plain user prompt can be routed into the correct ESCO mode
- outputs visibly separate claim, evidence, caveat, and interpretation
- unsupported assertions are downgraded, abstained, or blocked by policy
- the system can explain why a claim was allowed, softened, or rejected

### Phase 3: Audit, Evaluation, Secure Retrieval, Memory, and Orchestration

Goal:
Harden the platform and make it reproducible before the domain pilots.

Deliverables:

- immutable audit log
- reasoning trace graph schema
- steward review queue
- evaluation harness using factuality and RAG metrics
- prompt-injection and jailbreak regression suite
- web-search adapter with allowlists and caching
- web content sanitizer
- model adapter interface
- dual-model verification flow
- prompt builder with grounded style lock
- opt-in memory consent flow
- context reconstruction service
- tone router
- emotional state classifier and distress handling policy

Exit criteria:

- the platform can be evaluated repeatedly against a stable benchmark suite
- web-enabled retrieval is policy-gated and sanitized
- prompt injection is treated as content, not instructions
- memory is consent-aware
- tone selection does not weaken truth constraints
- large-model output is always mediated through ESCO rules

### Phase 4: SocraBot Pilot

Goal:
Launch the first specialized domain bot using the shared ESCO platform.

Deliverables:

- dialectic session model
- live fallacy detection
- fallacy accumulation scoring
- educational intervention flow
- dialogue reset phase
- steelman protocol
- moderator or dual-user conversation mode

Exit criteria:

- SocraBot can guide a debate without collapsing into passive summarization
- derailment can be measured, surfaced, and corrected

### Phase 5: BillBot Pilot

Goal:
Prove the analysis-system branch on a document-heavy, high-value use case.

Deliverables:

- bill and policy ingestion
- document OCR pipeline
- hidden clause detection
- entity and section graph extraction
- title-to-content coherence checks
- rider and contradiction surfacing
- transparent report output with support profile

Exit criteria:

- a long bill can be ingested, sectioned, analyzed, and summarized with traceable findings

### Phase 6: Expansion Wave

Goal:
Extend the stable ESCO platform into research and archive intelligence without rewriting the core.

Candidate modules:

- MedBot
- ArchiveBot / DeepFile
- Legal Loophole Bot
- Light Web integration services

Exit criteria:

- new domain modules reuse the same routing, ethics, memory, and audit contracts

## Recommended Build Order

If execution starts now, build in this order:

1. Phase 0
2. Phase 1
3. Phase 2
4. Phase 3
5. Phase 4
6. Phase 5
7. Hold Phase 6 in backlog until the platform proves stable

## Delivery Workflow

Every phase ticket should follow the same operating rule:

1. Move the ticket to `In Progress` before implementation starts.
2. Keep the Linear ticket as the source of truth for scope, decisions, and blockers.
3. Open a matching GitHub issue if code or repo changes are required.
4. After a pull request is opened, move the Linear ticket to `In Review`.
5. After the PR is merged and verified, move the ticket to `Done`.

## Starting Plan To Read Back

Use this as the execution script for the first pass:

1. We will start with Phase 0 and lock the architecture boundaries before building features.
2. We will treat the ESCO kernel, policy and ethics layer, audit spine, memory consent system, model orchestration, retrieval layer, provenance schema, and evaluation harness as shared platform work that all bots depend on.
3. We will move the active Linear ticket to `In Progress` before writing code.
4. We will create or update the matching GitHub issue before implementation begins if repo work is involved.
5. We will move the Linear ticket to `In Review` as soon as a PR is opened.
6. We will not start SocraBot or BillBot until the local-first evidence foundation, policy rules, and evaluation baseline are working.
7. We will use SocraBot and BillBot as the first domain proofs that the shared ESCO architecture can support very different reasoning styles.
8. We will not begin MedBot, ArchiveBot, or Light Web implementation until the core platform and the pilot bots are stable.

## Immediate Next Recommendation

Start with four concrete implementation artifacts:

- an ADR for the private-core versus transparent-surface split
- an event and metadata schema for evidence, support profiles, ethics decisions, and audit entries
- a local model selection note with runtime constraints
- a corpus and retrieval contract for the first offline-only MVP
