import logging

from app.domain.document.chunk.service.chunk_service import ChunkService
from app.domain.document.entity.documentinfo import DocumentInfo
from app.domain.document.rule.entity.document_classification import DocumentClassification
from app.domain.document.services.llm_parse_service import LlamaParseService
from app.domain.document.entity.doc import Doc
from app.domain.llm.embedding.openai_embeding_service import OpenAIEmbed
from app.domain.llm.services.llm_client import LlmClient
from app.domain.llm.prompt.prompt_registry import PromptRegistry
import json
import re

from app.infrastructure.qdrant.qdrant_repository import QdrantRepository
from app.service.pdf_service import PdfService

logger = logging.getLogger(__name__)

class ParseDocumentService:
    def __init__(self):
        pass

    def execute(self, file_bytes: bytes, filename: str):
        pdf_service = PdfService()
        llm_client = LlmClient()
        doc = pdf_service.normal_parse(file_bytes, filename)
        logger.info(doc)
        route_chunk_request: str = doc.get_first_route_llm()

        route_response: str = llm_client.ask(PromptRegistry._first_document_classification_prompt(),
                                             doc.get_route_doc())
        data = json.loads(route_response)

        classification = DocumentClassification(**data)

        docments: list[Doc] = doc.documents
        result :list[str] = []
        if classification.document_type == 'policy':
            logger.info("tt -> %s", classification.document_type)

        if classification.document_type == 'manual':
            chunk_svc = ChunkService()
            result :list[Doc]= chunk_svc.full_chunk(doc)
            logger.info(result)
            embedding :OpenAIEmbed= OpenAIEmbed()
            embedding_result = embedding.embed([doc.content for doc in result])
            vectors = []
            for i, (d, emb) in enumerate(zip(result, embedding_result)):
                vectors.append({
                    "id": i,
                    "vector": emb,
                    "payload": {
                        "content": d.content,
                        **d.metadata,
                    }
                })
            qdrant_repository = QdrantRepository()
            qdrant_repository.upsert("manual", vectors)


        return result


        # llama_parse_service = LlamaParseService()
        # llm_client = LlmClient()
        # doc: DocumentInfo = llama_parse_service.parse_bytes(file_bytes, filename)
        #
        # route_chunk_request: str = doc.get_first_route_llm()
        #
        # route_response: str = llm_client.ask(PromptRegistry._first_document_classification_prompt(),
        #                                      doc.get_route_doc())
        # logger.info("route res [{s}]", route_response)
        # data = json.loads(route_response)
        #
        # classification = DocumentClassification(**data)
        #
        # docments: list[Doc] = doc.documents
        #
        # if classification.document_type == 'policy':
        #     logger.info("tt -> %s", classification.document_type)
        #
        # return doc;
    # def execute(self,file_bytes:bytes,filename:str) :
    #     llama_parse_service = LlamaParseService()
    #     llm_client = LlmClient()
    #     doc : DocumentInfo = llama_parse_service.parse_bytes(file_bytes, filename)
    #
    #     route_chunk_request:str = doc.get_first_route_llm()
    #
    #     route_response :str = llm_client.ask(PromptRegistry._first_document_classification_prompt(),doc.get_route_doc())
    #     logger.info("route res [{s}]", route_response)
    #     data = json.loads(route_response)
    #
    #     classification = DocumentClassification(**data)
    #
    #     docments:list[Doc] = doc.documents
    #
    #     if classification.document_type=='policy':
    #         logger.info("tt -> %s", classification.document_type)
    #
    #
    #     return doc;


    def extract_json(text: str) -> dict:
        # ```json ... ``` 제거
        cleaned = re.sub(r"```json|```", "", text).strip()
        cleaned = cleaned.strip()
        return json.loads(cleaned)