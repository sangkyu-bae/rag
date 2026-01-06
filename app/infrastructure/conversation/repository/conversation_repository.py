from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text

from app.infrastructure.conversation.dto.conversation_dto import ConversationDTO
from app.models.conversation import Conversation

class ConversationRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def save(self,
                   request_conversation:ConversationDTO
                   ):
        result = await self.db.execute(
            text("""
                 SELECT COALESCE(MAX(seq_id), 0) + 1
                 FROM conversation
                 WHERE user_id = :user_id
                   AND session_id = :session_id
                     FOR UPDATE
                 """),
            {"user_id": request_conversation.user_id, "session_id": request_conversation.session_id},
        )

        next_seq = result.scalar_one()
        conv :Conversation = Conversation.from_conversation_dto(request_conversation)
        conv.seq_id = next_seq
        self.db.add(conv)
        await self.db.commit()
        return conv


    async def save(self,
                   session_id: str,
                   user_id: str,
                   role: str,
                   content: str) -> Conversation:
        result = await self.db.execute(
            text("""
                 SELECT COALESCE(MAX(seq_id), 0) + 1
                 FROM conversation
                 WHERE user_id = :user_id
                   AND session_id = :session_id
                     FOR UPDATE
                 """),
            {"user_id": user_id, "session_id": session_id},
        )

        next_seq = result.scalar_one()

        conv = Conversation(
            session_id=session_id,
            role=role,
            user_id=user_id,
            content=content,
            seq_id=next_seq
        )
        self.db.add(conv)
        await self.db.commit()
        return conv

    async def find_by_session(self, session_id: str) -> list[Conversation]:
        stmt = (
            select(Conversation)
            .where(Conversation.session_id == session_id )
            .order_by(Conversation.seq_id)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def find_by_session_and_top_k(
            self,
            session_id: str,
            top_k: int = 4,
    ) -> list[Conversation]:
        stmt = (
            select(Conversation)
            .where(Conversation.session_id == session_id)
            .order_by(Conversation.seq_id.desc())
            .limit(top_k)
        )
        result = await self.db.execute(stmt)
        conversations = result.scalars().all()

        # LLM에 넣기 전에 순서 복원
        return list(reversed(conversations))
