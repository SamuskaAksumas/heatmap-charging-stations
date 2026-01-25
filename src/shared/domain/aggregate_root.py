from abc import ABC
from typing import List
from src.shared.domain.entity import Entity


class AggregateRoot(Entity, ABC):
    """
    Base class for all Aggregate Roots.

    Responsibilities:
    - Identity
    - Invariant enforcement
    - Domain event collection
    """

    def __init__(self, aggregate_id: str):
        super().__init__(aggregate_id)
        self._domain_events: List[object] = []

    # ---- Domain Events ----
    def _add_domain_event(self, event: object) -> None:
        self._domain_events.append(event)

    def pull_domain_events(self) -> List[object]:
        """
        Returns and clears domain events.
        Called by application layer.
        """
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events
    
    @property
    def aggregate_id(self):
        """Alias for the ID stored in Entity."""
        return self.id  # or self._id depending on Entity

