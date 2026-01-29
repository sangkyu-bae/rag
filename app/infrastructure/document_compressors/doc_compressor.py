from typing import List

from langchain_core.documents import Document, BaseDocumentCompressor


class DocumentCompressor:
    def __init__(self,doc_list:List[Document],filters:BaseDocumentCompressor,query:str):
        self.doc_list = doc_list
        self.filters = filters
        self.query = query

    def _compress(self):
        return self.filters.compress_documents(
            documents=self.doc_list,
            query=self.query,
        )



