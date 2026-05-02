# Memory And Audit Contract

Date: 2026-04-10
Status: Locked for Phase 0

## Memory Contract

Memory behavior is opt-in only.

Required rules:

- default state is no-write
- memory consent is domain-scoped or narrower
- no memory write occurs without an active consent record
- revoked or opt-out consent takes effect immediately
- memory behavior must be representable without invoking hidden model logic

Required states:

- `opt_in`
- `opt_out`
- `revoked`

Required scopes:

- `none`
- `session`
- `domain`
- `global`

Required events:

- `memory.consent_recorded`
- `memory.write_skipped`
- `memory.write_completed`

Default behavior:

- if no consent record exists, ESCO records a skip event and performs no memory write

## Audit Contract

Audit behavior must show what happened without exposing the private core.

Required rules:

- every policy decision is auditable
- every evidence selection step is auditable
- every abstention and escalation is auditable
- every memory write or skipped memory write is auditable
- every search block or search sanitization action is auditable once web search exists

Visibility levels:

- `public_summary`
- `internal_restricted`

Redaction levels:

- `none`
- `internal_only`
- `core_private`

Required categories:

- `policy_decision`
- `evidence_selection`
- `support_profile_generation`
- `abstention`
- `escalation`
- `memory_write`
- `memory_skip`
- `search_block`
- `search_sanitization`
- `user_visible_output`

## Cross-Contract Rule

Audit must never require disclosure of `core_private` logic to explain a result.

This means:

- private heuristics are summarized through named outcomes and policy references
- public summaries point to evidence and route labels
- internal restricted entries may contain richer operational context without revealing sacred core logic

## Acceptance Scenarios

- A session with memory disabled produces no persistent memory write and does produce a `memory.write_skipped` event.
- A blocked claim produces both an `EthicsDecision` and an `AuditEntry`.
- A user-visible response can be replayed to its supporting evidence and audit summary without exposing the core-private internals.
