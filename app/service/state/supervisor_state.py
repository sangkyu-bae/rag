import operator
from typing import TypedDict, Annotated, List

from langchain_core.messages import BaseMessage, HumanMessage


class SupervisorState(TypedDict):
    messages:Annotated[List[BaseMessage],operator.add]
    next:str


def get_last_message(state:SupervisorState) -> str:
    last_message = state["messages"][-1]
    if isinstance(last_message, str):
        return {"messages" : [HumanMessage(content=last_message)]}
    else:
        return {"messages" : [last_message.content]}

def join_graph(response:dict):
    return {"messages" : response["messages"]}