from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic.v1 import BaseModel, Field

from app.domain.llm.services.llm_client import LlmClient

system =  """
You a question re-writer that converts an input question to a better version that is optimized \n 
for vectorstore retrieval. Look at the input and try to reason about the underlying semantic intent / meaning.
"""
class VectorQueryRewriter(BaseModel):
    query: str = Field(
        description="rewrite query"
    )

    @staticmethod
    def chain():
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        structured_llm_grader = llm.with_structured_output(VectorQueryRewriter)
        re_write_prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system),
                (
                    "human",
                    "Here is the initial question: \n\n {question} \n Formulate an improved question.",
                ),
            ]
        )

        return re_write_prompt | structured_llm_grader



