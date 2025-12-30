from langchain_core.runnables import Runnable
from langchain_core.documents import BaseDocumentCompressor
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

class DocumentCompressorService:
    def __init__(self, retriever, compressor: BaseDocumentCompressor):
        self._retriever = retriever
        self._compressor = compressor
        self.chain = self._build_chain()

    def _build_chain(self):
        return (
                RunnablePassthrough()
                | RunnableLambda(self._retrieve)
                | RunnableLambda(self._compress)
        )

    def _retrieve(self, question: str):
        docs = self._retriever.invoke(question)
        return {
            "question": question,
            "documents": docs
        }

    def _compress(self, x: dict):
        return self._compressor.compress_documents(
            documents=x["documents"],
            query=x["question"]
        )

    def invoke(self, question: str):
        return self.chain.invoke(question)

    # def __init__(self,retriever,filter,chain):
    #     self._retriever = retriever
    #     self._filter = filter
    #     self.chain = self.build_chain()
    #
    #
    # def build_chain(self,question:str):
    #     return (
    #             self._retriever|
    #             self._filter
    #     )

    # def get_compression_retriever(self,question:str):
    #     compression_retriever = ContextualCompressionRetriever(
    #         base_compressor=self._filter,
    #         base_retriever=self._retriever,
    #     )
    #
    #     compressed_docs =  compression_retriever.aget_relevant_documents(question)
    #     return compressed_docs
    # async def get_compressed_documents(self, question: str):
    #     # 1. 검색
    #     docs = await self._retriever.aget_relevant_documents(question)
    #
    #     # 2. 압축 / 필터링
    #     compressed_docs = await self._filter.acompress_documents(
    #         docs, question
    #     )
    #
    #     return compressed_docs

