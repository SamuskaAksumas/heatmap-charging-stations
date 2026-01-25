from abc import ABC

class ValueObject(ABC):
    """
    Base class for all Value Objects in the domain.
    
    - Implements value-based equality (__eq__) and hashing (__hash__).
    - Ensures that two Value Objects are equal if all their fields are equal.
    - Immutable objects should extend this class.
    """
    
    def __eq__(self, other):
        return isinstance(other, ValueObject) and self.__dict__ == other.__dict__

    def __hash__(self):
        # Sort items to ensure consistent hash independent of dictionary ordering
        return hash(tuple(sorted(self.__dict__.items())))
