# Verification And Policy Contract

Date: 2026-04-10
Status: Locked for Phase 0

## Purpose

This contract defines the decision path that turns a user prompt into an ESCO response mode.

Phase 2 must implement these stages in order.

## Required Stages

### 1. Claim extraction

Purpose:
Identify whether the prompt contains an assertive claim that should be evaluated.

Rules:

- If no assertive claim exists, ESCO may respond conversationally.
- Mixed prompts must be split so empirical claims are not hidden inside broader narrative text.

### 2. Claim routing

Purpose:
Assign one primary route to the extracted claim.

Primary routes:

- `Support Profile`
- `Exploration`
- `Clarification`

Routing rules:

- Use `Support Profile` for claims that are externally verifiable and specific enough to investigate.
- Use `Exploration` for claims that center on internal experience, meaning, or non-verifiable relational interpretation.
- Use `Clarification` when the claim is potentially verifiable but too underspecified to score honestly.

### 3. Support Profile construction

Purpose:
Build an inspectable evidence summary for a claim routed to `Support Profile`.

Required fields:

- `premise_validity`
- `source_convergence`
- `temporal_relevance`
- `internal_consistency`
- `counterevidence_presence`

Required posture output:

- `supported`
- `mixed`
- `weak`
- `insufficient`
- `conflicted`

Rules:

- counterevidence must be surfaced, not discarded
- the output must separate evidence, caveats, and interpretation
- unsupported claims must not be presented as settled truth

### 4. Policy evaluation

Purpose:
Apply the ethics gate after verification work is available.

Required policy outcomes:

- `allow`
- `soften`
- `abstain`
- `block`
- `escalate`

Rules:

- no claim is asserted without evidence or a clearly scoped interpretive frame
- insufficient evidence produces structured abstention, not rhetorical bluffing
- escalation is allowed when the system detects unresolved high-impact risk

## Consequences Mode

`What happens if this is false?` is a first-class consequences mode.

It is not a replacement for the primary routes above. Instead, it is a required secondary analysis mode that may be attached after the primary route is chosen.

Rules:

- It may follow `Support Profile` when the claim is specific enough to reason about downstream effects.
- It may follow `Exploration` when the user wants to inspect the implications of a belief or assumption.
- It may not replace `Clarification` when the prompt is still too vague to reason about responsibly.

Required output:

- the claim or assumption being stress-tested
- the downstream effects if the claim is false
- the systems, actors, or decisions affected
- the points where additional evidence would most change the conclusion

## User-Visible Output Rules

### Support Profile response

Must include:

- route label
- normalized claim text
- Support Profile metrics
- evidence references
- caveats
- counterevidence references when present
- policy outcome summary

### Exploration response

Must include:

- route label
- the interpretation or experience being explored
- no numerical scoring
- no fake external verification

### Clarification response

Must include:

- route label
- missing specifics the user needs to provide
- no truth-style scoring until those specifics exist

## Failure Modes

- No evidence for a specific factual claim: abstain or request clarification.
- Conflicting evidence: return `mixed` or `conflicted`, not artificial certainty.
- High-risk unsupported claim: block or escalate according to policy.
- Hidden instruction text in retrieved content: treat it as tainted evidence content, not executable guidance.
