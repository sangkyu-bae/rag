# import logging
#
# from app.domain.document.chunk.service.chunk_service import ChunkService
# from app.domain.document.entity.document_type import DocumentType
# from app.domain.document.entity.documentinfo import DocumentInfo
# from app.domain.document.rule.entity.document_classification import DocumentClassification
# from app.domain.document.services.llm_parse_service import LlamaParseService
# from app.domain.document.entity.doc import Doc
# from app.domain.llm.embedding.openai_embeding_service import OpenAIEmbed
# from app.domain.llm.services.llm_client import LlmClient
# from app.domain.llm.prompt.prompt_registry import PromptRegistry
# import json
# import re
#
# from app.infrastructure.qdrant.qdrant_repository import QdrantRepository
# from app.service.pdf_service import PdfService
#
# logger = logging.getLogger(__name__)
#
# class ParseDocumentService:
#     def __init__(self):
#         pass
#
#     def execute(self, file_bytes: bytes, filename: str):
#         pdf_service = PdfService()
#         llm_client = LlmClient()
#         doc = pdf_service.normal_parse(file_bytes, filename)
#         logger.info(doc)
#         route_response: str = llm_client.ask(PromptRegistry._first_document_classification_prompt(),
#                                              doc.get_route_doc())
#         data = json.loads(route_response)
#
#         classification = DocumentClassification(**data)
#         embedding: OpenAIEmbed = OpenAIEmbed()
#         result : DocumentInfo
#         vectors = []
#         logger.info("documentType : -> %s", classification.document_type)
#
#         if classification.document_type == DocumentType.POLICY:
#             llama_parse_service = LlamaParseService()
#             result = llama_parse_service.parse_bytes(file_bytes, filename)
#         elif classification.document_type == DocumentType.MANUAL:
#             chunk_svc = ChunkService()
#             result = chunk_svc.full_chunk(doc)
#         else :
#             chunk_svc = ChunkService()
#             result = chunk_svc.chunk(doc,800,150)
#
#         logger.info(result)
#         doc_list :list[Doc]  = result.documents
#         embedding_result = embedding.embed([doc_result.content for doc_result in doc_list])
#
#         for i, (d, emb) in enumerate(zip(result, embedding_result)):
#             vectors.append({
#                 "id": i,
#                 "vector": emb,
#                 "payload": {
#                     "content": d.content,
#                     **d.metadata,
#                 }
#             })
#         qdrant_repository = QdrantRepository()
#         qdrant_repository.upsert(classification.document_type, vectors)
#
#         return result
#
#     def extract_json(text: str) -> dict:
#         # ```json ... ``` 제거
#         cleaned = re.sub(r"```json|```", "", text).strip()
#         cleaned = cleaned.strip()
#         return json.loads(cleaned)

# application/services/parse_document_service.py
import logging
from langchain_core.runnables import RunnableLambda

from app.infrastructure.langchain.langsmith import langsmith
from app.infrastructure.langchain.upsert import Upsert
from app.infrastructure.qdrant.qdrant_langchain_repository import QdrantLangchainRepository
from app.service.pdf_service import PdfService
from app.domain.llm.services.llm_client import LlmClient
from app.domain.llm.prompt.prompt_registry import PromptRegistry
from app.domain.document.rule.entity.document_classification import DocumentClassification
from app.domain.document.entity.document_type import DocumentType
from app.domain.document.chunk.service.chunk_service import ChunkService
from app.domain.document.services.llm_parse_service import LlamaParseService
from app.domain.llm.embedding.openai_embeding_service import OpenAIEmbed
from app.infrastructure.qdrant.qdrant_repository import QdrantRepository

import json

from langchain.agents import create_agent


logger = logging.getLogger(__name__)

class ParseDocumentService:
    """
    Application Service
    - Controller에서 호출
    - LCEL은 내부 구현
    """

    def __init__(self):
        self._chain = self._build_chain()

    def execute(self, file_bytes: bytes, filename: str):
        langsmith("parse")
        return self._chain.invoke({
            "file_bytes": file_bytes,
            "filename": filename
        })

    # =================================================
    # LCEL 파이프라인은 private
    # =================================================
    def _build_chain(self):

        parse_pdf = RunnableLambda(
            lambda x: {
                **x,
                "doc": PdfService().normal_parse(
                    x["file_bytes"], x["filename"]
                )
            }
        )

        classify = RunnableLambda(
            lambda x: {
                **x,
                "classification": DocumentClassification(
                    **json.loads(
                        LlmClient().ask(
                            PromptRegistry._first_document_classification_prompt(),
                            x["doc"].get_route_doc()
                        )
                    )
                )
            }
        )

        def router_fn(x):
            doc_type = x["classification"].document_type

            if doc_type == DocumentType.POLICY:
                return RunnableLambda(
                    lambda y: {
                        **y,
                        "result": LlamaParseService().parse_bytes(
                            y["file_bytes"], y["filename"]
                        )
                    }
                )

            if doc_type == DocumentType.MANUAL:
                return RunnableLambda(
                    lambda y: {
                        **y,
                        "result": ChunkService().full_chunk(y["doc"])
                    }
                )

            return RunnableLambda(
                lambda y: {
                    **y,
                    "result": ChunkService().chunk(
                        y["doc"], 800, 150
                    )
                }
            )

        router = RunnableLambda(router_fn)

        upsert = RunnableLambda(
            lambda x:{
                **x,
                "upsert_document": Upsert(OpenAIEmbed,QdrantLangchainRepository)
                                        .upsert(
                                                x["result"].get_upsert_document(),
                                                x["classification"].document_type,
                                        )
            }
        )

        return (
                parse_pdf
                | classify
                | router
                | upsert
        )


        # embed = RunnableLambda(
        #     lambda x: {
        #         **x,
        #         "vectors": [
        #             {
        #                 "id": i,
        #                 "vector": emb,
        #                 "payload": {
        #                     "content": d.content,
        #                     **d.metadata,
        #                 }
        #             }
        #             for i, (d, emb) in enumerate(
        #                 zip(
        #                     x["result"].documents,
        #                     OpenAIEmbed().embed(
        #                         [doc.content for doc in x["result"].documents]
        #                     )
        #                 )
        #             )
        #         ]
        #     }
        # )
        #
        # store = RunnableLambda(
        #     lambda x: QdrantRepository().upsert(
        #         x["classification"].document_type,
        #         x["vectors"]
        #     )
        # )


        # return (
        #     parse_pdf
        #     | classify
        #     | router
        #     | upsert
        #     # | embed
        #     # | store
        # )
