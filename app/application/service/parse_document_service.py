import logging

from app.domain.document.chunk.service.chunk_service import ChunkService
from app.domain.document.entity.document_type import DocumentType
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
        route_response: str = llm_client.ask(PromptRegistry._first_document_classification_prompt(),
                                             doc.get_route_doc())
        data = json.loads(route_response)

        classification = DocumentClassification(**data)
        embedding: OpenAIEmbed = OpenAIEmbed()
        result : DocumentInfo
        vectors = []
        logger.info("documentType : -> %s", classification.document_type)

        if classification.document_type == DocumentType.POLICY:
            llama_parse_service = LlamaParseService()
            result = llama_parse_service.parse_bytes(file_bytes, filename)
        elif classification.document_type == DocumentType.MANUAL:
            chunk_svc = ChunkService()
            result = chunk_svc.full_chunk(doc)
        else :
            chunk_svc = ChunkService()
            result = chunk_svc.chunk(doc,800,150)

        logger.info(result)
        doc_list :list[Doc]  = result.documents
        embedding_result = embedding.embed([doc_result.content for doc_result in doc_list])

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
        qdrant_repository.upsert(classification.document_type, vectors)

        return result

    def extract_json(text: str) -> dict:
        # ```json ... ``` 제거
        cleaned = re.sub(r"```json|```", "", text).strip()
        cleaned = cleaned.strip()
        return json.loads(cleaned)