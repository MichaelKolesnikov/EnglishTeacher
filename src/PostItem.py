from pydantic import BaseModel


class PostItem(BaseModel):
    input: str | None = None
    direction: str | None = None
