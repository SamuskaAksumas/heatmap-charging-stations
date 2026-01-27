from dataclasses import dataclass
from datetime import datetime
from typing import List

@dataclass(frozen=True)
class LoadSuggestion:
    """Domain Event: Suggestions have been loaded from the repository."""
    count: int
    loaded_at: datetime = datetime.now()