from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import END
from langgraph.graph import StateGraph
from starlette.datastructures import UploadFile

from app.graph.flow.analysis_work_flow import AnalysisWorkFlow
from app.graph.flow.report_work_flow import ReportWorkFlow
from app.graph.research_work_flow import ResearchWorkFlow
from app.graph.util.graph import run_graph
from app.service.state.supervisor_state import SupervisorState, get_last_message, join_graph
from app.service.supervisor.team_superviosr import create_team_supervisor, get_next_node


class WorkFlowAdapter:
    def __init__(self):
        pass

    def process(self, query, file:UploadFile):
        llm = ChatOpenAI(model="gpt-4o")
        # supervisor_node = create_team_supervisor(
        #     llm,
        #     "You are a supervisor tasked with managing a conversation between the"
        #     " following teams: ['AnalysisTeam','ReportTeam','ResearchTeam']. Given the following user request,"
        #     " respond with the worker to act next. Each worker will perform a"
        #     " task and respond with their results and status. When finished,"
        #     " respond with FINISH.",
        #     ["ResearchTeam","AnalysisTeam","ReportTeam"]
        #     # ["AnalysisTeam","ReportTeam"]
        # )

        supervisor_node = create_team_supervisor(
            llm,
           """
           You are a strict workflow supervisor managing the following teams:
            ['AnalysisTeam','ReportTeam','ResearchTeam'].
            
            Your job is to select the SINGLE next team to act.
            
            You MUST follow these routing rules strictly.
            
            -------------------------------------------------
            STATE-AWARE ROUTING LOGIC
            -------------------------------------------------
            
            You MUST examine the conversation history carefully.
            
            ReportTeam can ONLY be selected if:
            - AnalysisTeam OR ResearchTeam has already produced results
            - AND those results exist in the conversation history
            - AND the user is requesting a structured report or summary based on those results
            
            If no prior team results exist, you MUST NOT choose ReportTeam.
            
            -------------------------------------------------
            ROUTING RULES
            -------------------------------------------------
            
            1) If the user request requires numerical analysis, aggregation,
               statistics, or structured data operations (Excel, DataFrame),
               → choose AnalysisTeam.
            
            2) If prior analysis/research results already exist AND the user requests:
               - report generation
               - executive summary
               - business document
               - structured report
               → choose ReportTeam.
            
            3) Choose ResearchTeam ONLY if:
               - External information is required
               - Web search is necessary
               - Vector document retrieval is required
               - The question cannot be answered using existing analysis results
            
            4) NEVER choose ReportTeam if:
               - There are no prior AnalysisTeam or ResearchTeam outputs
               - The user directly asks for a report without prior data collection
            
            5) If the final answer is complete, respond with FINISH.
            
            -------------------------------------------------
            
            Be logical and minimal.
            Return ONLY one of:
            ['AnalysisTeam','ReportTeam','ResearchTeam','FINISH']
           """,
            ["ResearchTeam", "AnalysisTeam", "ReportTeam"]
        )

        super_graph = StateGraph(SupervisorState)
        search_work_flow = ResearchWorkFlow()
        research_node = search_work_flow.create_work_flow(query)

        analysis_work_flow = AnalysisWorkFlow()
        analysis_node =  analysis_work_flow.create_work_flow(query,file)

        report_work_flow = ReportWorkFlow()
        report_node = report_work_flow.create_work_flow()



        super_graph.add_node("ResearchTeam",get_last_message | research_node | join_graph)
        super_graph.add_node("AnalysisTeam",get_last_message | analysis_node | join_graph)
        super_graph.add_node("ReportTeam",get_last_message | report_node | join_graph)
        super_graph.add_node("Supervisor",supervisor_node)

        super_graph.add_edge("ResearchTeam", "Supervisor")
        super_graph.add_edge("AnalysisTeam", "Supervisor")
        super_graph.add_edge("ReportTeam", "Supervisor")

        super_graph.add_conditional_edges(
            "Supervisor",
            get_next_node,
            {
                "ResearchTeam":"ResearchTeam",
                "AnalysisTeam":"AnalysisTeam",
                "ReportTeam":"ReportTeam",
                "FINISH": END
            }
        )
        super_graph.set_entry_point("Supervisor")
        super_graph = super_graph.compile(checkpointer=MemorySaver())
        output = run_graph(super_graph,query)

        print(output["messages"][-1].content)





