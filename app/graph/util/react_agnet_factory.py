from typing import TypedDict, List

from langchain_core.tools import BaseTool
from langgraph.prebuilt import create_react_agent


class AgentConfig(TypedDict):
    name:str
    tools:List[BaseTool]
    system_prompt:str

class ReactAgentFactory:
    def __init__(self, llm):
        self.llm = llm

    def create_agent(self, config: AgentConfig):
        return create_react_agent(
            self.llm,
            tools=config["tools"],
            state_modifier=config["system_prompt"]
        )