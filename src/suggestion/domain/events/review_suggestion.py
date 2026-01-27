from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class ReviewSuggestion:
    """Domain Event: A suggestion status transition has occurred."""
    suggestion_id: int
    new_status: str
    reviewer: str
    occurred_at: datetime = datetime.now()