"""Testing helpers and in-memory implementations for the retrieval layer."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from math import sqrt
from typing import Sequence
from uuid import uuid4

from esco_contracts.models import ProvenanceMetadata, QualityFlags

from .interfaces import Chunker, DocumentChunk, DocumentRepository, IngestionArtifact, SearchHit, VectorRecord, VectorStore


class SimpleParagraphChunker:
    """Split text on blank lines and fall back to line-based chunking."""

    def chunk(self, *, doc_id: str, text: str, publisher: str, provenance: ProvenanceMetadata, quality_flags: QualityFlags) -> list[DocumentChunk]:
        raw_segments = [segment.strip() for segment in text.split("\n\n") if segment.strip()]
        segments = raw_segments or [line.strip() for line in text.splitlines() if line.strip()]
        chunks: list[DocumentChunk] = []
        for segment in segments:
            chunks.append(
                DocumentChunk(
                    doc_id=doc_id,
                    chunk_id=str(uuid4()),
                    text=segment,
                    publisher=publisher,
                    provenance=provenance,
                    quality_flags=quality_flags,
                )
            )
        return chunks


class DeterministicEmbedder:
    """Cheap deterministic embeddings so the retrieval seam can be tested without a model."""

    _dimension = 8

    def embed(self, texts: Sequence[str]) -> list[tuple[float, ...]]:
        return [self._embed_text(text) for text in texts]

    def _embed_text(self, text: str) -> tuple[float, ...]:
        buckets = [0.0] * self._dimension
        for token in text.lower().split():
            bucket = int(sha256(token.encode("utf-8")).hexdigest(), 16) % self._dimension
            buckets[bucket] += 1.0
        norm = sqrt(sum(value * value for value in buckets)) or 1.0
        return tuple(value / norm for value in buckets)


@dataclass
class _StoredDocument:
    artifact: IngestionArtifact
    content_sha256: str
    doc_id: str


class InMemoryDocumentRepository:
    def __init__(self) -> None:
        self._documents: dict[str, _StoredDocument] = {}
        self._chunks: dict[str, DocumentChunk] = {}

    def create_document(self, artifact: IngestionArtifact, content_sha256: str) -> str:
        doc_id = str(uuid4())
        self._documents[doc_id] = _StoredDocument(artifact=artifact, content_sha256=content_sha256, doc_id=doc_id)
        return doc_id

    def store_chunk(self, chunk: DocumentChunk) -> None:
        self._chunks[chunk.chunk_id] = chunk

    def get_chunk(self, chunk_id: str) -> DocumentChunk:
        return self._chunks[chunk_id]

    def get_provenance(self, evidence_id: str) -> ProvenanceMetadata:
        return self._chunks[evidence_id].provenance


class InMemoryVectorStore:
    def __init__(self) -> None:
        self._records: dict[str, VectorRecord] = {}

    def upsert(self, records: Sequence[VectorRecord]) -> None:
        for record in records:
            self._records[record.chunk_id] = record

    def query(self, embedding: tuple[float, ...], limit: int, source_types: Sequence[str], source_domains: Sequence[str]) -> list[SearchHit]:
        hits: list[SearchHit] = []
        type_filter = set(source_types)
        domain_filter = set(source_domains)
        for chunk_id, record in self._records.items():
            if type_filter and record.source_type not in type_filter:
                continue
            if domain_filter and record.source_domain not in domain_filter:
                continue
            score = self._cosine_similarity(embedding, record.embedding)
            hits.append(SearchHit(chunk_id=chunk_id, score=score))
        hits.sort(key=lambda hit: hit.score, reverse=True)
        return hits[:limit]

    def _cosine_similarity(self, left: tuple[float, ...], right: tuple[float, ...]) -> float:
        return sum(a * b for a, b in zip(left, right, strict=True))
