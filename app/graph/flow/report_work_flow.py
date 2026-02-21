
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import END
from langgraph.graph import StateGraph
from langgraph.prebuilt import create_react_agent

from app.graph.nodes.report_node import Report
from app.infrastructure.node.agent_factory import AgentFactory
from app.service.state.research_state import ResearchState
from app.service.supervisor.team_superviosr import create_team_supervisor, get_next_node


class ReportWorkFlow:
    def __init__(self):
        pass

    def create_work_flow(self):
        report_tool = Report()
        llm = ChatOpenAI(model="gpt-4o-mini")
        agent_factory = AgentFactory(llm)
        report_agent  = create_react_agent(llm,tools=[report_tool])
        report_node = agent_factory.create_agent_node(agent=report_agent,name="Report")

        supervisor_agent = create_team_supervisor(
            llm,
            "You are a supervisor tasked with managing a conversation between the"
            " following workers: Report. Given the following user request,"
            " respond with the worker to act next. Each worker will perform a"
            " task and respond with their results and status. When finished,"
            " respond with FINISH.",
            ["Report"],
        )
        report_graph = StateGraph(ResearchState)
        report_graph.add_node("Report", report_node)
        report_graph.add_node("Supervisor", supervisor_agent)

        report_graph.add_conditional_edges(
            "Supervisor",
            get_next_node,
            {
                "Report" :"Report",
                "FINISH": END
            }
        )

        report_graph.set_entry_point("Supervisor")
        app = report_graph.compile(checkpointer=MemorySaver())

        return app