from typing import Literal

from pydantic import BaseModel

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI

prompt:str ="""
    You are a query routing classifier.

    Your task is to classify a user's question into exactly one datasource:
    
    [vectorstore]
    Use this when the question is about:
    - Internal company knowledge or proprietary documents
    - Technical specifications, system design, architecture, APIs, code conventions, operational manuals
    - Previously indexed documents, PDFs, internal reports, or uploaded files
    - Stable knowledge that does not require real-time updates
    
    [web_search]
    Use this when the question is about:
    - Real-time information, recent events, news, market data, or live statistics
    - Public information not owned by the organization
    - Information that changes frequently or must be verified externally
    - Topics unlikely to exist in private documents
    
    Rules:
    - If unsure or ambiguous → choose web_search.
    - Do not explain your reasoning.
    - Output only one value: "vectorstore" or "web_search".
"""

class RouteQuery(BaseModel):
    """Route a user query to the most relevant datasource."""

    # 데이터 소스 선택을 위한 리터럴 타입 필드
    datasource: Literal["vectorstore", "web_search"] = Field(
        ...,
        description="Given a user question choose to route it to web search or a vectorstore.",
    )

    @staticmethod
    def get_route_type():
        llm = ChatOpenAI(model="gpt-4o-mini",temperature=0)
        structured_llm_router = llm.with_structured_output(RouteQuery)
        system = prompt

        route_prompt = ChatPromptTemplate.from_messages(
            [
                ("system",system),
                ("human","{question}")
            ]
        )

        return (route_prompt | structured_llm_router)