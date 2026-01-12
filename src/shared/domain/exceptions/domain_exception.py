"""DomainException - Base class for all domain-level errors."""


class DomainException(Exception):
    """Base exception for domain errors. All domain exceptions inherit from this."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message
