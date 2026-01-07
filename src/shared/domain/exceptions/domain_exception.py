"""
Base domain exception class.

All domain-specific exceptions should inherit from this class
to allow for centralized exception handling.
"""


class DomainException(Exception):
    """
    Base exception for all domain-level errors.

    Provides a common parent class for domain exceptions,
    enabling catch-all handling of domain errors.

    Attributes:
        message: Human-readable error description.
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message
