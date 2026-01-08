from fastapi import Depends
from langchain_core.messages import HumanMessage, AIMessage

from app.api.deps import get_conversation_repository
from app.infrastructure.conversation.dto.conversation_dto import ConversationDTO
from app.infrastructure.conversation.repository.conversation_repository import ConversationRepository
from app.models.conversation import Conversation


class MultiTurnService:
    def __init__(self, conversation_repository: ConversationRepository):
        self.conversation_repository = conversation_repository

    def save(self, conversation: ConversationDTO):
        self.conversation_repository.save(conversation)

    def find_whit_conversation_by_user_id(self, conversation_id: int) -> Conversation:
        return ""

    def find_whit_conversation_by_session_id(self, session_id: str,top_k:int) -> list[Conversation]:
        return self.conversation_repository.find_by_session_and_top_k(session_id, top_k)

    def to_messages(self,session_id: str,top_k:int):
        # conversations: seq 기준 정렬된 리스트여야 함
        messages = []
        conversations:list[Conversation] = self.conversation_repository.find_by_session_and_top_k(session_id, top_k)


        for c in conversations:
            if c.role == "user":
                messages.append(HumanMessage(content=c.content))
            elif c.role == "answer":
                messages.append(AIMessage(content=c.content))

        return messages

    def save_turn(self,
                  user_id : str,
                  session_id:str,
                  question:str,
                  answer:str
                  ):

        return ""
