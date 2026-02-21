from typing import Type

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

REPORT_SYSTEM_PROMPT = """
You are a senior strategic analyst working in a financial institution.

Your job is to convert aggregated analysis results into a structured,
decision-ready executive report.

[STRICT RULES]
- Do NOT hallucinate new data.
- Use ONLY the provided context.
- If data is insufficient, explicitly state limitations.
- Clearly separate facts from interpretation.
- Maintain a professional executive tone.
- Avoid speculation.
"""

REPORT_USER_PROMPT = """
Create a structured report.

[REPORT STRUCTURE]

1. Executive Summary
2. Key Findings
3. Interpretation & Insights
4. Risks & Concerns
5. Recommendations

Report Type: {report_type}
Audience: {audience}

Context:
{context}
"""



class ReportInput(BaseModel):
    context: str = Field(
        description="Research 팀, 데이터분석 팀 등에서 수집된 모든 분석 결과 텍스트"
    )
    report_type: str = Field(
        description="보고서 유형 (예: 경영보고, 기술보고, 시장분석보고, 리스크보고)"
    )
    audience: str = Field(
        description="보고서를 읽는 대상 (예: 경영진, 개발팀, 투자자)"
    )

class Report(BaseTool):
    name:str = "report"
    description: str = """
        Generate a structured, executive-level report based on aggregated analysis results.
    
        Use this tool when:
        - Multiple analysis results must be synthesized
        - A structured business report is required
        - Insights, risks, and action items must be clearly presented
        - The output must be decision-ready
    
        Do NOT use this tool for:
        - Raw data analysis
        - Simple summarization
        - Web search tasks
        - Vector database retrieval
    
        This tool transforms analysis outputs into a professional, structured report.
    """
    args_schema: Type[BaseModel] = ReportInput

    def _run(self, context: str, report_type: str, audience: str) -> str:
        llm = ChatOpenAI(model="gpt-4o", temperature=0)

        prompt = ChatPromptTemplate.from_messages([
            ("system", REPORT_SYSTEM_PROMPT),
            ("human", REPORT_USER_PROMPT),
        ])

        chain = prompt | llm

        response = chain.invoke({
            "context": context,
            "report_type": report_type,
            "audience": audience
        })

        return response
