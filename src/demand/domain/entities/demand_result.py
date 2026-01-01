from dataclasses import dataclass
from typing import Optional, Any

@dataclass
class DemandResult:
    plz: str
    demand: float
    # Add these so the test (and the app) can store the full record
    einwohner: int = 0
    count: int = 0
    geometry: Optional[Any] = None

    @property
    def demand_score(self) -> float:
        """This matches the math used in your tests."""
        return self.einwohner / (self.count + 1)