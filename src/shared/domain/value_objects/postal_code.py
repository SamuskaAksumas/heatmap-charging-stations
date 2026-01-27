"""PostalCode Value Object - Immutable, self-validating Berlin PLZ."""
from dataclasses import dataclass
<<<<<<< HEAD


@dataclass(frozen=True)
class PostalCode:
=======
from src.shared.domain.value_objects.value_object import ValueObject  # <- ADD THIS


@dataclass(frozen=True)
class PostalCode(ValueObject):
>>>>>>> 607d696 (Revamp project structure using DDD approach)
    """Berlin postal code (10000-14200). Immutable and self-validating."""
    value: str

    def __post_init__(self) -> None:
        error = self._validate()
        if error:
            raise ValueError(error)

    def _validate(self) -> str | None:
        """Validate PLZ and return error message if invalid, None if valid."""
        if not self.value or not self.value.strip():
            return "Please enter a postal code"

        stripped = self.value.strip()
        if not stripped.isdigit() or len(stripped) != 5:
            return "Please enter a valid 5-digit postal code"

        plz_int = int(stripped)
        if not (10000 <= plz_int <= 14200):
            return "Please enter a valid Berlin postal code (10000-14200)"

        return None

    def __str__(self) -> str:
        return self.value
