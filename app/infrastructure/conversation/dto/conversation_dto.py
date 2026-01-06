from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ConversationDTO(BaseModel):
    user_id: str
    session_id: str
    content: str
    role: str
    next_seq: Optional[int] = None
    created_at: Optional[datetime] = None
