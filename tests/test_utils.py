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

from drumgizmo_kits_generator import exceptions, utils, validators


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
    ) as mock_section:
        yield {
            "info": mock_info,
            "debug": mock_debug,
            "warning": mock_warning,
            "error": mock_error,
            "section": mock_section,
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
    """Tests for the clean_instrument_name function."""

    def test_clean_instrument_name_basic(self):
        """Test clean_instrument_name with basic input."""
        # Test with a simple filename (without extension)
        assert utils.clean_instrument_name("Kick") == "Kick"
        assert utils.clean_instrument_name("Snare") == "Snare"
        assert utils.clean_instrument_name("HiHat") == "HiHat"

    def test_clean_instrument_name_with_path(self):
        """Test clean_instrument_name with path."""
        # Test with paths (without extension)
        assert utils.clean_instrument_name("Kick") == "Kick"
        assert utils.clean_instrument_name("Snare") == "Snare"

    def test_clean_instrument_name_with_special_chars(self):
        """Test clean_instrument_name with special characters."""
        # Test with special characters (without extension)
        assert utils.clean_instrument_name("Kick-Drum") == "Kick-Drum"
        assert utils.clean_instrument_name("Snare-Left") == "Snare-Left"
        assert utils.clean_instrument_name("Hi-Hat") == "Hi-Hat"

    def test_clean_instrument_name_with_numbers(self):
        """Test clean_instrument_name with numbers."""
        # Test with numbers (without extension)
        assert utils.clean_instrument_name("Kick01") == "Kick01"
        assert utils.clean_instrument_name("Snare_02") == "Snare_02"

    def test_clean_instrument_name_with_velocity_prefix(self):
        """Test clean_instrument_name with velocity prefix."""
        # Test with velocity prefix
        assert utils.clean_instrument_name("1-Kick") == "Kick"
        assert utils.clean_instrument_name("2-Snare") == "Snare"
        assert utils.clean_instrument_name("3-HiHat") == "HiHat"

    def test_clean_instrument_name_with_converted_suffix(self):
        """Test clean_instrument_name with _converted suffix."""
        # Test with _converted suffix
        assert utils.clean_instrument_name("Kick_converted") == "Kick"
        assert utils.clean_instrument_name("Snare_converted") == "Snare"
        assert utils.clean_instrument_name("1-HiHat_converted") == "HiHat"


class TestValidateDirectories:
    """Tests for the validate_directories function."""

    @mock.patch("os.path.isdir")
    def test_validate_directories_all_valid(self, mock_isdir, mock_logger_fixture):
        """Test validate_directories with all valid paths."""
        # Setup mocks
        mock_isdir.return_value = True

        # Call the function - should not raise an exception
        validators.validate_directories("/path/to/source", "/path/to/target")

        # Also test with dry_run parameter
        validators.validate_directories("/path/to/source", "/path/to/target", True)

    @mock.patch("os.path.isdir")
    def test_validate_directories_invalid_source(self, mock_isdir, mock_logger_fixture):
        """Test validate_directories with invalid source directory."""
        # Setup mocks
        mock_isdir.return_value = False

        # Call the function and expect a FileNotFoundError
        with pytest.raises(FileNotFoundError) as excinfo:
            validators.validate_directories("/invalid/source", "/valid/target")

        # Verify the error message
        assert "Source directory '/invalid/source' does not exist" in str(excinfo.value)

    @mock.patch("os.path.isdir")
    @mock.patch("os.makedirs")
    def test_validate_directories_create_target(
        self, mock_makedirs, mock_isdir, mock_logger_fixture
    ):
        """Test validate_directories creates target directory if it doesn't exist."""
        # Setup mocks
        mock_isdir.side_effect = lambda path: path == "/valid/source"

        # Call the function - should not raise an exception and should create target
        validators.validate_directories("/valid/source", "/nonexistent/target")

    @mock.patch("os.path.isdir")
    def test_validate_directories_dry_run(self, mock_isdir, mock_logger_fixture):
        """Test validate_directories in dry run mode."""
        # Setup mocks
        mock_isdir.side_effect = lambda path: path == "/valid/source"

        # Call the function in dry run mode - should not raise an exception
        validators.validate_directories("/valid/source", "/nonexistent/target", True)


class TestPrepareTargetDirectory:
    """Tests for the prepare_target_directory function."""

    @mock.patch("os.path.exists")
    @mock.patch("os.makedirs")
    def test_prepare_target_directory_new(self, mock_makedirs, mock_exists, mock_logger_fixture):
        """Test prepare_target_directory with a new directory."""
        # Setup mocks
        mock_exists.return_value = False

        # Call the function
        utils.prepare_target_directory("/path/to/target")

        # Assertions
        mock_makedirs.assert_called_once_with("/path/to/target")
        assert mock_logger_fixture["section"].call_count >= 1
        assert mock_logger_fixture["info"].call_count >= 1

    @mock.patch("os.path.exists")
    @mock.patch("os.path.isdir")
    @mock.patch("os.listdir")
    @mock.patch("os.path.join")
    @mock.patch("shutil.rmtree")
    @mock.patch("os.remove")
    def test_prepare_target_directory_existing(
        self,
        mock_remove,
        mock_rmtree,
        mock_join,
        mock_listdir,
        mock_isdir,
        mock_exists,
        mock_logger_fixture,
    ):
        """Test prepare_target_directory with an existing directory."""
        # Setup mocks
        mock_exists.return_value = True
        mock_listdir.return_value = ["file1.txt", "file2.txt", "dir1"]

        # Mock os.path.join to return predictable paths
        def mock_join_paths(dir_path, item):
            return f"{dir_path}/{item}"

        mock_join.side_effect = mock_join_paths

        # Mock os.path.isdir to identify directories
        def mock_is_dir(path):
            return "dir" in path

        mock_isdir.side_effect = mock_is_dir

        # Call the function
        utils.prepare_target_directory("/path/to/target")

        # Assertions
        assert mock_logger_fixture["section"].call_count >= 1
        assert mock_logger_fixture["info"].call_count >= 1
        assert mock_listdir.call_count == 1

        # Check that directories are removed with rmtree
        mock_rmtree.assert_called_once_with("/path/to/target/dir1")

        # Check that files are removed with os.remove
        assert mock_remove.call_count == 2
        mock_remove.assert_any_call("/path/to/target/file1.txt")
        mock_remove.assert_any_call("/path/to/target/file2.txt")


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
        # Setup mocks
        expected_path = "/usr/bin/test_command"
        mock_which.return_value = expected_path

        # Call the function and get the returned path
        result = utils.check_dependency("test_command")

        # Verify that the function returns the correct path
        assert result == expected_path

        # Verify that logger.error was not called
        mock_logger_fixture["error"].assert_not_called()

    @mock.patch("shutil.which")
    def test_check_dependency_not_found(self, mock_which, mock_logger_fixture):
        """Test check_dependency with dependency not found."""
        # Setup mocks
        mock_which.return_value = None

        # Call the function and expect a DependencyError
        with pytest.raises(exceptions.DependencyError) as excinfo:
            utils.check_dependency("test_command")

        # Verify the error message contains the command name
        assert "test_command" in str(excinfo.value)
        assert "not found" in str(excinfo.value)

        # No need to verify logger.error call as it's now handled in main.py
        # mock_logger_fixture["error"].assert_called_once()

    @mock.patch("shutil.which")
    def test_check_dependency_custom_message(self, mock_which, mock_logger_fixture):
        """Test check_dependency with a custom error message."""
        # Setup mocks
        mock_which.return_value = None
        custom_message = "Custom error message for test_command"

        # Call the function and expect a DependencyError
        with pytest.raises(exceptions.DependencyError) as excinfo:
            utils.check_dependency("test_command", custom_message)

        # Verify the error message
        assert custom_message == str(excinfo.value)

        # No need to verify logger.error call as it's now handled in main.py
        # mock_logger_fixture["error"].assert_called_once()

    @mock.patch("shutil.which")
    def test_check_dependency_returns_correct_path(self, mock_which, mock_logger_fixture):
        """Test that check_dependency returns the correct path when command is found."""
        # Setup mocks
        expected_path = "/custom/path/to/command"
        mock_which.return_value = expected_path

        # Call the function
        result = utils.check_dependency("custom_command")

        # Verify the returned path is correct
        assert result == expected_path

        # Verify shutil.which was called with the correct argument
        mock_which.assert_called_once_with("custom_command")

        # Verify no errors were logged
        mock_logger_fixture["error"].assert_not_called()
