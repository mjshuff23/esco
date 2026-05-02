# `esco_orchestrator`

This package is the first end-to-end glue layer for ESCO.

Its job is to take the pieces that already exist in the repo and run them in a
single local-first flow:

1. extract and route the user prompt
2. retrieve local evidence when the route supports it
3. build a Support Profile when appropriate
4. apply the policy gate
5. record append-only audit summaries when an audit service is configured
6. produce a grounded draft response through a local adapter

## What this package is for right now

This is not the final product orchestrator yet.

The current slice is intentionally small:

- local-only
- in-memory retrieval stack
- repo-doc seed corpus for demos
- no web search
- no memory writes
- optional in-memory audit wiring for the local demo path

That makes it a good Phase 2 to Phase 3 bridge. We can now exercise the full
flow from prompt to grounded answer with inspectable audit entries, without
pretending the heavier platform work already exists.

## Main files

- `service.py`
  - the orchestration flow
- `models.py`
  - the structured result returned to callers
- `builder.py`
  - the local demo builder that seeds a tiny corpus from repo documents

## Demo path

The easiest current entrypoint is the CLI module:

```bash
PYTHONPATH=src python -m esco_cli "Phase 2 is implemented in the repo."
```

That path seeds a local corpus from repository docs and runs the prompt through
retrieval, verification, policy, audit recording, and a deterministic grounded
adapter.

Later work can swap the deterministic adapter for a real local model runner
without changing the orchestrator shape.
