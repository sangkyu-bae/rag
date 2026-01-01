from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document
from typing import List

class EnsembleRetrieverService(BaseRetriever):
    def __init__(self, retrievers, weights):
        self.retrievers = retrievers
        self.weights = weights

    def _get_relevant_documents(self,collection:str,index:str)->List[Document]:
        scored = {}

        for retriever, weight in zip(self.retrievers, self.weights):
            docs = retriever._get_relevant_documents(query)

            for rank, doc in enumerate(docs):
                key = doc.metadata.get("chunk_id", doc.page_content)

                if key not in scored:
                    scored[key] = {
                        "doc": doc,
                        "score": 0.0
                    }

                # 간단하고 안정적인 rank-based score
                scored[key]["score"] += weight * (1.0 / (rank + 1))

        return [
            v["doc"]
            for v in sorted(
                scored.values(),
                key=lambda x: x["score"],
                reverse=True
            )
        ]

    async def _aget_relevant_documents(self, query: str):
        return self._get_relevant_documents(query)

