from app.domain.document.entity.documentinfo import DocumentInfo
from app.domain.document.services.llm_parse_service import LlamaParseService
from app.domain.document.entity.doc import Doc


class ParseDocumentService:
    def __init__(self):
        pass

    def execute(self,file_bytes:bytes,filename:str) :
        llama_parse_service = LlamaParseService()
        doc : DocumentInfo = llama_parse_service.parse_bytes(file_bytes, filename)

        route_chunk_request = doc.get_route_doc()
        docments:list[Doc] = doc.documents
        return ;