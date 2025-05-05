#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name
"""
Tests for the validators module.
"""

from unittest import mock

import pytest

from drumgizmo_kits_generator import constants, logger, validators
from drumgizmo_kits_generator.exceptions import ValidationError


@pytest.fixture
def mock_logger(monkeypatch):
    """Mock logger functions to capture messages without affecting output."""
    error_messages = []
    warning_messages = []

    def mock_error_func(msg):
        error_messages.append(msg)
        # No longer raising MockExit since error() no longer calls sys.exit()

    def mock_warning_func(msg):
        warning_messages.append(msg)

    monkeypatch.setattr(logger, "error", mock_error_func)
    monkeypatch.setattr(logger, "warning", mock_warning_func)

    return {"error": error_messages, "warning": warning_messages}


def test_validate_name():
    """Test validate_name function."""
    # Test with valid name
    assert validators.validate_name("Test Kit", {}) == "Test Kit"

    # Test with empty name
    with pytest.raises(ValidationError):
        validators.validate_name("", {})

    # Test with None
    with pytest.raises(ValidationError):
        validators.validate_name(None, {})


def test_validate_samplerate():
    """Test validate_samplerate function."""
    # Test with valid samplerate
    assert validators.validate_samplerate(44100, {}) == 44100

    # Test with empty samplerate
    assert validators.validate_samplerate("", {}) == constants.DEFAULT_SAMPLERATE

    # Test with negative samplerate
    with pytest.raises(ValidationError):
        validators.validate_samplerate(-1, {})

    # Test with invalid samplerate
    with pytest.raises(ValidationError):
        validators.validate_samplerate("invalid", {})


def test_validate_velocity_levels():
    """Test validate_velocity_levels function."""
    # Test with valid velocity levels
    assert validators.validate_velocity_levels(3, {}) == 3

    # Test with empty velocity levels
    assert validators.validate_velocity_levels(None, {}) == constants.DEFAULT_VELOCITY_LEVELS

    # Test with zero velocity levels
    assert validators.validate_velocity_levels(0, {}) == constants.DEFAULT_VELOCITY_LEVELS


def test_validate_midi_note_min():
    """Test validate_midi_note_min function."""
    # Test with valid midi_note_min
    assert validators.validate_midi_note_min(0, {}) == 0

    # Test with empty midi_note_min
    assert validators.validate_midi_note_min(None, {}) == constants.DEFAULT_MIDI_NOTE_MIN

    # Test with out-of-range midi_note_min (negative)
    with pytest.raises(ValidationError):
        validators.validate_midi_note_min(-1, {})

    # Test with out-of-range midi_note_min (too high)
    with pytest.raises(ValidationError):
        validators.validate_midi_note_min(128, {})

    # Test with midi_note_min >= midi_note_max
    with pytest.raises(ValidationError):
        validators.validate_midi_note_min(100, {"midi_note_max": 100})


def test_validate_midi_note_max():
    """Test validate_midi_note_max function."""
    # Test with valid midi_note_max
    assert validators.validate_midi_note_max(127, {}) == 127

    # Test with empty midi_note_max
    assert validators.validate_midi_note_max(None, {}) == constants.DEFAULT_MIDI_NOTE_MAX

    # Test with out-of-range midi_note_max (negative)
    with pytest.raises(ValidationError):
        validators.validate_midi_note_max(-1, {})

    # Test with out-of-range midi_note_max (too high)
    with pytest.raises(ValidationError):
        validators.validate_midi_note_max(128, {})

    # Test with midi_note_max <= midi_note_min
    with pytest.raises(ValidationError):
        validators.validate_midi_note_max(100, {"midi_note_min": 100})

    # Test with midi_note_max < midi_note_median
    with pytest.raises(ValidationError):
        validators.validate_midi_note_max(90, {"midi_note_median": 100})


def test_validate_midi_note_median():
    """Test validate_midi_note_median function."""
    # Test with valid midi_note_median
    assert validators.validate_midi_note_median(60, {}) == 60

    # Test with empty midi_note_median
    assert validators.validate_midi_note_median(None, {}) == constants.DEFAULT_MIDI_NOTE_MEDIAN

    # Test with out-of-range midi_note_median (negative)
    with pytest.raises(ValidationError):
        validators.validate_midi_note_median(-1, {})

    # Test with out-of-range midi_note_median (too high)
    with pytest.raises(ValidationError):
        validators.validate_midi_note_median(128, {})

    # Test with midi_note_median < midi_note_min
    with pytest.raises(ValidationError):
        validators.validate_midi_note_median(10, {"midi_note_min": 20})

    # Test with midi_note_median > midi_note_max
    with pytest.raises(ValidationError):
        validators.validate_midi_note_median(110, {"midi_note_max": 100})


def test_validate_extensions():
    """Test validate_extensions function."""
    # Test with valid extensions
    assert validators.validate_extensions(["wav", "ogg", "flac"], {}) == ["wav", "ogg", "flac"]

    # Test with empty extensions
    with pytest.raises(ValidationError):
        validators.validate_extensions("", {})

    # Test with None
    with pytest.raises(ValidationError):
        validators.validate_extensions(None, {})

    # Test with extensions that need trimming
    assert validators.validate_extensions([" wav ", " ogg ", " flac "], {}) == [
        "wav",
        "ogg",
        "flac",
    ]


def test_validate_channels():
    """Test validate_channels function."""
    # Test with valid channels
    assert validators.validate_channels(["kick", "snare"], {}) == ["kick", "snare"]

    # Test with empty channels
    with pytest.raises(ValidationError):
        validators.validate_channels("", {})

    # Test with None
    with pytest.raises(ValidationError):
        validators.validate_channels(None, {})

    # Test with channels that need trimming
    assert validators.validate_channels([" kick ", " snare "], {}) == ["kick", "snare"]


def test_validate_main_channels():
    """Test validate_main_channels function."""
    # Test with valid main_channels
    assert validators.validate_main_channels(
        ["kick", "snare"], {"channels": ["kick", "snare", "hihat"]}
    ) == ["kick", "snare"]

    # Test with empty main_channels
    assert validators.validate_main_channels("", {"channels": ["kick", "snare"]}) == []

    # Test with None
    assert validators.validate_main_channels(None, {"channels": ["kick", "snare"]}) == []

    # Test with main_channels that need trimming
    assert validators.validate_main_channels(
        [" kick ", " snare "], {"channels": ["kick", "snare", "hihat"]}
    ) == ["kick", "snare"]

    # Test with main_channels not in channels
    with pytest.raises(ValidationError):
        validators.validate_main_channels(["kick", "invalid"], {"channels": ["kick", "snare"]})

    # Test when config["channels"] doesn't exist
    assert validators.validate_main_channels(["kick", "snare"], {}) == ["kick", "snare"]

    # Test when config["channels"] is empty
    assert validators.validate_main_channels(["kick", "snare"], {"channels": []}) == [
        "kick",
        "snare",
    ]

    # Test when config["channels"] is None
    assert validators.validate_main_channels(["kick", "snare"], {"channels": None}) == [
        "kick",
        "snare",
    ]


def test_validate_logo(tmp_path):
    """Test validate_logo function."""
    # Create temporary logo file for testing
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    logo_file = source_dir / "logo.png"
    logo_file.write_text("test")

    # Test with valid logo
    assert validators.validate_logo("logo.png", {"source": str(source_dir)}) == "logo.png"

    # Test with nonexistent logo
    with pytest.raises(ValidationError):
        validators.validate_logo("nonexistent.png", {"source": str(source_dir)})

    # Test with None
    assert validators.validate_logo(None, {}) is None

    # Test with empty string
    assert validators.validate_logo("", {}) is None

    # Test when config["source"] doesn't exist
    assert validators.validate_logo("logo.png", {}) == "logo.png"

    # Test when config["source"] is empty
    assert validators.validate_logo("logo.png", {"source": ""}) == "logo.png"

    # Test when config["source"] is None
    assert validators.validate_logo("logo.png", {"source": None}) == "logo.png"


def test_validate_website():
    """Test validate_website function."""
    # Test with valid website
    assert validators.validate_website("https://example.com", {}) == "https://example.com"

    # Test with empty website
    assert validators.validate_website("", {}) is None

    # Test with None
    assert validators.validate_website(None, {}) is None


def test_validate_extra_files(tmp_path):
    """Test validate_extra_files function."""
    # Create temporary files for testing
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    file1 = source_dir / "file1.txt"
    file1.write_text("test1")
    file2 = source_dir / "file2.txt"
    file2.write_text("test2")

    # Test with valid extra_files
    assert validators.validate_extra_files(
        ["file1.txt", "file2.txt"], {"source": str(source_dir)}
    ) == ["file1.txt", "file2.txt"]

    # Test with extra_files that need trimming
    assert validators.validate_extra_files(
        [" file1.txt ", " file2.txt "], {"source": str(source_dir)}
    ) == ["file1.txt", "file2.txt"]

    # Test with nonexistent extra_file
    with pytest.raises(ValidationError):
        validators.validate_extra_files(
            ["file1.txt", "nonexistent.txt"], {"source": str(source_dir)}
        )

    # Test with empty extra_files list
    assert validators.validate_extra_files([], {}) == []

    # Test with None
    assert validators.validate_extra_files(None, {}) == []

    # Test when config["source"] doesn't exist
    assert validators.validate_extra_files(["file1.txt", "file2.txt"], {}) == [
        "file1.txt",
        "file2.txt",
    ]

    # Test when config["source"] is empty
    assert validators.validate_extra_files(["file1.txt", "file2.txt"], {"source": ""}) == [
        "file1.txt",
        "file2.txt",
    ]

    # Test when config["source"] is None
    assert validators.validate_extra_files(["file1.txt", "file2.txt"], {"source": None}) == [
        "file1.txt",
        "file2.txt",
    ]


def test_validate_version():
    """Test validate_version function."""
    # Test with valid version
    assert validators.validate_version("1.0", {}) == "1.0"

    # Test with None
    assert validators.validate_version(None, {}) == constants.DEFAULT_VERSION

    # Test with empty string
    assert validators.validate_version("", {}) == constants.DEFAULT_VERSION


def test_validate_description():
    """Test validate_description function."""
    # Test with valid description
    assert validators.validate_description("Test description", {}) == "Test description"

    # Test with None
    assert validators.validate_description(None, {}) is None

    # Test with empty string
    assert validators.validate_description("", {}) == ""

    # Test with whitespace-only string
    assert validators.validate_description("   ", {}) == "   "

    # Test with special characters
    assert (
        validators.validate_description("Test description with special chars: !@#$%^&*()", {})
        == "Test description with special chars: !@#$%^&*()"
    )

    # Test with very long description
    long_description = "A" * 1000
    assert validators.validate_description(long_description, {}) == long_description


def test_validate_notes():
    """Test validate_notes function."""
    # Test with valid notes
    assert validators.validate_notes("Test notes", {}) == "Test notes"

    # Test with None
    assert validators.validate_notes(None, {}) is None

    # Test with empty string
    assert validators.validate_notes("", {}) == ""

    # Test with whitespace-only string
    assert validators.validate_notes("   ", {}) == "   "

    # Test with multiline notes
    multiline_notes = "Line 1\nLine 2\nLine 3"
    assert validators.validate_notes(multiline_notes, {}) == multiline_notes

    # Test with special characters
    assert (
        validators.validate_notes("Test notes with special chars: !@#$%^&*()", {})
        == "Test notes with special chars: !@#$%^&*()"
    )


def test_validate_author():
    """Test validate_author function."""
    # Test with valid author
    assert validators.validate_author("Test Author", {}) == "Test Author"

    # Test with None
    assert validators.validate_author(None, {}) is None

    # Test with empty string
    assert validators.validate_author("", {}) == ""

    # Test with whitespace-only string
    assert validators.validate_author("   ", {}) == "   "

    # Test with special characters
    assert (
        validators.validate_author("Test Author with special chars: !@#$%^&*()", {})
        == "Test Author with special chars: !@#$%^&*()"
    )


def test_validate_license():
    """Test validate_license function."""
    # Test with valid license
    assert validators.validate_license("MIT License", {}) == "MIT License"

    # Test with None
    assert validators.validate_license(None, {}) == constants.DEFAULT_LICENSE

    # Test with empty string
    assert validators.validate_license("", {}) == constants.DEFAULT_LICENSE

    # Test with whitespace-only string
    assert validators.validate_license("   ", {}) == "   " or constants.DEFAULT_LICENSE

    # Test with special characters
    assert (
        validators.validate_license("License with special chars: !@#$%^&*()", {})
        == "License with special chars: !@#$%^&*()"
    )

    # Test with common license names
    assert validators.validate_license("GPL-3.0", {}) == "GPL-3.0"
    assert validators.validate_license("Apache-2.0", {}) == "Apache-2.0"
    assert validators.validate_license("BSD-3-Clause", {}) == "BSD-3-Clause"


class TestValidateDirectories:
    """Tests for the validate_directories function."""

    @mock.patch("os.path.isdir")
    @mock.patch("os.makedirs")
    def test_validate_directories_existing(self, mock_makedirs, mock_isdir):
        """Test validate_directories with existing directories."""
        mock_isdir.return_value = True

        validators.validate_directories("/path/to/source", "/path/to/target")

        mock_isdir.assert_any_call("/path/to/source")
        mock_makedirs.assert_not_called()

    @mock.patch("os.path.isdir")
    @mock.patch("os.makedirs")
    def test_validate_directories_nonexistent_target(self, mock_makedirs, mock_isdir):
        """Test validate_directories with nonexistent target directory."""
        # Source exists, target doesn't
        mock_isdir.side_effect = lambda path: path == "/path/to/source"

        validators.validate_directories("/path/to/source", "/path/to/target")

        mock_isdir.assert_any_call("/path/to/source")
        mock_isdir.assert_any_call("/path/to/target")
        mock_makedirs.assert_called_once_with("/path/to/target", exist_ok=True)

    @mock.patch("os.path.isdir")
    def test_validate_directories_nonexistent_source(self, mock_isdir):
        """Test validate_directories with nonexistent source directory."""
        mock_isdir.return_value = False

        with pytest.raises(FileNotFoundError):
            validators.validate_directories("/path/to/source", "/path/to/target")

        mock_isdir.assert_called_once_with("/path/to/source")

    @mock.patch("os.path.isdir")
    @mock.patch("os.makedirs")
    def test_validate_directories_dry_run(self, mock_makedirs, mock_isdir):
        """Test validate_directories in dry run mode."""
        # Source exists, target doesn't
        mock_isdir.side_effect = lambda path: path == "/path/to/source"

        validators.validate_directories("/path/to/source", "/path/to/target", dry_run=True)

        mock_isdir.assert_called_once_with("/path/to/source")
        mock_makedirs.assert_not_called()
