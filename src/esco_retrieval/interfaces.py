"""Protocol interfaces for the Phase 1 corpus and retrieval layer."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Protocol, Sequence

from esco_contracts.models import EventEnvelope, ProvenanceMetadata, QualityFlags


@dataclass(frozen=True)
class IngestionArtifact:
    raw_text: str
    canonical_url: str
    publisher: str
    source_type: str
    license_ref: str
    retrieved_at: datetime
    artifact_uri: str
    publication_date: str | None = None
    source_domain: str | None = None
    user_supplied: bool = False


@dataclass(frozen=True)
class DocumentChunk:
    doc_id: str
    chunk_id: str
    text: str
    publisher: str
    provenance: ProvenanceMetadata
    quality_flags: QualityFlags


@dataclass(frozen=True)
class VectorRecord:
    chunk_id: str
    embedding: tuple[float, ...]
    source_type: str
    source_domain: str


@dataclass(frozen=True)
class SearchHit:
    chunk_id: str
    score: float


@dataclass(frozen=True)
class IngestionResult:
    doc_id: str
    chunk_ids: tuple[str, ...]
    events: tuple[EventEnvelope, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class RetrievalQuery:
    claim_text: str
    limit: int = 5
    source_types: tuple[str, ...] = field(default_factory=tuple)
    source_domains: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class RetrievalResult:
    evidence_ids: tuple[str, ...]
    events: tuple[EventEnvelope, ...] = field(default_factory=tuple)


class Chunker(Protocol):
    def chunk(self, *, doc_id: str, text: str, publisher: str, provenance: ProvenanceMetadata, quality_flags: QualityFlags) -> list[DocumentChunk]:
        """Split a document into retrievable chunks."""


class EmbeddingProvider(Protocol):
    def embed(self, texts: Sequence[str]) -> list[tuple[float, ...]]:
        """Produce embeddings for document chunks or claim queries."""


class DocumentRepository(Protocol):
    def create_document(self, artifact: IngestionArtifact, content_sha256: str) -> str:
        """Persist a raw document and return a stable doc id."""

    def store_chunk(self, chunk: DocumentChunk) -> None:
        """Persist a chunk and its provenance metadata."""

    def get_chunk(self, chunk_id: str) -> DocumentChunk:
        """Return a previously stored chunk."""

    def get_provenance(self, evidence_id: str) -> ProvenanceMetadata:
        """Resolve one evidence identifier to provenance metadata."""


class VectorStore(Protocol):
    def upsert(self, records: Sequence[VectorRecord]) -> None:
        """Store embeddings for later nearest-neighbor search."""

    def query(self, embedding: tuple[float, ...], limit: int, source_types: Sequence[str], source_domains: Sequence[str]) -> list[SearchHit]:
        """Return the nearest matching chunk ids."""
