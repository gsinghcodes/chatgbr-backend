from pydantic import BaseModel


class CreateRepositoryRequest(BaseModel):
    clone_url: str
