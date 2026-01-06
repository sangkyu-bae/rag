from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.db.database import Base
from app.infrastructure.conversation.dto.conversation_dto import ConversationDTO


class Conversation(Base):
    __tablename__ = "conversation"

    id = Column(Integer, primary_key=True)
    session_id = Column(String(100), index=True)
    seq_id = Column(String(100))
    role = Column(String(20))
    user_id = Column(String(100), index=True)
    content = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

    @classmethod
    def from_conversation_dto(cls, conversation_dto: ConversationDTO):
        cls(
            session_id=conversation_dto.session_id,
            role = conversation_dto.role,
            user_id = conversation_dto.user_id,
            content = conversation_dto.content,
        )