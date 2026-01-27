from abc import ABC


class Entity(ABC):
    """
    Base class for all domain Entities.

    Entities are defined by their identity, not their attributes.
    """

    def __init__(self, entity_id: str):
        self._id = entity_id

    @property
    def id(self) -> str:
        return self._id

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Entity):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
