# `esco_verifier`

This package is the first implementation slice of Phase 2.

Its job is to answer a simple but important question:

"Given a user prompt, what kind of claim are we looking at, and what should ESCO do next?"

## What this package does right now

The current verifier is intentionally heuristic and lightweight. It is not pretending to be the final intelligent verifier.

It currently handles four jobs:

1. extract likely claims from a prompt
2. route the primary claim into `Support Profile`, `Exploration`, or `Clarification`
3. build a first-pass `SupportProfile` from retrieved evidence
4. generate a consequences-mode summary for `What happens if this is false?`

## Files

- `models.py`
  - result objects for routing, verification, and consequences analysis
- `service.py`
  - the actual Phase 2 verification logic
- `__init__.py`
  - package re-exports

## How to read the service

If you open `service.py`, these are the methods to read in order:

1. `evaluate_prompt`
2. `extract_claims`
3. `route_claims`
4. `build_support_profile`
5. `analyze_consequences`

That order mirrors the flow we want the system to take.

## Important limitation

This verifier is still a foundation layer.

It uses clear heuristics so that:

- the routing contract becomes executable
- the behavior is easy to test
- the next iteration can replace heuristics with stronger logic without changing the public interfaces

So if a route feels simple right now, that is by design.
