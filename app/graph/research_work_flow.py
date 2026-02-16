
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
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

        llm = ChatOpenAI(model="gpt-4o-mini")
        agent_factory = AgentFactory(llm)

        search_agent  = create_react_agent(llm,tools=[tavily_tool,vector]
                                         )
        search_node = agent_factory.create_agent_node(agent =search_agent,name="Searcher")

        supervisor_agent = create_team_supervisor(
            llm,
            "You are a supervisor tasked with managing a conversation between the"
            " following workers: Search. Given the following user request,"
            " respond with the worker to act next. Each worker will perform a"
            " task and respond with their results and status. When finished,"
            " respond with FINISH.",
            ["Searcher"],
        )

        research_graph = StateGraph(ResearchState)
        research_graph.add_node("Searcher", search_node)
        research_graph.add_node("Supervisor", supervisor_agent)

        research_graph.add_edge("Searcher", "Supervisor")

        research_graph.add_conditional_edges(
            "Supervisor",
            get_next_node,
            {"Searcher": "Searcher", "FINISH": END},
        )

        research_graph.set_entry_point("Supervisor")
        app = research_graph.compile()  # 🔥 이거 필수
        output = run_graph(app,query)

        print(output["messages"][-1].content)

        # RESEARCH_AGENT["tools"] = [tavily_tool, vector]

        #
        # agent = ReactAgentFactory(llm)
        #
        # research_agent = agent.create_agent(RESEARCH_AGENT)
        # node = AgentFactory(llm).create_agent_node(
        #     research_agent
        # )


