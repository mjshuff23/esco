"""Builders for the offline interactive orchestration lane."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import re

from esco_policy import PolicyService
from esco_retrieval import IngestionArtifact, RetrievalService
from esco_retrieval.testing import (
    DeterministicEmbedder,
    InMemoryDocumentRepository,
    InMemoryVectorStore,
    SimpleParagraphChunker,
)
from esco_runtime import GroundedDraftAdapter, build_grounded_demo_config
from esco_verifier import VerificationService

from .service import OrchestratorService


@dataclass(frozen=True)
class RepoSeedDocument:
    relative_path: str
    publisher: str = "ESCO Repository"
    source_type: str = "official_docs"
    license_ref: str = "Repository local documentation"


DEFAULT_REPO_SEEDS = (
    RepoSeedDocument("README.md"),
    RepoSeedDocument("resources/contracts/corpus-and-retrieval-contract.md"),
    RepoSeedDocument("resources/contracts/verification-and-policy-contract.md"),
    RepoSeedDocument("resources/contracts/local-model-selection.md"),
    RepoSeedDocument("resources/adrs/0001-private-core-vs-transparent-surface.md"),
)


def build_demo_orchestrator(repo_root: Path | None = None) -> OrchestratorService:
    """Create a local-only orchestrator backed by in-memory services and repo docs."""
    root = repo_root or Path(__file__).resolve().parents[2]
    retrieval = RetrievalService(
        repository=InMemoryDocumentRepository(),
        embedder=DeterministicEmbedder(),
        vector_store=InMemoryVectorStore(),
        chunker=SimpleParagraphChunker(),
    )
    service = OrchestratorService(
        retrieval=retrieval,
        verifier=VerificationService(),
        policy=PolicyService(),
        runtime=GroundedDraftAdapter(config=build_grounded_demo_config()),
    )
    _seed_repo_corpus(service.retrieval, root)
    return service


def _seed_repo_corpus(retrieval: RetrievalService, repo_root: Path) -> None:
    now = datetime.now(timezone.utc)
    for seed in DEFAULT_REPO_SEEDS:
        path = repo_root / seed.relative_path
        raw_text = _read_seed_text(path)
        publication_date = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).date().isoformat()
        retrieval.ingest_document(
            IngestionArtifact(
                raw_text=raw_text,
                canonical_url=path.resolve().as_uri(),
                publisher=seed.publisher,
                source_type=seed.source_type,
                license_ref=seed.license_ref,
                retrieved_at=now,
                publication_date=publication_date,
                artifact_uri=path.resolve().as_uri(),
                source_domain="local.repo",
            )
        )


def _read_seed_text(path: Path) -> str:
    """Read repo documentation while stripping fenced code blocks from demo seeds.

    The seeded corpus is meant to exercise the knowledge-bearing prose in the
    repo. Removing fenced code blocks avoids the CLI example commands
    overshadowing actual roadmap and contract content during retrieval.
    """
    raw_text = path.read_text(encoding="utf-8")
    return re.sub(r"```.*?```", "", raw_text, flags=re.DOTALL)
