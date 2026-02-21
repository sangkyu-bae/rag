from fastapi import UploadFile
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import END
from langgraph.graph import StateGraph
from langgraph.prebuilt import create_react_agent

from app.application.nodes.test_node import supervisor_agent
from app.graph.nodes.analysis_node import DataAnalysis
from app.graph.util.graph import run_graph
from app.infrastructure.node import agent_factory
from app.infrastructure.node.agent_factory import AgentFactory
from app.service.state.analysis_state import AnalysisState
from app.service.supervisor.team_superviosr import create_team_supervisor, get_next_node


class AnalysisWorkFlow:
    def __init__(self):
        pass

    def create_work_flow(self,query,file:UploadFile):


        llm = ChatOpenAI(model="gpt-4o")
        agent_factory = AgentFactory(llm)
        data_analysis =  DataAnalysis(analysis_file=file)
        excel_data_analysis_agent = create_react_agent(llm,tools=[data_analysis])
        # excel_data_analysis_agent =data_analysis

        excel_data_analysis_node = agent_factory.create_agent_node(agent = excel_data_analysis_agent,name = "ExcelAnalysis")

        supervisor_agent = create_team_supervisor(
            llm,
        """
                You are a supervisor managing a Data Analysis Team.

                Available worker:
                - ExcelAnalysis:
                    A professional data analyst capable of:
                    - Performing statistical analysis
                    - Generating summaries and insights
                    - Creating charts and visualizations
                    - Preparing structured analytical outputs
                
                Decision Rules:
                
                1. If the user request involves:
                   - Any type of numeric analysis
                   - Data filtering or grouping
                   - KPI calculation
                   - Trend or comparison analysis
                   - Chart or visualization generation
                   → Respond with: ExcelAnalysis
                
                2. If the analysis is complete and a final answer has already been generated
                   → Respond with: FINISH
                
                Respond with only one of:
                ["ExcelAnalysis", "FINISH"]
            """,
            ["ExcelAnalysis"]
        )

        analysis_graph = StateGraph(AnalysisState)
        analysis_graph.add_node("ExcelAnalysis",excel_data_analysis_node)
        analysis_graph.add_node("Supervisor",supervisor_agent)

        analysis_graph.add_edge("ExcelAnalysis","Supervisor")
        analysis_graph.add_conditional_edges(
            "Supervisor",
            get_next_node,
            {
                "ExcelAnalysis":"ExcelAnalysis",
                "FINISH":END
            }
        )

        analysis_graph.set_entry_point("Supervisor")
        app = analysis_graph.compile(checkpointer=MemorySaver())

        # output = run_graph(app,query)
        #
        # print(output["messages"][-1].content)

        return app