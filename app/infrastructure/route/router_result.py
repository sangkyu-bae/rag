from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel
from typing import List

class RouterResult(BaseModel):
    tools: List[str]
    reason: str


