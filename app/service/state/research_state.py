import operator
from typing import TypedDict,List

from langchain_core.messages import BaseMessage
from typing_extensions import Annotated


class ResearchState(TypedDict):
    messages: Annotated [List[BaseMessage], operator.add]
    team_members: List[str]
    next:str

