"""
Base Domain Event class following DDD principles.

Domain Events capture things that happen in the domain that domain experts care about.
They are immutable and contain all relevant data about what happened.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid


@dataclass(frozen=True)
class DomainEvent:
    """
    Base class for all domain events.

    Domain events are immutable records of something that happened in the domain.
    They are used to communicate between bounded contexts and for event sourcing.

    Attributes:
        event_id: Unique identifier for this event instance.
        timestamp: When the event occurred (ISO format).
        event_type: Type name of the event (auto-derived from class name).

    Example:
        >>> event = DomainEvent()
        >>> print(event.event_type)
        'DomainEvent'
    """
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    @property
    def event_type(self) -> str:
        """Return the type name of this event."""
        return self.__class__.__name__

    def to_dict(self) -> dict:
        """
        Convert event to dictionary for serialization.

        Returns:
            Dictionary representation of the event.
        """
        return {
            'event_id': self.event_id,
            'event_type': self.event_type,
            'timestamp': self.timestamp,
        }
