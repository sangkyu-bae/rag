from app.infrastructure.qdrant.qdrant_client_factory import QdrantClientFactory
from app.infrastructure.qdrant.qdrant_repository import QdrantRepository

from langchain_community.vectorstores import Qdrant
class QdrantLangchainRepository:
    """
    LangChain 기반 Qdrant Repository
    - 컬렉션 관리
    - VectorStore 생성 책임
    """

    def __init__(self,embed_model):
        self.client = QdrantClientFactory.get_client()
        self.embed_model = embed_model


    def get_vectorstore(self,collection: str)-> Qdrant:
        """
             컬렉션 기반 VectorStore 반환
             (없으면 자동 생성)
             """
        return Qdrant(
            client=self.client,
            collection_name=collection,
            embedding=self.embed_model
        )
    def delete_collection(self,collection:str):
        if self.client.collection_exists(collection):
            self.client.delete_collection(collection)
