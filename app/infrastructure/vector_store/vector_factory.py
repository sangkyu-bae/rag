from langchain_core.embeddings import Embeddings

from app.infrastructure.qdrant.qdrant_langchain_repository import QdrantLangchainRepository
from app.infrastructure.vector_store.vector_db import VectorDB

from enum import Enum
class VectorType(str, Enum):
    QDRANT = "qdrant"
    FAISS = "faiss"

class VectorFactory:

    @staticmethod
    def get_vectorstore(
            vector_type: VectorType,
            embed_model:Embeddings
    ) -> VectorDB:
        if vector_type == VectorType.QDRANT:
            return QdrantLangchainRepository(embed_model)


