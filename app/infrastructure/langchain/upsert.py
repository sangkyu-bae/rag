from openai import vector_stores

from langchain_core.documents import Document

class Upsert():
    def __init__(self, embed_model,embed_repository):
        self.embed_model = embed_model
        self.embed_repository = embed_repository(self.embed_model)

    def upsert(self,collection:str, docs :list[Document]):
        vector_stores = self.embed_repository.get_vectorstore(collection)
        vector_stores.add_documents(docs)
