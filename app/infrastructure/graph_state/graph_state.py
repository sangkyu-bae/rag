from typing import TypedDict, Annotated, List


class GraphState(TypedDict):
    """
     그래프의 상태를 나타내는 데이터 모델

     Attributes:
         question: 질문
         generation: LLM 생성된 답변
         documents: 도큐먼틑 리스트
     """

    question: Annotated[str, "User question"]
    generation: Annotated[str, "LLM generated answer"]
    documents: Annotated[List[str], "List of documents"]