from pydantic import BaseModel


class VizItem(BaseModel):
    input_text: str
