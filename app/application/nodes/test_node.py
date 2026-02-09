# Tavily 검색 도구 정의
from typing import Annotated

from langchain_core.messages import  HumanMessage
from langchain_core.prompts import MessagesPlaceholder, ChatPromptTemplate
from langchain_experimental.utilities import PythonREPL
from langgraph.graph import MessagesState

from app.application.nodes.route_response import options_for_next, members, RouteResponse
from app.service.tool.web_search.tavil_search import TavilySearch
from langchain_core.tools import tool



# Python 코드를 실행하는 도구 정의
python_repl = PythonREPL()
# Python 코드를 실행하는 도구 정의
@tool
def python_repl_tool(
    code: Annotated[str, "The python code to execute to generate your chart."],
):
    """Use this to execute python code. If you want to see the output of a value,
    you should print it out with `print(...)`. This is visible to the user."""
    try:
        # 주어진 코드를 Python REPL에서 실행하고 결과 반환
        result = python_repl.run(code)
    except BaseException as e:
        return f"Failed to execute code. Error: {repr(e)}"
    # 실행 성공 시 결과와 함께 성공 메시지 반환
    result_str = f"Successfully executed:\n```python\n{code}\n```\nStdout: {result}"
    return (
        result_str + "\n\nIf you have completed all tasks, respond with FINAL ANSWER."
    )

prompt =  ("You are a helpful AI assistant, collaborating with other assistants."
        " Use the provided tools to progress towards answering the question."
        " If you are unable to fully answer, that's OK, another assistant with different tools "
        " will help where you left off. Execute what you can to make progress."
        " If you or any of the other assistants have the final answer or deliverable,"
        " prefix your response with FINAL ANSWER so the team knows to stop.")

def routers(state: MessagesState):
    # This is the router
    messages = state["messages"]
    last_message = messages[-1]
    print(last_message)
    if "FINAL ANSWER" in last_message.content:
        # Any agent decided the work is done
        from langgraph.graph import END  # 👈 이걸 사용
        return END
    return "continue"
def chart_node(state: MessagesState) -> MessagesState:
    from langchain_openai import ChatOpenAI
    llm = ChatOpenAI(model="gpt-5.1")

    chart_generator_system_prompt = """
    You can only generate charts. You are working with a researcher colleague.
    Be sure to use the following font code in your code when generating charts.

    ##### 폰트 설정 #####
    import platform

    # OS 판단
    current_os = platform.system()

    if current_os == "Windows":
        # Windows 환경 폰트 설정
        font_path = "C:/Windows/Fonts/malgun.ttf"  # 맑은 고딕 폰트 경로
        fontprop = fm.FontProperties(fname=font_path, size=12)
        plt.rc("font", family=fontprop.get_name())
    elif current_os == "Darwin":  # macOS
        # Mac 환경 폰트 설정
        plt.rcParams["font.family"] = "AppleGothic"
    else:  # Linux 등 기타 OS
        # 기본 한글 폰트 설정 시도
        try:
            plt.rcParams["font.family"] = "NanumGothic"
        except:
            print("한글 폰트를 찾을 수 없습니다. 시스템 기본 폰트를 사용합니다.")

    ##### 마이너스 폰트 깨짐 방지 #####
    plt.rcParams["axes.unicode_minus"] = False  # 마이너스 폰트 깨짐 방지
    """
    from langchain_core.prompts import ChatPromptTemplate
    chart_prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            prompt + "\n\n"
            +chart_generator_system_prompt
        ),
        MessagesPlaceholder(variable_name="messages")
    ])

    # Chart Generator Agent 생성
    from langgraph.prebuilt import create_react_agent
    chart_agent = create_react_agent(
        llm,
        [python_repl_tool],
        prompt=chart_prompt,
    )

    result = chart_agent.invoke(state)

    # 마지막 메시지를 HumanMessage 로 변환
    last_message = HumanMessage(
        content=result["messages"][-1].content, name="chart_generator"
    )
    return {
        # share internal message history of chart agent with other agents
        "messages": [last_message],
    }


# Research Agent 노드 정의
def research_node(state: MessagesState) -> MessagesState:
    from langchain_openai import ChatOpenAI
    llm = ChatOpenAI(model="gpt-5.1")

    tavily_tool = TavilySearch(max_results=5)
    # Research Agent 생성
    from langgraph.prebuilt import create_react_agent

    from langchain_core.prompts import ChatPromptTemplate

    prompt_re ="""
        CRITICAL: You are NOT allowed to output FINAL ANSWER.
        CRITICAL: Do NOT provide plotting code.
        Your only job is to find and return a clean table of (year, value) with source notes.
        End your message with the token: DATA_READY
    """
    research_prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            prompt_re + "\n\n"
            "You can only do research. You are working with a chart generator colleague. CRITICAL: Do NOT provide plotting code."
        ),
        MessagesPlaceholder(variable_name="messages")
    ])
    research_agent = create_react_agent(
        llm,
        tools=[tavily_tool],
        prompt=research_prompt,
    )

    result = research_agent.invoke(state)

    # 마지막 메시지를 HumanMessage 로 변환
    last_message = HumanMessage(
        content=result["messages"][-1].content, name="researcher"
    )
    return {
        # Research Agent 의 메시지 목록 반환
        "messages": [last_message],
    }
def coder_agent () :
    from langchain_openai import ChatOpenAI
    llm = ChatOpenAI(model="gpt-5.1")

    chart_generator_system_prompt = """
  Be sure to use the following font in your code for visualization.
    
    ##### 폰트 설정 #####
    import platform
    
    # OS 판단
    current_os = platform.system()
    
    if current_os == "Windows":
        # Windows 환경 폰트 설정
        font_path = "C:/Windows/Fonts/malgun.ttf"  # 맑은 고딕 폰트 경로
        fontprop = fm.FontProperties(fname=font_path, size=12)
        plt.rc("font", family=fontprop.get_name())
    elif current_os == "Darwin":  # macOS
        # Mac 환경 폰트 설정
        plt.rcParams["font.family"] = "AppleGothic"
    else:  # Linux 등 기타 OS
        # 기본 한글 폰트 설정 시도
        try:
            plt.rcParams["font.family"] = "NanumGothic"
        except:
            print("한글 폰트를 찾을 수 없습니다. 시스템 기본 폰트를 사용합니다.")
    
    ##### 마이너스 폰트 깨짐 방지 #####
    plt.rcParams["axes.unicode_minus"] = False  # 마이너스 폰트 깨짐 방지
    """
    from langchain_core.prompts import ChatPromptTemplate
    chart_prompt = ChatPromptTemplate.from_messages([
        ("system",chart_generator_system_prompt ),
        MessagesPlaceholder(variable_name="messages")
    ])

    # Chart Generator Agent 생성
    from langgraph.prebuilt import create_react_agent
    chart_agent = create_react_agent(
        llm,
        [python_repl_tool],
        prompt=chart_prompt,
    )

    return chart_agent


# Research Agent 노드 정의
def research_agent() :
    from langchain_openai import ChatOpenAI
    llm = ChatOpenAI(model="gpt-5.1")

    tavily_tool = TavilySearch(max_results=5)
    # Research Agent 생성
    from langgraph.prebuilt import create_react_agent
    research_prompt = """
        You are a specialized Research Agent.
    
        Your ONLY responsibility is to perform information retrieval using the provided search tool.
    
        STRICT RULES:
        1. You must ONLY perform web searches.
        2. Do NOT generate code.
        3. Do NOT analyze, summarize, or reason about the results.
        4. Do NOT answer the user's question directly.
        5. Do NOT make decisions.
        6. Do NOT create any additional content beyond the raw search results.
        7. Your job ends immediately after retrieving information.
    
        Other agents in the system will handle reasoning, coding, and decision-making.
    
        Return ONLY the information obtained from the search tool AS-IS.
    """
    chart_prompt = ChatPromptTemplate.from_messages([
        ("system", research_prompt),
        MessagesPlaceholder(variable_name="messages")
    ])

    research_agent = create_react_agent(
        llm,
        tools=[tavily_tool],
        prompt=chart_prompt
    )

    return research_agent



def agent_node(state,agent,names):
    agent_response = agent.invoke(state)
    return {
        "messages" :[
            HumanMessage(content=agent_response["messages"][-1].content,name=names)
        ]
    }


# 시스템 프롬프트 정의: 작업자 간의 대화를 관리하는 감독자 역할
system_prompt = (
    "You are a supervisor tasked with managing a conversation between the"
    " following workers:  {members}. Given the following user request,"
    " respond with the worker to act next. Each worker will perform a"
    " task and respond with their results and status. When finished,"
    " respond with FINISH."
)

# ChatPromptTemplate 생성
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
        (
            "system",
            "Given the conversation above, who should act next? "
            "Or should we FINISH? Select one of: {options}",
        ),
    ]
).partial(options=str(options_for_next), members=", ".join(members))

def supervisor_agent(state):
    from langchain_openai import ChatOpenAI
    llm = ChatOpenAI(model="gpt-5.1",temperature=0.0)
    supervisor_chain = prompt|llm.with_structured_output(RouteResponse)

    return supervisor_chain.invoke(state)
