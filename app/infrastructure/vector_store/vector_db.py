from abc import ABC, abstractmethod

from app.infrastructure.vector_store.vector_filter import VectorFilter


class VectorDB(ABC):
    @abstractmethod
    def _ensure_collection(self, collection):
        pass
    @abstractmethod
    def get_vectorstore(self,collection):
        pass
    @abstractmethod
    def delete_collection(self,collection:str):
        pass
    @abstractmethod
    def get_retriever(self,collection:str,filters:list[VectorFilter], k:int):
        pass