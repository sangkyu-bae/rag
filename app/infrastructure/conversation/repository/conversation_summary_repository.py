from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.conversation_summary import ConversationSummary

class ConversationSummaryRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def save(self, session_id: str, summary: str, last_message_id: int) -> ConversationSummary:
        conv = ConversationSummary(
            session_id = session_id,
            summary = summary,
            last_message_id = last_message_id
        )
        self.db.add(conv)
        await self.db.commit()
        return conv

    async def update(self, session_id: str, summary: str, last_message_id: int) -> ConversationSummary:
        conv = ConversationSummary(
            session_id = session_id,
            summary = summary,
            last_message_id = last_message_id
        )
        self.db.(conv)
        await self.db.commit()
        return conv

    async def find_by_session(self, session_id: str) -> list[ConversationSummary]:
        stmt = (
            select(ConversationSummary)
            .where(ConversationSummary.session_id == session_id)
            .order_by(ConversationSummary.created_at)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()
