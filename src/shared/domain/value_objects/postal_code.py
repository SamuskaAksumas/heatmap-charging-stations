"""PostalCode Value Object - Immutable, self-validating Berlin PLZ."""
from dataclasses import dataclass


@dataclass(frozen=True)
class PostalCode:
    """Berlin postal code (10000-14200). Immutable and self-validating."""
    value: str

    def __post_init__(self) -> None:
        if not self._is_valid():
            raise ValueError(f"Invalid postal code: {self.value}")

    def _is_valid(self) -> bool:
        """Check if PLZ is valid for Berlin (5 digits, 10000-14200)."""
        if not self.value or len(self.value) != 5 or not self.value.isdigit():
            return False
        return 10000 <= int(self.value) <= 14200

    def __str__(self) -> str:
        return self.value
