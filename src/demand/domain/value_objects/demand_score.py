from dataclasses import dataclass
import numpy as np

@dataclass(frozen=True)
class DemandScore:
    """Value Object: The business logic for 'what makes a demand score'."""
    value: float

    @classmethod
    def from_raw(cls, residents: int, stations: int) -> 'DemandScore':
        """The actual formula calculation moved from events to here."""
        if stations > 0:
            score = residents / stations
        else:
            score = float(residents)
        
        # Clean data for presentation
        clean_val = 0.0 if np.isnan(score) or np.isinf(score) else score
        return cls(value=clean_val)