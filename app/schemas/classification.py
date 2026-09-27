from pydantic import BaseModel

class ClassificationResult(BaseModel):
    is_urgent: bool
    is_spam: bool
    sentiment: str   # positive | negative | neutral
    category: str    # invoice, meeting, support, sales, other
