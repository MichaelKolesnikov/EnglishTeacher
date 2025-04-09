from pydantic import BaseModel
from typing import Optional


class TextItem(BaseModel):
    """Модель данных для текстового обмена с визуализацией ВТ"""
    input: Optional[str] = None
    direction: Optional[str] = None


class EmotionItem(BaseModel):
    """Модель данных для обмена эмоциями с визуализацией ВТ"""
    direction: Optional[str] = None
