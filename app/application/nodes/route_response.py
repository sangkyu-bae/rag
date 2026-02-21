from typing import Literal

from pydantic import BaseModel


members = ["Researcher","Coder"]
options_for_next = ["FINISH"] + members
class RouteResponse(BaseModel):
    next: Literal[*options_for_next]
