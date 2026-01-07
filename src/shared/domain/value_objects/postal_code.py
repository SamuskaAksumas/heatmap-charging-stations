"""
Value Object: PostalCode (PLZ)

A Value Object is immutable and validates itself upon creation.
This follows DDD principles as shown in the TDD assignment (Figure 5).
"""
from dataclasses import dataclass


@dataclass(frozen=True)  # frozen=True makes it immutable
class PostalCode:
    """
    Value Object representing a Berlin postal code (PLZ).

    Attributes:
        value: The postal code string (5 digits, Berlin range 10000-14200)

    Raises:
        ValueError: If the postal code is invalid

    Example:
        >>> plz = PostalCode("10115")  # Valid
        >>> plz = PostalCode("99999")  # Raises ValueError
    """
    value: str

    def __post_init__(self) -> None:
        """Validate the postal code upon creation."""
        if not self._is_valid():
            raise ValueError(f"Invalid postal code: {self.value}")

    def _is_valid(self) -> bool:
        """
        Check if the postal code is valid for Berlin.

        Returns:
            bool: True if valid, False otherwise
        """
        # Must be exactly 5 digits
        if not self.value or len(self.value) != 5:
            return False

        if not self.value.isdigit():
            return False

        # Berlin postal codes range from 10000 to 14200
        plz_int = int(self.value)
        return 10000 <= plz_int <= 14200

    def __str__(self) -> str:
        """Return the postal code as string."""
        return self.value
