from app.domain.document.entity.doc import Doc
from app.domain.document.entity.documentinfo import DocumentInfo
from langchain_text_splitters import RecursiveCharacterTextSplitter
class ChunkService:
    def __init__(self):
        pass


    def full_chunk(self,doc:DocumentInfo)-> DocumentInfo:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1500,
            chunk_overlap=200,
            separators=["\n\n", "\n", ".", " ", ""],
        )
        splitter_text = splitter.split_text(doc.content)

        doc_list: list[Doc] = [Doc.from_document_pdf(text,doc.metadata) for text in splitter_text]

        return  DocumentInfo.from_doc_info(doc.content,doc.metadata,doc_list)

    def chunk(self,doc:DocumentInfo,chunk_size,chunk_overlap) -> DocumentInfo:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", ".", " ", ""],
        )

        chunks = splitter.split_documents(doc.get_upsert_document())
        doc_list = []
        for idx, chunk in enumerate(chunks):
            chunk.metadata["chunk_index"] = idx
            chunk.metadata["role"] = "child"
            doc_list.append(
                Doc.from_document_pdf(chunk.page_content, chunk.metadata)
            )
        return doc


