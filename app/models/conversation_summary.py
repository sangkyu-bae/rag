from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.db.database import Base

class ConversationSummary(Base):
    __tablename__ = "conversation_summaries"

    id = Column(Integer, primary_key=True)
    session_id = Column(String(100), unique=True, index=True)
    summary = Column(Text)
    last_message_id = Column(Integer)
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
    )
