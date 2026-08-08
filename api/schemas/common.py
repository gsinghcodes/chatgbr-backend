from typing import Any

from pydantic import BaseModel


class ReturnJSON(BaseModel):
    message: str
    data: Any | None = None
