
class DocumentCompressorService:
    def __init__(self,retriever,filter):
        self._retriever = retriever
        self._filter = filter



    # def get_compression_retriever(self,question:str):
    #     compression_retriever = ContextualCompressionRetriever(
    #         base_compressor=self._filter,
    #         base_retriever=self._retriever,
    #     )
    #
    #     compressed_docs =  compression_retriever.aget_relevant_documents(question)
    #     return compressed_docs
    async def get_compressed_documents(self, question: str):
        # 1. 검색
        docs = await self._retriever.aget_relevant_documents(question)

        # 2. 압축 / 필터링
        compressed_docs = await self._filter.acompress_documents(
            docs, question
        )

        return compressed_docs
