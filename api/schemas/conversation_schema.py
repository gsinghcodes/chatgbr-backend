from pydantic import BaseModel


class ConversationPagination(BaseModel):
    page: int
    limit: int
