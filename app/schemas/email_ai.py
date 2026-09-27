from pydantic import BaseModel
from typing import List, Literal


class EmailSummary(BaseModel):
    summary: List[str]
    actions: List[str]
    urgency: Literal["low", "medium", "high"]
    sentiment: Literal["positive", "neutral", "negative", "angry"]
    intent: str
