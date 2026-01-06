# """Shared dependencies for API routes."""
#
# from typing import Generator
#
# from contextlib import contextmanager
#
#
# @contextmanager
# def get_db() -> Generator[None, None, None]:
#     """
#     Dependency placeholder for database session handling.
#
#     Replace this implementation with your actual database session manager.
#     """
#     try:
#         yield
#     finally:
#         # Close DB connection here when a real session is used.
#         ...
#
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.deps import get_db
from app.infrastructure.conversation.repository.conversation_repository import ConversationRepository


def get_conversation_repository(
    db: AsyncSession = Depends(get_db),
) -> ConversationRepository:
    return ConversationRepository(db)