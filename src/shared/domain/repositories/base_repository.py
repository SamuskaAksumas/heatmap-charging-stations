"""
Base Repository Interface following the Repository Pattern.

Defines the contract that all repository implementations must follow,
enabling dependency inversion and testability.
"""
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List

T = TypeVar('T')  # Entity type
ID = TypeVar('ID')  # ID type


class BaseRepository(ABC, Generic[T, ID]):
    """
    Abstract base repository defining the interface for data persistence.

    This interface follows the Repository Pattern from DDD, which:
    - Abstracts data storage from the domain layer
    - Enables dependency inversion (domain depends on abstraction, not implementation)
    - Facilitates testing with mock/fake implementations

    Type Parameters:
        T: The entity type this repository manages.
        ID: The identifier type for the entity.

    Implementing classes must provide concrete implementations for all methods.

    Example:
        >>> class UserRepository(BaseRepository[User, int]):
        ...     def get_by_id(self, id: int) -> Optional[User]:
        ...         return self._storage.get(id)
    """

    @abstractmethod
    def get_by_id(self, id: ID) -> Optional[T]:
        """
        Retrieve an entity by its unique identifier.

        Args:
            id: The unique identifier of the entity.

        Returns:
            The entity if found, None otherwise.
        """
        pass

    @abstractmethod
    def get_all(self) -> List[T]:
        """
        Retrieve all entities.

        Returns:
            List of all entities in the repository.
        """
        pass

    @abstractmethod
    def save(self, entity: T) -> T:
        """
        Persist an entity (create or update).

        Args:
            entity: The entity to persist.

        Returns:
            The persisted entity (may include generated ID).
        """
        pass

    @abstractmethod
    def delete(self, id: ID) -> bool:
        """
        Remove an entity from the repository.

        Args:
            id: The identifier of the entity to remove.

        Returns:
            True if the entity was deleted, False if not found.
        """
        pass
