# `esco_policy`

This package is the first policy gate for Phase 2.

Its job is to decide what ESCO is allowed to do after the verifier has routed a claim and, when relevant, built a Support Profile.

## What it does right now

The current policy layer is still a first slice. It does not implement a full OPA or Rego integration yet.

Instead, it gives us a clear local decision point for:

- `allow`
- `soften`
- `abstain`
- `block`
- `escalate`

That makes the Phase 2 contract executable before we bring in a dedicated policy engine.

## Files

- `models.py`
  - the `PolicyContext` object passed into the policy layer
- `service.py`
  - the current rule-based decision logic
- `__init__.py`
  - package re-exports

## How the current policy behaves

Examples:

- no assertive claim
  - allow conversational handling
- Exploration route
  - allow, because ESCO is not pretending to verify a personal interpretation
- Clarification route
  - soften, because the system should ask for more detail instead of scoring too early
- Support Profile route with no evidence
  - abstain, or block when the claim is high impact
- Support Profile route with conflicting evidence
  - soften, or escalate when the claim is high impact
- Support Profile route with supported evidence
  - allow

## Why this package matters

This is the first place where ESCO starts behaving like:

"The model may suggest, but the system only asserts when the evidence and policy allow it."

That is a core design principle of the whole project.
