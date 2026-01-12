"""
Tests for PostalCode Value Object.

Following TDD principles:
- Happy Path (valid postal codes)
- Edge Cases (boundary conditions)
- Error Scenarios (invalid inputs)
- Domain Rules (Berlin PLZ range)
"""
import pytest
from src.shared.domain.value_objects.postal_code import PostalCode


class TestPostalCodeHappyPath:
    """Happy Path tests - valid postal codes."""

    def test_valid_berlin_plz_mitte(self) -> None:
        """Test valid Berlin Mitte postal code."""
        plz = PostalCode("10115")
        assert plz.value == "10115"
        assert str(plz) == "10115"

    def test_valid_berlin_plz_kreuzberg(self) -> None:
        """Test valid Berlin Kreuzberg postal code."""
        plz = PostalCode("10999")
        assert plz.value == "10999"

    def test_valid_berlin_plz_spandau(self) -> None:
        """Test valid Berlin Spandau postal code."""
        plz = PostalCode("13597")
        assert plz.value == "13597"


class TestPostalCodeEdgeCases:
    """Edge Case tests - boundary conditions."""

    def test_minimum_berlin_plz(self) -> None:
        """Test minimum valid Berlin postal code (10000)."""
        plz = PostalCode("10000")
        assert plz.value == "10000"

    def test_maximum_berlin_plz(self) -> None:
        """Test maximum valid Berlin postal code (14200)."""
        plz = PostalCode("14200")
        assert plz.value == "14200"

    def test_just_below_minimum_raises(self) -> None:
        """Test postal code just below Berlin range."""
        with pytest.raises(ValueError, match="valid Berlin postal code"):
            PostalCode("09999")

    def test_just_above_maximum_raises(self) -> None:
        """Test postal code just above Berlin range."""
        with pytest.raises(ValueError, match="valid Berlin postal code"):
            PostalCode("14201")


class TestPostalCodeErrorScenarios:
    """Error Scenario tests - invalid inputs."""

    def test_empty_string_raises(self) -> None:
        """Test that empty string raises ValueError."""
        with pytest.raises(ValueError, match="enter a postal code"):
            PostalCode("")

    def test_none_value_raises(self) -> None:
        """Test that None raises ValueError."""
        with pytest.raises(ValueError, match="enter a postal code"):
            PostalCode(None)  # type: ignore

    def test_non_numeric_raises(self) -> None:
        """Test that non-numeric string raises ValueError."""
        with pytest.raises(ValueError, match="valid 5-digit postal code"):
            PostalCode("abcde")

    def test_mixed_alphanumeric_raises(self) -> None:
        """Test that mixed alphanumeric raises ValueError."""
        with pytest.raises(ValueError, match="valid 5-digit postal code"):
            PostalCode("10a15")

    def test_too_short_raises(self) -> None:
        """Test that too short postal code raises ValueError."""
        with pytest.raises(ValueError, match="valid 5-digit postal code"):
            PostalCode("1011")

    def test_too_long_raises(self) -> None:
        """Test that too long postal code raises ValueError."""
        with pytest.raises(ValueError, match="valid 5-digit postal code"):
            PostalCode("101150")

    def test_whitespace_raises(self) -> None:
        """Test that whitespace-padded short code raises ValueError."""
        with pytest.raises(ValueError, match="valid 5-digit postal code"):
            PostalCode("  101")


class TestPostalCodeDomainRules:
    """Domain Rule tests - Berlin-specific constraints."""

    def test_non_berlin_plz_munich_raises(self) -> None:
        """Test that Munich postal code raises ValueError."""
        with pytest.raises(ValueError, match="valid Berlin postal code"):
            PostalCode("80331")  # Munich

    def test_non_berlin_plz_hamburg_raises(self) -> None:
        """Test that Hamburg postal code raises ValueError."""
        with pytest.raises(ValueError, match="valid Berlin postal code"):
            PostalCode("20095")  # Hamburg

    def test_postal_code_is_immutable(self) -> None:
        """Test that PostalCode is immutable (frozen dataclass)."""
        plz = PostalCode("10115")
        with pytest.raises(AttributeError):
            plz.value = "10116"  # type: ignore
