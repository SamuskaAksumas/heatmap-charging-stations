"""Domain exceptions for the Shared bounded context."""
from .domain_exception import DomainException
from .invalid_postal_code_exception import InvalidPostalCodeException

__all__ = ["DomainException", "InvalidPostalCodeException"]
