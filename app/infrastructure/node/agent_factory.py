from langchain_core.messages import HumanMessage


class AgentFactory:
    def __init__(self,model):
        self.llm = model

    def create_agent_node(self,agent,name:str):
        def agent_node(state):
            result = agent.invoke(state)
            if isinstance(result, str):
                return {
                    "messages" : [HumanMessage(content=result)]
                }
            else:
                return {
                    "messages" : [
                        HumanMessage(content=result["messages"][-1].content, name=name)
                    ]
                }

        return agent_node