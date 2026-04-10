"""Offline-first retrieval service implementation seams."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from typing import Iterable
from urllib.parse import urlparse
from uuid import uuid4

from esco_contracts.constants import PROMPT_INJECTION_PATTERNS
from esco_contracts.models import (
    ActorRef,
    EventEnvelope,
    EvidenceRecord,
    ProvenanceMetadata,
    QualityFlags,
    SourceRef,
    SubjectRef,
)

from .interfaces import (
    Chunker,
    DocumentRepository,
    EmbeddingProvider,
    IngestionArtifact,
    IngestionResult,
    RetrievalQuery,
    RetrievalResult,
    VectorRecord,
    VectorStore,
)


@dataclass(slots=True)
class RetrievalService:
    repository: DocumentRepository
    embedder: EmbeddingProvider
    vector_store: VectorStore
    chunker: Chunker
    service_actor_id: str = "esco-retrieval"

    def ingest_document(self, artifact: IngestionArtifact) -> IngestionResult:
        self._validate_ingestion_artifact(artifact)
        content_sha256 = sha256(artifact.raw_text.encode("utf-8")).hexdigest()
        doc_id = self.repository.create_document(artifact, content_sha256)
        provenance = ProvenanceMetadata(
            canonical_url=artifact.canonical_url,
            source_domain=artifact.source_domain or urlparse(artifact.canonical_url).netloc,
            content_sha256=content_sha256,
            retrieved_at=artifact.retrieved_at,
            publication_date=artifact.publication_date,
            source_type=artifact.source_type,
            license_ref=artifact.license_ref,
            raw_artifact_uri=artifact.artifact_uri,
        )
        quality_flags = QualityFlags(
            primary_source=not artifact.user_supplied,
            contains_opinion=artifact.source_type in {"commentary", "user_supplied"},
            official_docs=artifact.source_type == "official_docs",
            contains_prompt_injection_patterns=self._contains_prompt_injection(artifact.raw_text),
        )
        chunks = self.chunker.chunk(
            doc_id=doc_id,
            text=artifact.raw_text,
            publisher=artifact.publisher,
            provenance=provenance,
            quality_flags=quality_flags,
        )
        embeddings = self.embedder.embed([chunk.text for chunk in chunks])
        self.vector_store.upsert(
            [
                VectorRecord(
                    chunk_id=chunk.chunk_id,
                    embedding=embedding,
                    source_type=provenance.source_type,
                    source_domain=provenance.source_domain,
                )
                for chunk, embedding in zip(chunks, embeddings, strict=True)
            ]
        )
        for chunk in chunks:
            self.repository.store_chunk(chunk)
        event = self._build_event(
            event_type="evidence.ingested",
            subject_type="evidence_record",
            subject_id=doc_id,
            session_id=doc_id,
            payload={
                "doc_id": doc_id,
                "chunk_count": len(chunks),
                "source_domain": provenance.source_domain,
            },
        )
        return IngestionResult(doc_id=doc_id, chunk_ids=tuple(chunk.chunk_id for chunk in chunks), events=(event,))

    def retrieve_evidence(self, query: RetrievalQuery) -> tuple[EvidenceRecord, ...]:
        if not query.claim_text.strip():
            return tuple()
        embedding = self.embedder.embed([query.claim_text])[0]
        hits = self.vector_store.query(
            embedding=embedding,
            limit=query.limit,
            source_types=query.source_types,
            source_domains=query.source_domains,
        )
        records: list[EvidenceRecord] = []
        for hit in hits:
            chunk = self.repository.get_chunk(hit.chunk_id)
            records.append(
                EvidenceRecord(
                    evidence_id=chunk.chunk_id,
                    doc_id=chunk.doc_id,
                    chunk_id=chunk.chunk_id,
                    excerpt=chunk.text,
                    publisher=chunk.publisher,
                    provenance=chunk.provenance,
                    quality_flags=chunk.quality_flags,
                )
            )
        return tuple(records)

    def retrieve_with_audit(self, query: RetrievalQuery) -> RetrievalResult:
        records = self.retrieve_evidence(query)
        event = self._build_event(
            event_type="evidence.retrieved",
            subject_type="evidence_record",
            subject_id=records[0].evidence_id if records else "empty",
            session_id=str(uuid4()),
            payload={
                "claim_text": query.claim_text,
                "result_count": len(records),
            },
        )
        return RetrievalResult(evidence_ids=tuple(record.evidence_id for record in records), events=(event,))

    def resolve_provenance(self, evidence_ids: Iterable[str]) -> dict[str, ProvenanceMetadata]:
        return {evidence_id: self.repository.get_provenance(evidence_id) for evidence_id in evidence_ids}

    def _validate_ingestion_artifact(self, artifact: IngestionArtifact) -> None:
        required_fields = {
            "raw_text": artifact.raw_text,
            "canonical_url": artifact.canonical_url,
            "publisher": artifact.publisher,
            "source_type": artifact.source_type,
            "license_ref": artifact.license_ref,
            "artifact_uri": artifact.artifact_uri,
        }
        missing = [name for name, value in required_fields.items() if not value or not value.strip()]
        if missing:
            raise ValueError(f"Missing required provenance fields: {', '.join(missing)}")

    def _contains_prompt_injection(self, text: str) -> bool:
        lowered = text.lower()
        return any(pattern in lowered for pattern in PROMPT_INJECTION_PATTERNS)

    def _build_event(
        self,
        *,
        event_type: str,
        subject_type: str,
        subject_id: str,
        session_id: str,
        payload: object,
    ) -> EventEnvelope:
        now = datetime.now(timezone.utc)
        return EventEnvelope(
            schema_version="1.0.0",
            event_id=str(uuid4()),
            event_type=event_type,  # type: ignore[arg-type]
            occurred_at=now,
            trace_id=str(uuid4()),
            session_id=session_id,
            sequence=1,
            actor=ActorRef(actor_type="service", actor_id=self.service_actor_id, actor_domain="retrieval"),
            source=SourceRef(channel="retrieval", origin="RetrievalService"),
            subject=SubjectRef(entity_type=subject_type, entity_id=subject_id),  # type: ignore[arg-type]
            payload=payload,
        )
