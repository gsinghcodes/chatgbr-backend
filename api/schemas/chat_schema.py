from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class ChatRequest(BaseModel):
    question: str
    conversation_id: Optional[UUID] = None
