"""Unit tests for UserAge entity."""

import pytest
from age_average.domain.user_age import UserAge


class TestUserAge:
    """Test suite for UserAge entity."""

    def test_create_valid_user_age(self):
        """Test creating UserAge with valid data."""
        user_age = UserAge(user_id=1, age=25)

        assert user_age.user_id == 1
        assert user_age.age == 25

    def test_user_age_is_immutable(self):
        """Test that UserAge instances are immutable (frozen dataclass)."""
        user_age = UserAge(user_id=1, age=25)

        with pytest.raises(AttributeError):
            user_age.user_id = 2

        with pytest.raises(AttributeError):
            user_age.age = 30

    def test_user_age_equality(self):
        """Test that UserAge instances with same data are equal."""
        user_age1 = UserAge(user_id=1, age=25)
        user_age2 = UserAge(user_id=1, age=25)
        user_age3 = UserAge(user_id=2, age=25)

        assert user_age1 == user_age2
        assert user_age1 != user_age3

    def test_user_age_hash(self):
        """Test that UserAge instances can be used in sets and as dict keys."""
        user_age1 = UserAge(user_id=1, age=25)
        user_age2 = UserAge(user_id=1, age=25)
        user_age3 = UserAge(user_id=2, age=30)

        # Test set behavior
        user_set = {user_age1, user_age2, user_age3}
        assert len(user_set) == 2  # user_age1 and user_age2 are equal

        # Test dict key behavior
        user_dict = {user_age1: "value1", user_age3: "value2"}
        assert user_dict[user_age2] == "value1"  # user_age2 equals user_age1

    def test_invalid_negative_user_id(self):
        """Test that negative user_id raises ValueError."""
        with pytest.raises(ValueError, match="user_id must be non-negative"):
            UserAge(user_id=-1, age=25)

    def test_invalid_negative_age(self):
        """Test that negative age raises ValueError."""
        with pytest.raises(ValueError, match="age must be non-negative"):
            UserAge(user_id=1, age=-5)

    def test_zero_values_allowed(self):
        """Test that zero values are allowed for both user_id and age."""
        user_age = UserAge(user_id=0, age=0)

        assert user_age.user_id == 0
        assert user_age.age == 0

    def test_create_method(self):
        """Test the static create method."""
        user_age = UserAge.create(user_id=1, age=25)

        assert user_age.user_id == 1
        assert user_age.age == 25
        assert isinstance(user_age, UserAge)

    def test_create_method_validation(self):
        """Test that create method validates input parameters."""
        with pytest.raises(ValueError, match="user_id must be non-negative"):
            UserAge.create(user_id=-1, age=25)

        with pytest.raises(ValueError, match="age must be non-negative"):
            UserAge.create(user_id=1, age=-5)