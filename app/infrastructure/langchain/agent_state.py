import operator
from typing import  Sequence, Annotated

from langchain_core.messages import BaseMessage
from typing_extensions import TypedDict

class AgentState(TypedDict):
    # messages : Annotated [
    #     Sequence[BaseMessage],operator.add
    # ]
    messages : Annotated [
        Sequence[BaseMessage],operator.add
    ]
    sender: Annotated[str, "The sender of the last message"]
    next:str