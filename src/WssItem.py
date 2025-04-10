from pydantic import BaseModel


class WssItem(BaseModel):
    type: str
    content: str
    timestamp: str
