from qdrant_client import QdrantClient
from functools import lru_cache


class QdrantClientFactory:

    @staticmethod
    @lru_cache(maxsize=1)
    def get_client() -> QdrantClient:
        return QdrantClient(
            host="localhost",
            port=6333,
            timeout=30.0
        )