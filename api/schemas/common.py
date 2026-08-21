from typing import Any, Optional
from fastapi import status
from pydantic import BaseModel


class ReturnJSON(BaseModel):
    message: str
    data: Optional[Any] = None
    status: Optional[int] = None
