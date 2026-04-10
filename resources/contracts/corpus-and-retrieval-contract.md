# Corpus And Retrieval Contract

Date: 2026-04-10
Status: Locked for Phase 0

## Purpose

This contract defines the offline-first evidence foundation for the ESCO MVP.

Phase 1 must implement these operations before any domain bot work begins.

## System Defaults

- Postgres is the system of record for relational state.
- Raw corpus artifacts live in a filesystem-backed or object-backed document store.
- Qdrant is the first vector store.
- Web search is not part of the MVP until Phase 3.
- Retrieval must work against curated local and user-supplied documents only.

## Required Operations

### 1. `ingest_document`

Purpose:
Store a raw document, normalize it, chunk it, attach provenance metadata, and make it retrievable.

Required input:

- raw artifact path or blob reference
- declared source type
- canonical URL when one exists
- publisher or issuing body when known
- license or terms reference
- retrieval timestamp

Required output:

- `doc_id`
- chunk records
- embeddings ready for indexing
- provenance metadata for every chunk
- at least one `evidence.ingested` event

Non-negotiable behavior:

- ingestion fails closed when canonical provenance fields are missing
- content hashing is mandatory
- every chunk must be traceable to a raw source artifact
- user-supplied content must be labeled as such

### 2. `retrieve_evidence`

Purpose:
Return evidence candidates for a user claim without hiding provenance.

Required input:

- extracted claim text
- optional route context
- optional source filters
- optional domain scope

Required output:

- ordered `EvidenceRecord` results
- retrieval metadata including doc and chunk ids
- at least one `evidence.retrieved` event

Non-negotiable behavior:

- retrieval responses must include provenance, not just text excerpts
- retrieval must support metadata filtering
- retrieval may not silently blend incompatible source types into one unsupported claim
- if no adequate evidence is found, the caller must receive an empty evidence set rather than fabricated support

### 3. `resolve_provenance`

Purpose:
Expand one or more evidence references into inspectable provenance summaries for audit and user-visible output.

Required input:

- one or more `evidence_id` values

Required output:

- canonical URL
- publisher
- source domain
- license reference
- retrieval timestamp
- publication date when known
- raw artifact reference

Non-negotiable behavior:

- provenance resolution must work without the language model
- provenance resolution must be stable across replays of the same stored evidence

## Required Metadata Fields

Every retrievable chunk must preserve:

- `doc_id`
- `chunk_id`
- `content_sha256`
- `canonical_url`
- `source_domain`
- `publisher`
- `retrieved_at`
- `publication_date` when known
- `source_type`
- `license_ref`
- quality flags, including whether the chunk is opinion-bearing or contains prompt-injection patterns

## Retrieval Output Rules

- Retrieval returns evidence records, not final truth judgments.
- Support comes from the verifier and policy layers after retrieval, not from vector similarity alone.
- Conflicting records may be returned together if they are materially relevant.
- The system must preserve counterevidence instead of hiding it for narrative neatness.

## Failure Modes

- Missing provenance: reject ingestion.
- Empty retrieval set: return no evidence and let the verifier route toward abstention or clarification.
- Corrupt raw artifact: record an ingest failure event and keep the document out of the index.
- Suspicious content patterns: keep the record available for audit, but mark the relevant quality flag for downstream sanitization.

## Acceptance Scenarios

- A grounded claim can retrieve local evidence with full provenance.
- A conflicting claim can retrieve both supporting and opposing evidence.
- A user-supplied document can be retrieved, but is always labeled as user-supplied.
- A document missing provenance fields cannot enter the trusted retrievable set.
