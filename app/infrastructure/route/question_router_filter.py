from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import BasePromptTemplate, PromptTemplate, ChatPromptTemplate
from langchain_core.runnables import Runnable
from typing import List, Optional, Dict, Callable
from pydantic import BaseModel, ConfigDict

from app.domain.llm.prompt.prompt_registry import PromptRegistry
from app.infrastructure.langchain.langsmith import langsmith
from app.infrastructure.route.router_result import RouterResult


def default_get_input(query:str)-> Dict[str,str]:
    return {"question": query}

class QuestionRouterFilter(BaseModel):
    router_chain:Runnable
    get_input: Callable[[str], dict] = default_get_input
    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )

    def execute(self,question):
        langsmith("router")
        _input = self.get_input(question)
        return self.router_chain.invoke(_input)

    @classmethod
    def form_question_router_llm(cls,
                                 llm,
                                 prompt:Optional[BasePromptTemplate]=None)->"QuestionRouterFilter":

        if prompt is None:
            prompt_template = PromptRegistry.question_router_prompt()
            _prompt = ChatPromptTemplate.from_messages([
                ("system", prompt_template["system"]),
                ("human", prompt_template["human"]),
            ])
        else:
            _prompt = PromptTemplate.from_template(prompt)

        parser = PydanticOutputParser(pydantic_object=RouterResult)
        router_chain = _prompt | llm | parser
        return cls(router_chain=router_chain)


