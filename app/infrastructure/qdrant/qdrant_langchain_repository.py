# from app.infrastructure.qdrant.qdrant_client_factory import QdrantClientFactory
#
# from langchain_community.vectorstores import Qdrant
# class QdrantLangchainRepository:
#     """
#     LangChain 기반 Qdrant Repository
#     - 컬렉션 관리
#     - VectorStore 생성 책임
#     """
#
#     def __init__(self,embed_model):
#         self.client = QdrantClientFactory.get_client()
#         self.embed_model = embed_model
#
#
#     def get_vectorstore(self,collection: str)-> Qdrant:
#         """
#          컬렉션 기반 VectorStore 반환
#          (없으면 자동 생성)
#          """
#         return Qdrant(
#             client=self.client,
#             collection_name=collection,
#             embeddings=self.embed_model
#         )
#     def delete_collection(self,collection:str):
#         if self.client.collection_exists(collection):
#             self.client.delete_collection(collection)
#
#     def get_retriever(self, collection: str, k: int = 10):
#         vectorstore = self.get_vectorstore(collection)
#         return vectorstore.as_retriever(
#             search_kwargs={"k": k}
#         )

from qdrant_client.models import VectorParams, Distance
from langchain_qdrant import Qdrant
from app.infrastructure.qdrant.qdrant_client_factory import QdrantClientFactory


class QdrantLangchainRepository:
    """
    LangChain 기반 Qdrant Repository
    - 컬렉션 관리
    - VectorStore 생성 책임
    """

    def __init__(self, embed_model):
        self.client = QdrantClientFactory.get_client()
        print(type(self.client), self.client)
        print("has search?", hasattr(self.client, "search"))
        print("dir contains search?", "search" in dir(self.client))

        self.embed_model = embed_model

    def _ensure_collection(self, collection: str):
        if self.client.collection_exists(collection):
            return

        # 🔑 embedding 차원 계산 (1회)
        dim = len(self.embed_model.embed_query("dimension check"))

        self.client.create_collection(
            collection_name=collection,
            vectors_config=VectorParams(
                size=dim,
                distance=Distance.COSINE,
            ),
        )

    def get_vectorstore(self, collection: str) -> Qdrant:
        """
        컬렉션 기반 VectorStore 반환
        (없으면 생성 보장)
        """
        self._ensure_collection(collection)

        return Qdrant(
            client=self.client,
            collection_name=collection,
            embeddings=self.embed_model,
        )

    def delete_collection(self, collection: str):
        if self.client.collection_exists(collection):
            self.client.delete_collection(collection)

    def get_retriever(self, collection: str, k: int = 10):
        vectorstore = self.get_vectorstore(collection)
        return vectorstore.as_retriever(search_kwargs={"k": k})
