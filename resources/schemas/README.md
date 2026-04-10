# ESCO Phase 0 Schemas

This directory is the canonical Phase 0 schema package.

Files:

- `event-envelope.schema.json`
- `domain-records.schema.json`

Design rules:

- schema files are documentation-first and implementation-neutral
- later code should generate or validate against these contracts rather than silently changing them
- new schema versions must preserve backward-readable audit records
