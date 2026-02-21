from langchain_core.tools import BaseTool
from pydantic import Field, BaseModel
from starlette.datastructures import UploadFile

from app.infrastructure.parser.execle.processor import ask


class DataAnalysisInput(BaseModel):
    """Inpout for the excel analysis tool"""
    query : str = Field(description="데이터 분석 쿼리")

class DataAnalysis(BaseTool):
    name:str = "excel_data_analysis"
    # description: str = """
    #     Analyze and interpret structured data from an uploaded Excel file using Pandas.
    #
    #     Use this tool when:
    #     - The user asks about numerical summaries, aggregations, statistics, or trends in tabular data
    #     - The question refers to rows, columns, months, categories, totals, averages, ratios, ranking, filtering, or grouping
    #     - The user wants insights derived from a dataset rather than external knowledge
    #     - The question requires calculations from the provided Excel file
    #
    #     Capabilities:
    #     - Perform filtering, grouping, aggregation (sum, mean, count, ratio, percentage)
    #     - Compare time periods or categories
    #     - Detect trends or anomalies in data
    #     - Generate descriptive statistical summaries
    #     - Create visualization code when necessary
    #
    #     Input:
    #     - A natural language question describing the analysis to perform on the dataset
    #
    #     Do NOT use this tool when:
    #     - The question requires web search or general knowledge
    #     - The answer does not depend on the uploaded dataset
    #     - The question is about company documents or text documents (use vector search instead)
    #
    #     This tool only analyzes the currently uploaded Excel dataset.
    # """
    description :str= """
        This tool is a data analysis execution endpoint.

        You MUST call this tool whenever the user's question requires analyzing the uploaded Excel dataset.
        
        Do not attempt to analyze the data yourself.
        Do not answer from general knowledge.
        Do not summarize or reason about the dataset in the response.
        
        Your role is only to forward the user's question to this tool.
        
        The tool internally performs the full Pandas analysis and returns the final result.
        
        Trigger conditions:
        - Any question about the uploaded Excel data
        - Any request involving numbers, totals, statistics, trends, comparisons, filters, rankings, or calculations from the dataset
        
        Never answer directly when the dataset is required.
        Always call the tool.
    """

    args_schema : type[BaseModel] = DataAnalysisInput
    analysis_file : UploadFile  =Field(default=None,exclude = True)
    class Config:
        arbitrary_types_allowed = True

    def __init(self,file:UploadFile):
        self.analysis_file = file

    def _run(self,query:str):
        return self.search(query)
    # def _run(self,state):
    #     return self.search(state["first_query"])

    def search(self,query:str):
         return ask(self.analysis_file,query)
