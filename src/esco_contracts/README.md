# `esco_contracts`

This package is the shared vocabulary of ESCO.

If the rest of the system is the body, `esco_contracts` is the skeleton. It defines the shapes of the records that retrieval, verification, policy, audit, and runtime code will pass around.

## Why this package exists

Without a contracts layer, each subsystem tends to invent its own version of the same ideas:

- what a claim looks like
- what counts as evidence
- what an audit event stores
- how memory consent is represented

That leads to drift and confusion fast.

This package prevents that by giving the project one central place for shared record shapes.

## Files in this package

- `constants.py`
  - shared names and locked public values
  - includes the route names, model ids, Support Profile field names, and prompt-injection phrase patterns
- `models.py`
  - typed records and validation rules
  - most of the important system nouns live here
- `__init__.py`
  - re-exports the important symbols so other packages can import from `esco_contracts` directly

## The main records

Here is the practical meaning of each model:

- `ActorRef`
  - who or what performed an action
  - example: a user, a service, or a reviewer
- `SourceRef`
  - where an event came from
  - example: API, UI, retrieval flow
- `SubjectRef`
  - what object the event is about
  - example: a claim, support profile, or audit entry
- `EventEnvelope`
  - the outer wrapper for auditable system events
  - this is the append-only "event log" container
- `ProvenanceMetadata`
  - the evidence provenance block
  - URL, domain, content hash, retrieval time, license, and source type
- `QualityFlags`
  - quick boolean markers about evidence quality
  - example: official docs, peer reviewed, contains prompt injection patterns
- `Claim`
  - the normalized statement ESCO is evaluating
- `EvidenceRecord`
  - one retrievable piece of supporting or opposing evidence
- `SupportMetric`
  - one dimension inside the Support Profile
- `SupportProfile`
  - the inspectable evidence summary for a claim
- `EthicsDecision`
  - the result of the policy layer deciding what the system is allowed to do
- `AuditEntry`
  - a user-visible or internal summary of something important that happened
- `MemoryConsentRecord`
  - the rules for whether memory writes are allowed

## Why the models use `dataclass`

We are using Python `dataclass` objects because they are easy to read and easy to construct.

That gives us a nice balance:

- strong enough structure for typing and tests
- simple enough for learning and early iteration

You can think of them as "plain data objects with a little validation."

## What `__post_init__` is doing

Several models use `__post_init__`.

That method runs **right after** the dataclass is created. We use it for simple guardrails such as:

- making sure required strings are not empty
- making sure sequences or ids exist
- making sure a Support Profile includes all required metrics
- making sure memory writes are not enabled when consent says they should not be

This is small but important. It means bad data fails early instead of quietly moving deeper into the system.

## Public constants vs internal details

`constants.py` holds values we want to treat as stable project contracts.

Examples:

- `SUPPORT_PROFILE_ROUTE`
- `EXPLORATION_ROUTE`
- `CLARIFICATION_ROUTE`
- `SUPPORT_PROFILE_FIELDS`
- `DEFAULT_PRIMARY_MODEL_ID`
- `DEFAULT_FALLBACK_MODEL_ID`

These matter because later packages and tests should not each hardcode their own version of the same strings.

## How other packages use this

- `esco_retrieval` uses `ProvenanceMetadata`, `QualityFlags`, `EvidenceRecord`, and `EventEnvelope`
- `esco_runtime` uses the model id constants
- tests import these records to assert that our public contracts stay locked

## Good next places to read

- `src/esco_retrieval/README.md`
- `src/esco_runtime/README.md`
- `resources/schemas/`

The docs in `resources/schemas/` show the documentation-first source that these Python models mirror.
