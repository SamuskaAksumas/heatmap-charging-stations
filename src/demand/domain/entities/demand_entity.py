from dataclasses import dataclass

from src.shared.domain.entities.entity import Entity
from src.demand.domain.value_objects.plz import PLZ
from src.demand.domain.value_objects.demand_score import DemandScore


@dataclass(eq=False)
class DemandEntity(Entity):
    """
    Entity representing demand for a specific PLZ.

    Identity is defined by the PLZ value object.
    """
    plz: PLZ
    score: DemandScore

    def __post_init__(self) -> None:
        # Enforce basic invariants
        if self.plz is None:
            raise ValueError("PLZ must be provided")
        if self.score is None:
            raise ValueError("DemandScore must be provided")

    @property
    def identity(self) -> str:
        """
        Entity identity used for equality comparison.
        """
        return self.plz.code
