from app.domain.document.entity.doc import Doc
from app.domain.document.entity.documentinfo import DocumentInfo
from langchain_text_splitters import RecursiveCharacterTextSplitter
import logging

logger = logging.getLogger(__name__)

class ChunkService:
    def __init__(self):
        pass


    def full_chunk(self,doc:DocumentInfo)-> DocumentInfo:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500,
            chunk_overlap=200,
            separators=["\n\n", "\n", ".", " ", ""],
        )
        texts = splitter.split_text(doc.content)
        metadata = doc.metadata
        metadata["total_chunks"] = len(texts)
        doc_list:list[Doc] = []
        for idx,text in enumerate(texts):
            metadata["chunk_index"] = idx
            metadata["role"] = "child"
            doc_list.append(
                Doc.from_document_pdf(text, metadata)
            )
        doc.set_child_document(doc_list)
        return doc

    def chunk(self,doc:DocumentInfo,chunk_size,chunk_overlap) -> DocumentInfo:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ".", " ", ""],
        )

        chunks = splitter.split_documents(doc.get_upsert_document())
        doc_list:list[Doc] = []
        for idx, chunk in enumerate(chunks):
            chunk.metadata["chunk_index"] = idx
            chunk.metadata["role"] = "child"
            chunk.metadata["total_chunks"] = len(chunks)
            doc_list.append(
                Doc.from_document_pdf(chunk.page_content, chunk.metadata)
            )
        doc.set_child_document(doc_list)
        return doc


