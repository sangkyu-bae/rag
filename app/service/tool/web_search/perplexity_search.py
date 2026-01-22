from langchain_community.chat_models import ChatPerplexity
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.tools import BaseTool
from typing import Optional, Dict, Any
import os
import httpx
import json

from pydantic import Field, BaseModel


class PerplexityResearchInput(BaseModel):
    """Input for the Perplexity Research tool."""

    query: str = Field(description="웹 기반 조사가 필요한 질문")
    # focus: Optional[str] = Field(
    #     default=None,
    #     description="요약 관점 (예: '핵심만 5줄', '장단점 비교', '정책 변경 중심')"
    # )

class PerplexityResearch(BaseTool):
    """
    Tool that performs web-grounded research using Perplexity API
    and returns summarized results with citations.
    """

    name: str = "perplexity_web_research"
    description: str = (
        "웹 검색이 필요한 질문에 대해 Perplexity를 사용해 조사하고 "
        "요약 + 출처(URL)를 함께 반환합니다. "
        "정리, 비교, 최신 동향 파악에 적합합니다."
    )

    args_schema: type[BaseModel] = PerplexityResearchInput

    model: str = "sonar-pro"
    temperature: float = 0.2
    max_tokens: int = 900
    llm:type[ChatPerplexity] =None

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "sonar-pro",
        temperature: float = 0.2,
        max_tokens: int = 900,
    ):
        super().__init__()

        if api_key is None:
            api_key = os.environ.get("PPLX_API_KEY", None)

        if api_key is None:
            raise ValueError("PPLX API key is not set.")


        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.llm = ChatPerplexity(
            model=self.model,
            temperature=self.temperature,
            pplx_api_key=api_key
        )

    # LangChain / LangGraph 진입점
    # def _run(self, query: str, focus: Optional[str] = None) -> str:
    def _run(self, query: str) -> str:
        result = self.research(query=query)
        return json.dumps(result, ensure_ascii=False)

    # def research(self, query: str, focus: Optional[str] = None) -> Dict[str, Any]:
    def research(self, query: str) -> Dict[str, Any]:
        """
        Perplexity API를 호출해 웹 기반 조사 수행
        """

        system_prompt = (
            "You are a web-grounded research assistant. "
            "Answer in Korean. "
            "Summarize clearly using bullet points. "
            "ALWAYS include sources (URLs). "
            "If information is uncertain, explicitly say so."
        )

        user_prompt = query
        # if focus:
        #     user_prompt += f"\n\n[요약 관점]\n{focus}"

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]
        response = self.llm.invoke(messages)
        return {
            "query": query,
            "summary": response.content,
            "model": self.llm.model,
        }
