# `esco_retrieval`

This package is the beginning of ESCO's offline-first evidence system.

Right now it is intentionally modest. We are not talking to a real database or vector engine yet. Instead, we are proving the shape of the retrieval layer so we can later swap in real infrastructure without changing how the rest of the system thinks about retrieval.

## The job of this package

This package is responsible for three big actions:

1. ingesting a document
2. retrieving evidence for a claim
3. resolving provenance for evidence we already found

That maps directly to the Phase 0 retrieval contract.

## Files in this package

- `interfaces.py`
  - the typed inputs, outputs, and interface contracts for retrieval
  - this is where we define what the retrieval layer expects from chunkers, embedders, repositories, and vector stores
- `service.py`
  - the first orchestration layer for retrieval behavior
  - this is the main "do the work" class for Phase 1
- `testing.py`
  - in-memory test doubles and lightweight helper implementations
  - useful for fast feedback before real infrastructure exists
- `__init__.py`
  - re-exports the main retrieval symbols

## How to read the code

If you are newer to the current Python style, read it in this order:

1. `interfaces.py`
2. `testing.py`
3. `service.py`

That order works well because:

- `interfaces.py` tells you the nouns and seams
- `testing.py` gives simple concrete implementations
- `service.py` ties them together

## `interfaces.py`: the seam layer

This file has two kinds of things:

1. `dataclass` records like:
   - `IngestionArtifact`
   - `DocumentChunk`
   - `RetrievalQuery`
   - `RetrievalResult`
2. `Protocol` interfaces like:
   - `Chunker`
   - `EmbeddingProvider`
   - `DocumentRepository`
   - `VectorStore`

The key idea is that `RetrievalService` does not care *which* database or embedder you use. It only cares that the object you give it has the right methods.

That is why `Protocol` is powerful here. It lets us write code against capabilities instead of hardcoded classes.

## `service.py`: the orchestration layer

`RetrievalService` is the central class in this package.

Its methods currently do this:

- `ingest_document`
  - validate required provenance fields
  - hash the raw text
  - create a document record
  - build provenance metadata
  - set quality flags
  - chunk the document
  - embed the chunks
  - store vectors
  - persist chunks
  - emit an ingestion event
- `retrieve_evidence`
  - embed the claim text
  - query the vector store
  - hydrate hits back into `EvidenceRecord` objects
- `retrieve_with_audit`
  - wrap retrieval with a retrieval event
- `resolve_provenance`
  - map evidence ids back to their provenance metadata

This is the first "real" service in the repo, even though some of the backing parts are still test implementations.

## `testing.py`: the learning-friendly sandbox

This file gives us simple concrete versions of the retrieval interfaces:

- `SimpleParagraphChunker`
  - splits documents into chunks using blank lines first
- `DeterministicEmbedder`
  - creates tiny fake embeddings in a repeatable way
  - not smart, but perfect for tests
- `InMemoryDocumentRepository`
  - stores docs and chunks in Python dictionaries
- `InMemoryVectorStore`
  - stores vectors in memory and performs a cosine-similarity lookup

These are extremely useful while learning because they let us test the retrieval flow without Docker, Postgres, Qdrant, or a local LLM.

## Why we flag prompt injection here

The retrieval layer marks suspicious content as data, not instructions.

That is why the service looks for patterns like:

- "ignore previous instructions"
- "system prompt"
- "tool call"

We are not trying to solve prompt injection fully here yet. We are just making sure the retrieval layer preserves the fact that suspicious content exists so later layers can react safely.

## What is missing on purpose

This package does **not** yet include:

- a real Postgres-backed repository
- a real Qdrant-backed vector store
- a production embedding model
- document parsing for PDFs, HTML, or markdown files
- chunk ranking logic beyond the minimal current behavior

That is intentional. We are building the seam first.

## Mental model

If you want one sentence to remember:

`esco_retrieval` turns raw documents into traceable evidence and gives the rest of ESCO a clean way to ask for it.
