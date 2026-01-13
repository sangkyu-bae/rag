import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, UploadFile, File
import pandas as pd
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.output_parsers import JsonOutputToolsParser
from langchain_core.prompts import ChatPromptTemplate

from app.domain.llm.services.llm_client import LlmClient
from app.infrastructure.langchain.langsmith import langsmith
from app.service.tool.web_search.test import get_tools, execute_tool_calls

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/parse")
async def analyze_excel(
    file: UploadFile = File(...),
    sheet_name: Optional[str] = None,
    sample_rows: int = 50,
):
    try:
        dfs = pd.read_excel(
            file.file,
            sheet_name=None,
            engine="openpyxl",
            dtype=str,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Excel parse failed: {e}")

    sheet_names = list(dfs.keys())
    target_sheet = sheet_name or sheet_names[0]

    if target_sheet not in sheet_names:
        raise HTTPException(
            status_code=400,
            detail=f"Sheet not found. available={sheet_names}",
        )

    df = dfs[target_sheet]

    # ⭐ 핵심 라인
    df = df.where(pd.notna(df), None)

    payload = {
        "sheet_name": target_sheet,
        "row_count": len(df),
        "columns": list(df.columns),
        "sample_rows": df.head(sample_rows).to_dict(orient="records"),
    }

    system = """
         You are a senior data analyst and Excel structure expert.
        
        Your task is NOT to calculate numbers.
        Your task is to understand the STRUCTURE of a human-made Excel report
        and explain how it should be interpreted for programmatic analysis.
        
        Think in terms of:
        - header rows
        - category rows
        - subtotal / total rows
        - value columns
        - hierarchical grouping
    """

    user ="""
        The following JSON is extracted from an Excel sheet using pandas.
        This Excel file is a HUMAN-ORIENTED REPORT, not a clean data table.
        
        Your job:
        1. Identify which rows are:
           - title / description rows
           - header rows
           - actual data rows
           - subtotal or total rows
        
        2. Identify which column represents:
           - row labels (e.g. 항목명, 구분)
           - category hierarchy (e.g. 본부 / 팀)
           - numeric value columns
        
        3. Explain the logical table structure in plain language.
        
        4. Propose a normalized table schema suitable for pandas analysis.
           (Do NOT compute values.)
        
        5. Output a JSON plan that explains:
           - how many top rows should be skipped
           - which row should be used as header
           - how to interpret hierarchical columns
           - how to detect subtotal / total rows
        
        ⚠️ Important rules:
        - Do NOT calculate or summarize numbers.
        - Do NOT hallucinate missing data.
        - Base your reasoning ONLY on the given JSON.
        - If something is unclear, explicitly say it is ambiguous.
        
        Here is the extracted Excel data:
        <EXCEL_JSON>
        {{payload}}
        </EXCEL_JSON>
    """
    llm = LlmClient("gpt-4o-mini",0.1,30)
    tt = llm.ask(system_prompt=system,user_prompt=user)
    return tt

@router.post("/test")
async def test(
    url:str
):
    langsmith("tools_question")
    llm = LlmClient("gpt-4o-mini",0.0,30).llm
    # llm_with_tools = llm.bind_tools(get_tools())
    # chain = llm_with_tools|JsonOutputToolsParser(tools=get_tools())|execute_tool_calls
    #
    # return chain.invoke("뉴스 기사 내용을 크롤링해줘:"+url)
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful assistant. "
                "Make sure to use the `search_news` tool for searching keyword related news.",
            ),
            # ("placeholder", "{chat_history}"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    )
    tools = get_tools()
    agent = create_tool_calling_agent(llm,tools,prompt)

    # AgentExecutor 생성
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=10,
        max_execution_time=10,
        handle_parsing_errors=True,
    )

    result = agent_executor.invoke({"input": "AI 투자와 관련된 뉴스를 검색해 주세요."})

