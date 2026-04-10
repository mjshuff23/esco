# ESCO Phase 0 Contracts

This directory locks the behavior that later implementation tickets must inherit.

Files:

- `local-model-selection.md`
- `corpus-and-retrieval-contract.md`
- `verification-and-policy-contract.md`
- `memory-and-audit-contract.md`

Contract rules:

- later phases may add fields, but they may not silently redefine the meaning of an existing field or route
- no contract may assume cloud inference or web search before Phase 3
- public output behavior must stay aligned with the visibility bands in `resources/adrs/0001-private-core-vs-transparent-surface.md`
