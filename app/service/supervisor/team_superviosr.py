from typing import Literal

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from pydantic import BaseModel

from app.application.nodes.route_response import options_for_next


def create_team_supervisor(model,system_prompt,members) -> str:
    options_for_next = ["FINISH"] + members

    class RouteResponse(BaseModel):
        next: Literal[*options_for_next]

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system",system_prompt),
            MessagesPlaceholder(variable_name="messages"),
            (
                "system",
                "Given the conversation above, who should act next? "
                "Or should we FINISH? Select one of: {options}",
            )
        ]
    ).partial(options = str(options_for_next))

    llm = model

    supervisor_chain = prompt | llm.with_structured_output(RouteResponse)

    return supervisor_chain

def get_next_node(x):
    return x["next"]