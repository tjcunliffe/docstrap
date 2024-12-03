"""Tests for the filename formatter module."""

import pytest
from pathlib import Path
from docstrap.core.formatter import FilenameFormatter

def test_sanitize_basic():
    """Test basic filename sanitization."""
    result = FilenameFormatter.sanitize("Test File.md")
    assert result == "test-file.md"

def test_sanitize_multiple_spaces():
    """Test sanitization with multiple spaces."""
    result = FilenameFormatter.sanitize("Test   Multiple   Spaces.md")
    assert result == "test-multiple-spaces.md"

def test_sanitize_special_chars():
    """Test sanitization of special characters."""
    result = FilenameFormatter.sanitize("Test!@#$%^&*().md")
    assert result == "test.md"

def test_sanitize_multiple_dashes():
    """Test sanitization of multiple dashes."""
    result = FilenameFormatter.sanitize("test---multiple---dashes.md")
    assert result == "test-multiple-dashes.md"

def test_sanitize_leading_trailing_dashes():
    """Test sanitization of leading/trailing dashes."""
    result = FilenameFormatter.sanitize("-test-file-.md")
    assert result == "test-file.md"

def test_get_base_name_with_prefix():
    """Test extracting base name from prefixed filename."""
    result = FilenameFormatter.get_base_name(Path("010_test-file.md"))
    assert result == "test-file.md"

def test_get_base_name_without_prefix():
    """Test extracting base name from non-prefixed filename."""
    result = FilenameFormatter.get_base_name(Path("test-file.md"))
    assert result == "test-file.md"

def test_get_base_name_with_numbers():
    """Test extracting base name with numbers in filename."""
    result = FilenameFormatter.get_base_name(Path("test123-file.md"))
    assert result == "test123-file.md"

def test_to_title_basic():
    """Test basic title conversion."""
    result = FilenameFormatter.to_title("test-file.md")
    assert result == "Test File"

def test_to_title_multiple_words():
    """Test title conversion with multiple words."""
    result = FilenameFormatter.to_title("getting-started-guide.md")
    assert result == "Getting Started Guide"

def test_to_title_with_numbers():
    """Test title conversion with numbers."""
    result = FilenameFormatter.to_title("test-123-file.md")
    assert result == "Test 123 File"

def test_to_title_without_extension():
    """Test title conversion without file extension."""
    result = FilenameFormatter.to_title("test-file")
    assert result == "Test File"

def test_sanitize_empty_string():
    """Test sanitization of empty string."""
    with pytest.raises(ValueError):
        FilenameFormatter.sanitize("")

def test_sanitize_only_special_chars():
    """Test sanitization of string with only special characters."""
    result = FilenameFormatter.sanitize("!@#$%^&*.md")
    assert result == ".md"

def test_to_title_empty_string():
    """Test title conversion of empty string."""
    with pytest.raises(ValueError):
        FilenameFormatter.to_title("")
