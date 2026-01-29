# class GradeNode:
#     def __call__(self):
from langchain_openai import ChatOpenAI

from app.infrastructure.document_compressors.doc_compressor import DocumentCompressor
from app.infrastructure.document_compressors.llm_filter import LLMChainFilter


def grade_documents(state):
    print("==== [CHECK DOCUMENT RELEVANCE TO QUESTION] ====")
    # 질문과 문서 검색 결과 가져오기
    question = state["question"]
    documents = state["documents"]
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        timeout=30
    )
    llm_filter = LLMChainFilter.from_llm(llm=llm)

    doc_compress:DocumentCompressor = DocumentCompressor(
        doc_list=documents,
        filters=llm_filter,
        query=question,
    )

    filter_doc = doc_compress._compress()
    return {
        "question": question,
        "documents": filter_doc,
    }
