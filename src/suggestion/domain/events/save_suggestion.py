from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class SaveSuggestion:
    """Domain Event: A new suggestion has been successfully persisted."""
    suggestion_id: int
    plz: str
    occurred_at: datetime = datetime.now()