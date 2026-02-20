from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import END
from langgraph.graph import StateGraph

from app.graph.research_work_flow import ResearchWorkFlow
from app.graph.util.graph import run_graph
from app.service.state.supervisor_state import SupervisorState, get_last_message, join_graph
from app.service.supervisor.team_superviosr import create_team_supervisor, get_next_node


class WorkFlowAdapter:
    def __init__(self):
        pass

    def process(self, query):
        llm = ChatOpenAI(model="gpt-4o")
        supervisor_node = create_team_supervisor(
            llm,
            "You are a supervisor tasked with managing a conversation between the"
            " following teams: ['ResearchTeam']. Given the following user request,"
            " respond with the worker to act next. Each worker will perform a"
            " task and respond with their results and status. When finished,"
            " respond with FINISH.",
            ["ResearchTeam"]
        )

        super_graph = StateGraph(SupervisorState)
        search_work_flow = ResearchWorkFlow()
        research_node = search_work_flow.create_work_flow(query)

        super_graph.add_node("ResearchTeam",get_last_message | research_node | join_graph)
        super_graph.add_node("Supervisor",supervisor_node)

        super_graph.add_conditional_edges(
            "Supervisor",
            get_next_node,
            {
                "ResearchTeam":"ResearchTeam",
                "FINISH": END
            }
        )
        super_graph.set_entry_point("Supervisor")
        super_graph = super_graph.compile(checkpointer=MemorySaver())
        output = run_graph(super_graph,query)

        print(output["messages"][-1].content)





