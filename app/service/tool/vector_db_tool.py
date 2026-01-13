from langchain_openai import ChatOpenAI

from app.domain.document.question.document_compressor_service import DocumentCompressorService
from app.domain.llm.embedding.openai_embeding_service import OpenAIEmbed
from app.infrastructure.document_compressors.llm_filter import LLMChainFilter
from app.service.tool.tool_executor import ToolExecutor
from app.infrastructure.vector_store.vector_db import VectorDB
from app.infrastructure.vector_store.vector_factory import VectorFactory, VectorType
from typing import List

from app.infrastructure.vector_store.vector_filter import VectorFilter


class VectorDBTool(ToolExecutor):
    def __init__(self,collection:str):
        self.collection = collection
    def execute(self, question: str):
        # 1. VectorStore
        vector_db: VectorDB = VectorFactory.get_vectorstore(
            VectorType.QDRANT,
            OpenAIEmbed().embeddings
        )

        # 2. Filter
        vector_filter_list: List[VectorFilter] = [
            VectorFilter.match("metadata.role", "child")
        ]

        retriever = vector_db.get_retriever(
            filters=vector_filter_list,
            collection=self.collection,
        )

        # 3. LLM
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.2,
            timeout=30,
        )

        # 4. Compressor
        llm_filter = LLMChainFilter.from_llm(llm=llm)
        compression = DocumentCompressorService(
            retriever=retriever,
            compressor=llm_filter
        )

        return compression.invoke(question)
