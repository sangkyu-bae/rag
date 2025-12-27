from app.infrastructure.qdrant.qdrant_repository import QdrantRepository
from langchain_community.retrievers import ContextualCompressionRetriever

class DocumentCompressorService:
    def __init__(self,retriever,filter):
        self._retriever = retriever
        self._filter = filter



    def get_compression_retriever(self,question:str):
        compression_retriever = ContextualCompressionRetriever(
            base_compressor=self._filter,
            base_retriever=self._retriever,
        )

        compressed_docs =  compression_retriever.aget_relevant_documents(question)
        return compressed_docs
