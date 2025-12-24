from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class ChargingSuggestion:
    plz: str
    address: str
    reason: str
    id: Optional[int] = None
    timestamp: str = datetime.now().isoformat()
    status: str = 'pending'