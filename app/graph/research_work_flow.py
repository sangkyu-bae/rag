
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import END
from langgraph.graph import StateGraph
from langgraph.prebuilt import create_react_agent

from app.graph.util.graph import run_graph
from app.graph.util.react_agnet_factory import AgentConfig, ReactAgentFactory
from app.infrastructure.node.agent_factory import AgentFactory
from app.infrastructure.vector_store.qdrant.vector_search import VectorSearch
from app.service.state.research_state import ResearchState
from app.service.supervisor.team_superviosr import create_team_supervisor, get_next_node
from app.service.tool.tool_executor import ToolExecutor
from app.service.tool.vector_db_tool import VectorDBTool
from app.service.tool.web_search.tavil_search import TavilySearch

RESEARCH_AGENT: AgentConfig = {
    "name": "Researcher",
    "system_prompt": "You are a research specialist. Search and collect information.",
    # "tools": [tavily_tool, vector_tool],
}

class ResearchWorkFlow:
    # def __init__(self, config: RunnableConfig,nodes):
    #     self.config = config
    #     self.nodes = nodes

    def __init__(self):
        pass

    def create_work_flow(self,query):
        tavily_tool = TavilySearch(max_results=5)
        vector_tool: ToolExecutor = VectorDBTool(collection="test")
        vector = VectorSearch(vector_db=vector_tool)

        # llm = ChatOpenAI(model="gpt-4o-mini")
        llm = ChatOpenAI(model="gpt-5o-mini")
        agent_factory = AgentFactory(llm)

        web_search_agent  = create_react_agent(llm,tools=[tavily_tool])
        web_search_node = agent_factory.create_agent_node(agent =web_search_agent,name="WebSearcher")

        vector_search_agent = create_react_agent(llm,tools=[vector])
        vector_search_node = agent_factory.create_agent_node(agent =vector_search_agent,name="VectorSearcher")

        supervisor_agent = create_team_supervisor(
            llm,
            "You are a supervisor tasked with managing a conversation between the"
            " following workers: WebSearcher,VectorSearcher. Given the following user request,"
            " respond with the worker to act next. Each worker will perform a"
            " task and respond with their results and status. When finished,"
            """
                Routing Rules:
                
              1) ALWAYS choose VectorSearcher ONLY if:
               - The question clearly refers to company-internal systems,
               - proprietary documents,
               - internal app names (e.g., 크크크앱),
               - deployment guides,
               - internal financial reports.
            
            2) ALWAYS choose WebSearcher if the question refers to:
               - current or recent financial market data (e.g., call rate, interest rates, exchange rate)
               - macroeconomic indicators
               - stock prices
               - economic statistics
               - public financial metrics
            
            3) If the information is time-sensitive (e.g., "전월", "최근", "현재"),
               ALWAYS prefer WebSearcher.
            """
            " respond with FINISH.",
            ["WebSearcher","VectorSearcher"],
        )

        research_graph = StateGraph(ResearchState)
        research_graph.add_node("WebSearcher", web_search_node)
        research_graph.add_node("VectorSearcher", vector_search_node)
        research_graph.add_node("Supervisor", supervisor_agent)

        research_graph.add_edge("WebSearcher", "Supervisor")
        research_graph.add_edge("VectorSearcher", "Supervisor")

        research_graph.add_conditional_edges(
            "Supervisor",
            get_next_node,
            {
                "WebSearcher": "WebSearcher",
                "VectorSearcher":"VectorSearcher",
                 "FINISH": END
            },
        )

        research_graph.set_entry_point("Supervisor")
        app = research_graph.compile(checkpointer=MemorySaver())  # 🔥 이거 필수

        # output = run_graph(app,query)
        #
        # print(output["messages"][-1].content)

        return app


        # RESEARCH_AGENT["tools"] = [tavily_tool, vector]

        #
        # agent = ReactAgentFactory(llm)
        #
        # research_agent = agent.create_agent(RESEARCH_AGENT)
        # node = AgentFactory(llm).create_agent_node(
        #     research_agent
        # )


