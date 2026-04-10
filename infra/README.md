# Local Infrastructure

Phase 1 uses two local services:

- Postgres as the system of record
- Qdrant as the first vector store

Start them with:

```bash
docker compose -f infra/compose.yaml up -d
```

Default local ports:

- Postgres: `5432`
- Qdrant HTTP: `6333`
- Qdrant gRPC: `6334`

This setup intentionally keeps web search out of the stack until Phase 3.
