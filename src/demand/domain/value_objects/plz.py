from dataclasses import dataclass

@dataclass(frozen=True)
class PLZ:
    """Value Object representing a German postal code (Postleitzahl)."""
    code: str
    
    def __post_init__(self):
        """Validate PLZ format (German standard)."""
        # Ensure we handle numeric input by converting to string
        str_code = str(self.code).strip()
        if not str_code.isdigit() or len(str_code) != 5:
            raise ValueError(f"Invalid PLZ: {self.code}. Must be exactly 5 digits.")
        # Re-assigning to ensure it's stored as a clean string
        object.__setattr__(self, 'code', str_code)
    
    def __str__(self) -> str:
        return self.code