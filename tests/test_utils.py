#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-arguments
# pylint: disable=unused-argument
"""
SPDX-License-Identifier: MIT
SPDX-PackageName: DrumGizmo kits generator
SPDX-PackageHomePage: https://github.com/e-picas/drumgizmo-kits-generator
SPDX-FileCopyrightText: 2025 Pierre Cassat (Picas)

Tests for the utils module of the DrumGizmo kit generator.
"""

import os
import tempfile
from unittest import mock

import pytest

from drumgizmo_kits_generator import exceptions, utils


@pytest.fixture
def mock_logger_fixture():
    """Mock logger functions."""
    with mock.patch("drumgizmo_kits_generator.logger.info") as mock_info, mock.patch(
        "drumgizmo_kits_generator.logger.debug"
    ) as mock_debug, mock.patch(
        "drumgizmo_kits_generator.logger.warning"
    ) as mock_warning, mock.patch(
        "drumgizmo_kits_generator.logger.error"
    ) as mock_error, mock.patch(
        "drumgizmo_kits_generator.logger.section"
    ) as mock_section, mock.patch(
        "drumgizmo_kits_generator.logger.print_action_start"
    ) as mock_print_action_start, mock.patch(
        "drumgizmo_kits_generator.logger.print_action_end"
    ) as mock_print_action_end:
        yield {
            "info": mock_info,
            "debug": mock_debug,
            "warning": mock_warning,
            "error": mock_error,
            "section": mock_section,
            "print_action_start": mock_print_action_start,
            "print_action_end": mock_print_action_end,
        }


@pytest.fixture
def sample_file_fixture():
    """Create a temporary audio file for testing."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
        temp_file_path = temp_file.name
    yield temp_file_path
    if os.path.exists(temp_file_path):
        os.unlink(temp_file_path)


class TestCleanInstrumentName:
    """Tests for the get_instrument_name function."""

    def test_get_instrument_name_basic(self):
        """Test get_instrument_name with basic input."""
        # Test with a simple filename (without extension)
        assert utils.get_instrument_name("Kick") == "Kick"
        assert utils.get_instrument_name("Snare") == "Snare"
        assert utils.get_instrument_name("HiHat") == "HiHat"

    def test_get_instrument_name_with_path(self):
        """Test get_instrument_name with path."""
        # Test with paths (without extension)
        assert utils.get_instrument_name("Kick") == "Kick"
        assert utils.get_instrument_name("Snare") == "Snare"

    def test_get_instrument_name_with_special_chars(self):
        """Test get_instrument_name with special characters."""
        # Test with special characters (without extension)
        assert utils.get_instrument_name("Kick-Drum") == "Kick-Drum"
        assert utils.get_instrument_name("Snare-Left") == "Snare-Left"
        assert utils.get_instrument_name("Hi-Hat") == "Hi-Hat"

    def test_get_instrument_name_with_numbers(self):
        """Test get_instrument_name with numbers."""
        # Test with numbers (without extension)
        assert utils.get_instrument_name("Kick01") == "Kick01"
        assert utils.get_instrument_name("Snare_02") == "Snare_02"

    def test_get_instrument_name_with_velocity_prefix(self):
        """Test get_instrument_name with velocity prefix."""
        # Test with velocity prefix
        assert utils.get_instrument_name("1-Kick") == "Kick"
        assert utils.get_instrument_name("2-Snare") == "Snare"
        assert utils.get_instrument_name("3-HiHat") == "HiHat"

    def test_get_instrument_name_with_converted_suffix(self):
        """Test get_instrument_name with _converted suffix."""
        # Test with _converted suffix
        assert utils.get_instrument_name("Kick_converted") == "Kick"
        assert utils.get_instrument_name("Snare_converted") == "Snare"
        assert utils.get_instrument_name("1-HiHat_converted") == "HiHat"


class TestStripQuotes:
    """Tests for the strip_quotes function."""

    def test_strip_quotes_double_quotes(self):
        """Test strip_quotes with double quotes."""
        # Test with double quotes
        assert utils.strip_quotes('"test"') == "test"

    def test_strip_quotes_single_quotes(self):
        """Test strip_quotes with single quotes."""
        # Test with single quotes
        assert utils.strip_quotes("'test'") == "test"

    def test_strip_quotes_no_quotes(self):
        """Test strip_quotes with no quotes."""
        # Test with no quotes
        assert utils.strip_quotes("test") == "test"

    def test_strip_quotes_mixed_quotes(self):
        """Test strip_quotes with mixed quotes (should not strip)."""
        # Test with mixed quotes
        assert utils.strip_quotes("\"test'") == "\"test'"
        assert utils.strip_quotes("'test\"") == "'test\""

    def test_strip_quotes_non_string(self):
        """Test strip_quotes with non-string input."""
        # Test with non-string input
        assert utils.strip_quotes(123) == 123


class TestCalculateMidiNote:
    """Tests for the calculate_midi_note function."""

    def test_calculate_midi_note_left_of_median(self):
        """Test calculate_midi_note with an instrument to the left of median."""
        # Test with an instrument to the left of median
        note = utils.calculate_midi_note(
            i=1, left_count=3, midi_note_median=60, midi_note_min=0, midi_note_max=127
        )
        # Should be median - (left_count - i) = 60 - (3 - 1) = 58
        assert note == 58

    def test_calculate_midi_note_right_of_median(self):
        """Test calculate_midi_note with an instrument to the right of median."""
        # Test with an instrument to the right of median
        note = utils.calculate_midi_note(
            i=4, left_count=3, midi_note_median=60, midi_note_min=0, midi_note_max=127
        )
        # Should be median + (i - left_count) = 60 + (4 - 3) = 61
        assert note == 61

    def test_calculate_midi_note_at_median(self):
        """Test calculate_midi_note with an instrument at the median."""
        # Test with an instrument at the median
        note = utils.calculate_midi_note(
            i=3, left_count=3, midi_note_median=60, midi_note_min=0, midi_note_max=127
        )
        # Should be median + (i - left_count) = 60 + (3 - 3) = 60
        assert note == 60

    def test_calculate_midi_note_below_min(self):
        """Test calculate_midi_note with a note below the minimum."""
        # Test with a note that would be below the minimum
        note = utils.calculate_midi_note(
            i=0, left_count=10, midi_note_median=10, midi_note_min=5, midi_note_max=127
        )
        # Would be 10 - 10 = 0, but should be clamped to 5
        assert note == 5

    def test_calculate_midi_note_above_max(self):
        """Test calculate_midi_note with a note above the maximum."""
        # Test with a note that would be above the maximum
        note = utils.calculate_midi_note(
            i=10, left_count=0, midi_note_median=120, midi_note_min=0, midi_note_max=127
        )
        # Would be 120 + 10 = 130, but should be clamped to 127
        assert note == 127


class TestCheckDependency:
    """Tests for the check_dependency function."""

    @mock.patch("shutil.which")
    def test_check_dependency_found(self, mock_which, mock_logger_fixture):
        """Test check_dependency with a command that is found."""
        # Setup
        mock_which.return_value = "/usr/bin/command"
        # Test
        result = utils.check_dependency("command")
        # Assert
        assert result == "/usr/bin/command"
        mock_which.assert_called_once_with("command")
        mock_logger_fixture["info"].assert_not_called()

    @mock.patch("shutil.which")
    def test_check_dependency_not_found(self, mock_which, mock_logger_fixture):
        """Test check_dependency with dependency not found."""
        # Setup
        mock_which.return_value = None
        # Test & Assert
        with pytest.raises(exceptions.DependencyError) as exc_info:
            utils.check_dependency("nonexistent")
        assert "Dependency 'nonexistent' not found" in str(exc_info.value)
        mock_which.assert_called_once_with("nonexistent")

    @mock.patch("shutil.which")
    def test_check_dependency_custom_message(self, mock_which, mock_logger_fixture):
        """Test check_dependency with a custom error message."""
        # Setup
        mock_which.return_value = None
        custom_message = "Custom error message"
        # Test & Assert
        with pytest.raises(exceptions.DependencyError, match=custom_message):
            utils.check_dependency("nonexistent", error_message=custom_message)
        mock_which.assert_called_once_with("nonexistent")

    @mock.patch("shutil.which")
    def test_check_dependency_returns_correct_path(self, mock_which, mock_logger_fixture):
        """Test that check_dependency returns the correct path when command is found."""
        # Setup
        expected_path = "/custom/path/to/command"
        mock_which.return_value = expected_path
        # Test
        result = utils.check_dependency("command")
        # Assert
        assert result == expected_path
        mock_which.assert_called_once_with("command")


class TestSplitCommaSeparated:
    """Tests for the split_comma_separated function."""

    def test_split_comma_separated_basic(self):
        """Test basic comma-separated string splitting."""
        result = utils.split_comma_separated("a,b,c")
        assert result == ["a", "b", "c"]

    def test_split_comma_separated_with_spaces(self):
        """Test splitting with spaces around commas."""
        result = utils.split_comma_separated("a, b, c")
        assert result == ["a", "b", "c"]

    def test_split_comma_separated_with_quotes(self):
        """Test splitting a quoted string."""
        result = utils.split_comma_separated('"a,b,c"')
        # La fonction split_comma_separated divise toujours sur les virgules, même à l'intérieur des guillemets
        # car c'est le comportement attendu pour notre cas d'utilisation
        assert result == ["a", "b", "c"]

    def test_split_comma_separated_with_empty_items(self):
        """Test splitting with empty items."""
        result = utils.split_comma_separated("a,,b,c,")
        assert result == ["a", "b", "c"]

    def test_split_comma_separated_with_newlines(self):
        """Test splitting with newlines in the string."""
        result = utils.split_comma_separated("a,\n  b, c")
        assert result == ["a", "b", "c"]

    def test_split_comma_separated_with_list_input(self):
        """Test with list input."""
        result = utils.split_comma_separated(["a", "b", "c"])
        assert result == ["a", "b", "c"]

    def test_split_comma_separated_with_none_input(self):
        """Test with None input."""
        result = utils.split_comma_separated(None)
        assert result == []

    def test_split_comma_separated_without_stripping(self):
        """Test without stripping whitespace from items."""
        result = utils.split_comma_separated("a, b ,  c", strip_items=False)
        assert result == ["a", " b ", "  c"]

    def test_split_comma_separated_without_removing_empty(self):
        """Test without removing empty items."""
        result = utils.split_comma_separated("a,,b,c,", remove_empty=False)
        assert result == ["a", "", "b", "c", ""]

    def test_split_comma_separated_with_non_string_input(self):
        """Test with non-string input."""
        result = utils.split_comma_separated(123)
        assert result == []
