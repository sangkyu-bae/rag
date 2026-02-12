from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

from app.infrastructure.vector_store.vector_db import VectorDB

class VectorSearchInput(BaseModel):
    """Input for the Qdrant tool"""
    query :str =Field(description = "검색쿼리")

class VectorSearch(BaseTool):
    name:str = "qdrant_vector_search"
    description:str = (
        """Search documents in a collection using semantic, keyword, or hybrid search.
    
         This function is used to find relevant documents within a specific collection based on a search query.
         It supports multiple search types to provide flexible document retrieval capabilities.
         The function returns structured search results with document content, metadata, relevance scores, and document IDs.
    
         Args:
             collection_id: The unique identifier of the collection to search in. This should be obtained
                           from the list_collections() function or provided by the user.
             query: The search query string to find relevant documents. This can be a natural language
                    question, keywords, or any text that describes what you're looking for.
             limit: Maximum number of documents to return. Default is 5, maximum allowed is 100.
                    Higher limits provide more results but may take longer to process.
             search_type: Type of search algorithm to perform. Options include:
                         - "semantic": Uses vector similarity search (recommended for natural language queries)
                         - "keyword": Uses traditional text matching (good for exact terms)
                         - "hybrid": Combines both semantic and keyword search (best overall results)
             filter_json: Optional JSON string containing metadata filters to narrow down the search scope.
                         Example: '{"source": "sample.pdf", "category": "technical"}'
                         This helps focus the search on specific document types or sources.
         """
    )
    args_schema: type[BaseModel] = VectorSearchInput
    # vector_db : VectorDB = None

    def __init(
            self,
            vector_db: VectorDB,
    ):
        self.vector_db = vector_db

    def _run(self,query:str)->str:
        results = self.search(query)
        return results

    def search(
            self,
            query:str
    ) -> list:
        res = self.vector_db.excute(question=query)
        return res




