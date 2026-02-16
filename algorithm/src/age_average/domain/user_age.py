"""User age entity representing a user with their age."""

from dataclasses import dataclass


@dataclass(frozen=True)
class UserAge:
    """
    Entity representing a user with their age.

    This is a simple domain entity that encapsulates user identification
    and age information. The entity is immutable (frozen) to ensure
    data integrity.

    Attributes:
        user_id: Unique identifier for the user
        age: Age of the user in years
    """
    user_id: int
    age: int

    def __post_init__(self):
        """Validate entity invariants after initialization."""
        if self.user_id < 0:
            raise ValueError("user_id must be non-negative")
        if self.age < 0:
            raise ValueError("age must be non-negative")

    @staticmethod
    def create(user_id: int, age: int) -> "UserAge":
        """
        Factory method to create a UserAge instance.

        This static method provides a clear and explicit way to create
        UserAge instances, encapsulating the creation logic.

        Args:
            user_id: Unique identifier for the user
            age: Age of the user in years

        Returns:
            A new UserAge instance

        Raises:
            ValueError: If user_id or age are negative
        """
        return UserAge(user_id=user_id, age=age)
