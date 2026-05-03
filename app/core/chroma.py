import asyncio
import hashlib
import logging
import math
import re

import chromadb

from app.core.config import Settings


logger = logging.getLogger(__name__)


class ChromaManager:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client = (
            chromadb.HttpClient(
                host=settings.chroma_host,
                port=settings.chroma_port,
                ssl=settings.chroma_ssl,
            )
            if settings.use_chroma_http
            else chromadb.PersistentClient(path=settings.chroma_persist_directory)
        )

    async def upsert_analysis(
        self,
        *,
        analysis_id: str,
        document: str,
        metadata: dict[str, str | int | float],
    ) -> None:
        def _upsert() -> None:
            collection = self._client.get_or_create_collection(
                name=self._settings.chroma_collection_name,
                metadata={"hnsw:space": "cosine"},
            )
            collection.upsert(
                ids=[analysis_id],
                documents=[document],
                metadatas=[metadata],
                embeddings=[self._simple_embedding(document)],
            )

        try:
            await asyncio.to_thread(_upsert)
        except Exception as exc:  # pragma: no cover - network dependency
            logger.warning("Chroma upsert skipped: %s", exc)

    @staticmethod
    def _simple_embedding(text: str, dimensions: int = 64) -> list[float]:
        buckets = [0.0] * dimensions
        tokens = re.findall(r"[a-z0-9']+", text.lower())
        if not tokens:
            return buckets

        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
            bucket = int(digest[:8], 16) % dimensions
            buckets[bucket] += 1.0

        norm = math.sqrt(sum(value * value for value in buckets)) or 1.0
        return [round(value / norm, 6) for value in buckets]
