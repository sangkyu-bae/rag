import logging

from langchain_core.runnables import RunnableLambda
from langchain_experimental.llms.anthropic_functions import prompt

from app.domain.document.question.document_compressor_service import DocumentCompressorService
from app.domain.llm.embedding.openai_embeding_service import OpenAIEmbed
from app.domain.llm.prompt.prompt_registry import PromptRegistry
from app.domain.llm.services.llm_client import LlmClient
from app.infrastructure.document_compressors.llm_filter import LLMChainFilter
from app.infrastructure.langchain.langsmith import langsmith
from app.infrastructure.qdrant.qdrant_langchain_repository import QdrantLangchainRepository
from langchain_core.prompts import ChatPromptTemplate

logger = logging.getLogger(__name__)

class QuestionService:
    def __init__(
            self,
            model:str ="gpt-4o-mini",
            temperature: float = 0.2,
            timeout: int = 30,
    ):
        self.llm = LlmClient(model,temperature,timeout)
        self._chain = self._build_chain()
        self.filter =LLMChainFilter.from_llm(self.llm.llm)
        self.retriever = QdrantLangchainRepository(OpenAIEmbed().embeddings).get_retriever("test")
        self.compression = DocumentCompressorService(self.retriever,self.filter)


    def execute(self, question:str):
        langsmith("question")
        return self._chain.invoke({
            "question": question,
        })

    def normalize_docs(self,docs):
        return [
            {
                "content": d.page_content,
                "source": {
                    "file_name": d.metadata.get("file_name"),
                    "page": d.metadata.get("page"),
                    "chunk_index": d.metadata.get("chunk_index"),
                }
            }
            for d in docs
        ]
    def _build_chain(self):
        compress_doc = RunnableLambda(
            lambda x:{
                **x,
                "tool_outputs" : self.normalize_docs(self.compression.invoke(x["question"]))
            }
        )

        build_payload = RunnableLambda(PromptRegistry.basic_prompt)
        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "출력은 반드시 JSON만 사용한다. "
                "payload_json을 읽고 규칙을 엄격히 준수하라."
            ),
            (
                "human",
                """
                payload:
                {payload_json}
                
                출력은 다음 JSON 스키마를 반드시 만족해야 한다:
                {format_instructions}
                """
            )
        ])
        return (
            compress_doc|
            build_payload|
            prompt|
            self.llm.llm
        )

