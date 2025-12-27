from app.domain.document.entity.doc import Doc
from app.domain.document.entity.documentinfo import DocumentInfo
from langchain_text_splitters import RecursiveCharacterTextSplitter
class ChunkService:
    def __init__(self):
        pass


    def full_chunk(self,doc:DocumentInfo)-> DocumentInfo:
        return self.chunk(doc,1500,200)

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
            doc_list.append(
                Doc.from_document_pdf(chunk.page_content, chunk.metadata)
            )
        doc.set_child_document(doc_list)
        return doc


