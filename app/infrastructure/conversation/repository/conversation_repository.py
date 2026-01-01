from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.conversation import Conversation

class ConversationRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def save(self, session_id: str, role: str, content: str) -> Conversation:
        conv = Conversation(
            session_id=session_id,
            role=role,
            content=content,
        )
        self.db.add(conv)
        await self.db.commit()
        return conv

    async def find_by_session(self, session_id: str) -> list[Conversation]:
        stmt = (
            select(Conversation)
            .where(Conversation.session_id == session_id)
            .order_by(Conversation.created_at)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()
