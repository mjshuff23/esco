# Local Model Selection Note

Date: 2026-04-10
Status: Locked for Phase 0

## Decision

ESCO will start with this local model baseline:

- Primary: `Ministral 8B Instruct`
- Fallback: `Gemma 4 E4B`

No cloud inference is allowed as a fallback for the initial build.

## Why This Is The Default

The current repo context favors:

- permissive licensing
- local-first execution
- strong enough reasoning for evidence-grounded responses
- a size profile that still leaves room for retrieval, tracing, and policy checks on a personal machine

`Ministral 8B Instruct` is the default because it best matches the first offline MVP goal: strong local quality without jumping directly to a heavier medium model. `Gemma 4 E4B` is the fallback because it preserves the same permissive posture while reducing local pressure.

## Candidate Comparison

| Model | Role | Why it was considered | Why it is or is not the default |
| --- | --- | --- | --- |
| `Ministral 8B Instruct` | Primary | Best balance of local quality, manageable footprint, and permissive license posture for the first evidence-grounded MVP. | Chosen as the default. |
| `Gemma 4 E4B` | Fallback | Smaller local footprint with permissive license posture and good fit for grounded, structured outputs. | Chosen as the fallback when the primary model is too heavy. |
| `Phi-4-mini-instruct` | Deferred alternative | Interesting reasoning density and permissive posture. | Not selected for Phase 0 to keep the baseline simple and avoid widening the first validation matrix. |

## Runtime Defaults

- Monorepo first.
- Python `3.10` is the application baseline.
- PyTorch is the baseline runtime library for ESCO-owned neural components.
- The model adapter may call a local inference runner, but the surrounding ESCO services remain Python-first.
- Only one primary inference model is active in the offline MVP.
- Retrieval, policy, and audit must remain available even if the model lane is swapped from primary to fallback.

## Hardware Validation Rule

Use the primary model unless it fails either of these checks on the target machine:

1. It cannot produce an interactive grounded answer without starving retrieval and audit services.
2. It cannot run locally without introducing cloud dependence or disabling required Phase 1 components.

If either check fails, switch to the fallback model and keep the same public contracts.

## What Later Tickets May Change

Later tickets may:

- add a secondary verifier model in Phase 3
- benchmark other permissive local models
- change the underlying inference runner

Later tickets may not:

- introduce cloud inference as the first answer path for the MVP
- replace the model without updating this note and preserving the same response contracts
