from typing import List
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct
)
from app.infrastructure.qdrant.qdrant_client_factory import QdrantClientFactory


class QdrantRepository:

    def __init__(self):
        self.client = QdrantClientFactory.get_client()

    def create_collection(self, collection: str, vector_size: int = 1536):
        if self.client.collection_exists(collection):
            return

        self.client.recreate_collection(
            collection_name=collection,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE,
            ),
        )

    def upsert(self, collection: str, items: List[dict]):
        collections = [c.name for c in self.client.get_collections().collections]
        if collection not in collections:
            self.create_collection(collection)

        points = []
        for item in items:
            points.append(
                PointStruct(
                    id=item["id"],
                    vector=item["vector"],
                    payload=item["payload"]
                )
            )

        self.client.upsert(collection_name=collection, points=points)

    def search(self, collection: str, query: str, top_k: int = 5):
        return self.client.search(
            collection_name=collection,
            query_vector=query,
            limit=top_k
        )

    def delete_collection(self, collection: str):
        if self.client.collection_exists(collection):
            self.client.delete_collection(collection)

