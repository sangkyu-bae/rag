from langchain_openai import ChatOpenAI

from app.domain.document.question.document_compressor_service import DocumentCompressorService
from app.domain.llm.embedding.openai_embeding_service import OpenAIEmbed
from app.infrastructure.document_compressors.llm_filter import LLMChainFilter
from app.infrastructure.tool.tool_executor import ToolExecutor
from app.infrastructure.vector_store.vector_db import VectorDB
from app.infrastructure.vector_store.vector_factory import VectorFactory, VectorType
from typing import List

from app.infrastructure.vector_store.vector_filter import VectorFilter


class VectorDBTool(ToolExecutor):

    def _execute(self,question:str):
        vector_db: VectorDB = VectorFactory.get_vectorstore(VectorType.QDRANT, OpenAIEmbed().embeddings)

        vector_filter_list: List[VectorFilter] = []
        vector_filter_list.append(
            VectorFilter.match("metadata.role", "child")
        )
        retriever =  vector_db.get_retriever(question,vector_filter_list)
        llm = ChatOpenAI(
            model = "gpt-4o-mini",
            temperature = 0.2,
            timeout = 30,
        )
        llm_filter = LLMChainFilter(llm)
        compression :DocumentCompressorService = DocumentCompressorService(retriever,LLMChainFilter)
        return compression.invoke(question)

