# ESCO Phased Roadmap

Date: 2026-04-10

## Architecture Confidence

Yes, I feel confident developing an architecture here.

The repository does not yet contain implementation code, but it does contain enough signal to define:

- the core ESCO platform boundaries
- the sequencing between platform work and domain bots
- the audit, ethics, memory, and orchestration spine
- the first execution phases that can become projects, tickets, and issues

What is still under-specified is not the high-level architecture. The main open questions are implementation choices inside the architecture:

- which UI stack should front the system
- whether the symbolic layer starts as a custom rules DSL or a Prolog-backed engine
- whether the audit graph stays in Postgres first or gets a dedicated graph projection later
- how much of the inner core remains private versus mirrored through transparent adapters
- which domain bot becomes the first production pilot after the core platform

## Recommended System Shape

The cleanest starting shape for ESCO is a modular platform with a private inner core and transparent outer surfaces.

### Core platform layers

1. Interaction Gateway
   - API, auth, session handling, user preference intake, file upload entrypoints
   - routes all user requests into the ESCO kernel

2. Claim Routing Kernel
   - claim extraction
   - intent clarification
   - support-profile routing
   - exploration-mode routing
   - clarification-mode routing
   - "what happens if this is false?" consequences mode

3. Ethics and Coherence Layer
   - symbolic rule engine
   - contradiction detector
   - coherence scoring
   - policy validation
   - steward escalation rules

4. Model Orchestration Layer
   - prompt builder
   - model adapter interface
   - dual-model verification
   - leak-review comparison flow

5. Memory and Context Layer
   - opt-in memory consent
   - context reconstruction
   - per-domain memory policies
   - document state storage

6. Tone and State Layer
   - user-selected tone target: blunt, balanced, gentle
   - emotional state classifier
   - distress and escalation detection
   - tone router that cannot override truth constraints

7. Transparency and Audit Spine
   - immutable decision log
   - reasoning trace graph
   - human steward review queue
   - explainable output surface

8. Domain Modules
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
- Object storage or filesystem-backed document store for uploads and OCR inputs
- Vector search only when retrieval quality becomes a real bottleneck
- Graph projection later for reasoning traces and entity relationships if Postgres tables become too limiting

### Suggested service split

- `esco-gateway`
- `esco-kernel`
- `esco-ethics`
- `esco-audit`
- `esco-memory`
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
- event schema for claims, ethics decisions, audit entries, and steward review
- closed-core versus open-surface policy
- security and misuse threat model for the platform

Exit criteria:

- every future feature can be placed into a named module
- audit events and review triggers have a stable schema
- the team can explain which parts are private, public, or user-visible

### Phase 1: Core Interaction Kernel

Goal:
Stand up the MVP ESCO reasoning path without domain specialization.

Deliverables:

- claim extraction pipeline
- intent clarifier
- support profile model
- clarification mode
- exploration mode
- consequences mode for false-claim tracing
- response envelope that separates evidence, inference, uncertainty, and tone

Exit criteria:

- a plain user prompt can be routed into the correct ESCO mode
- outputs visibly separate claim, evidence, caveat, and interpretation

### Phase 2: Ethics, Coherence, and Audit Spine

Goal:
Make ESCO inspectable and gateable before adding more capability.

Deliverables:

- symbolic rule engine baseline
- contradiction detector
- coherence scoring
- immutable audit log
- reasoning trace graph schema
- steward review queue
- double-leak escalation policy

Exit criteria:

- every response can produce a reason trail
- rule violations can stop or reshape a response
- steward review can be triggered automatically

### Phase 3: Model Orchestration, Memory, and Tone

Goal:
Add the layers that make ESCO feel like ESCO rather than a generic wrapper.

Deliverables:

- model adapter interface
- dual-model verification flow
- prompt builder with grounded style lock
- opt-in memory consent flow
- context reconstruction service
- tone router
- emotional state classifier and distress handling policy

Exit criteria:

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
2. We will treat the ESCO kernel, ethics layer, audit spine, memory consent system, and model orchestration as platform work that all bots depend on.
3. We will move the active Linear ticket to `In Progress` before writing code.
4. We will create or update the matching GitHub issue before implementation begins if repo work is involved.
5. We will move the Linear ticket to `In Review` as soon as a PR is opened.
6. We will not begin MedBot, ArchiveBot, or Light Web implementation until the core platform and at least one pilot bot are stable.
7. We will use SocraBot and BillBot as the first proof that the shared ESCO architecture can support very different reasoning domains.

## Immediate Next Recommendation

Start with three concrete architecture artifacts:

- an ADR for the private-core versus transparent-surface split
- an event schema for support profiles, ethics decisions, and audit entries
- an interface contract for the claim routing kernel
