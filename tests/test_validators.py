#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name
"""
Tests for the validators module.
"""

import pytest

from drumgizmo_kits_generator import constants, logger, validators


class MockExit(Exception):
    """Exception raised to mock sys.exit without actually exiting."""

    def __init__(self, code=0):
        self.code = code
        super().__init__(f"Mock exit with code {code}")


@pytest.fixture
def mock_logger(monkeypatch):
    """Mock logger functions to capture messages and avoid actual exit."""
    error_messages = []
    warning_messages = []

    def mock_error_func(msg):
        error_messages.append(msg)
        raise MockExit(127)

    def mock_warning_func(msg):
        warning_messages.append(msg)

    monkeypatch.setattr(logger, "error", mock_error_func)
    monkeypatch.setattr(logger, "warning", mock_warning_func)

    return {"error": error_messages, "warning": warning_messages}


def test_validate_name(mock_logger):
    """Test validate_name function."""
    # Test with valid name
    assert validators.validate_name("Test Kit", {}) == "Test Kit"

    # Test with empty name
    with pytest.raises(MockExit) as excinfo:
        validators.validate_name("", {})
    assert excinfo.value.code == 127

    # Check that the error message was logged
    assert any("name cannot be empty" in msg for msg in mock_logger["error"])

    # Test with None
    with pytest.raises(MockExit):
        validators.validate_name(None, {})


def test_validate_samplerate(mock_logger):
    """Test validate_samplerate function."""
    # Test with valid samplerate
    assert validators.validate_samplerate(44100, {}) == 44100

    # Test with empty samplerate
    assert validators.validate_samplerate("", {}) == constants.DEFAULT_SAMPLERATE
    assert any("Sample rate is empty" in msg for msg in mock_logger["warning"])

    # Test with negative samplerate
    with pytest.raises(MockExit):
        validators.validate_samplerate(-1, {})
    assert any("Sample rate must be greater than 0" in msg for msg in mock_logger["error"])

    # Test with non-numeric samplerate
    with pytest.raises(MockExit):
        validators.validate_samplerate("invalid", {})
    assert any("Sample rate must be a number" in msg for msg in mock_logger["error"])


def test_validate_velocity_levels(mock_logger):
    """Test validate_velocity_levels function."""
    # Test with valid velocity levels
    assert validators.validate_velocity_levels(10, {}) == 10

    # Test with empty velocity levels
    assert validators.validate_velocity_levels(None, {}) == constants.DEFAULT_VELOCITY_LEVELS
    assert any("Velocity levels is empty" in msg for msg in mock_logger["warning"])

    # Test with zero velocity levels
    assert validators.validate_velocity_levels(0, {}) == constants.DEFAULT_VELOCITY_LEVELS
    assert any("using default" in msg for msg in mock_logger["warning"])


def test_validate_midi_note_min(mock_logger):
    """Test validate_midi_note_min function."""
    # Test with valid midi_note_min
    assert validators.validate_midi_note_min(0, {}) == 0

    # Test with empty midi_note_min
    assert validators.validate_midi_note_min(None, {}) == constants.DEFAULT_MIDI_NOTE_MIN
    assert any("Minimum MIDI note is empty" in msg for msg in mock_logger["warning"])

    # Test with out-of-range midi_note_min (negative)
    with pytest.raises(MockExit):
        validators.validate_midi_note_min(-1, {})
    assert any("Minimum MIDI note must be between 0 and 127" in msg for msg in mock_logger["error"])

    # Test with out-of-range midi_note_min (too high)
    with pytest.raises(MockExit):
        validators.validate_midi_note_min(128, {})
    assert any("Minimum MIDI note must be between 0 and 127" in msg for msg in mock_logger["error"])

    # Test with midi_note_min >= midi_note_max
    with pytest.raises(MockExit):
        validators.validate_midi_note_min(100, {"midi_note_max": 100})
    assert any(
        "Minimum MIDI note (100) must be less than maximum MIDI note (100)" in msg
        for msg in mock_logger["error"]
    )


def test_validate_midi_note_max(mock_logger):
    """Test validate_midi_note_max function."""
    # Test with valid midi_note_max
    assert validators.validate_midi_note_max(127, {}) == 127

    # Test with empty midi_note_max
    assert validators.validate_midi_note_max(None, {}) == constants.DEFAULT_MIDI_NOTE_MAX
    assert any("Maximum MIDI note is empty" in msg for msg in mock_logger["warning"])

    # Test with out-of-range midi_note_max (negative)
    with pytest.raises(MockExit):
        validators.validate_midi_note_max(-1, {})
    assert any("Maximum MIDI note must be between 0 and 127" in msg for msg in mock_logger["error"])

    # Test with out-of-range midi_note_max (too high)
    with pytest.raises(MockExit):
        validators.validate_midi_note_max(128, {})
    assert any("Maximum MIDI note must be between 0 and 127" in msg for msg in mock_logger["error"])

    # Test with midi_note_max <= midi_note_min
    with pytest.raises(MockExit):
        validators.validate_midi_note_max(100, {"midi_note_min": 100})
    assert any(
        "Maximum MIDI note (100) must be greater than minimum MIDI note (100)" in msg
        for msg in mock_logger["error"]
    )

    # Test with midi_note_max < midi_note_median
    with pytest.raises(MockExit):
        validators.validate_midi_note_max(90, {"midi_note_median": 100})
    assert any(
        "Maximum MIDI note (90) must be greater than or equal to median MIDI note (100)" in msg
        for msg in mock_logger["error"]
    )


def test_validate_midi_note_median(mock_logger):
    """Test validate_midi_note_median function."""
    # Test with valid midi_note_median
    assert validators.validate_midi_note_median(64, {}) == 64

    # Test with empty midi_note_median
    assert validators.validate_midi_note_median(None, {}) == constants.DEFAULT_MIDI_NOTE_MEDIAN
    assert any("Median MIDI note is empty" in msg for msg in mock_logger["warning"])

    # Test with out-of-range midi_note_median (negative)
    with pytest.raises(MockExit):
        validators.validate_midi_note_median(-1, {})
    assert any("Median MIDI note must be between 0 and 127" in msg for msg in mock_logger["error"])

    # Test with out-of-range midi_note_median (too high)
    with pytest.raises(MockExit):
        validators.validate_midi_note_median(128, {})
    assert any("Median MIDI note must be between 0 and 127" in msg for msg in mock_logger["error"])

    # Test with midi_note_median < midi_note_min
    with pytest.raises(MockExit):
        validators.validate_midi_note_median(10, {"midi_note_min": 20})
    assert any(
        "Median MIDI note (10) must be greater than or equal to minimum MIDI note (20)" in msg
        for msg in mock_logger["error"]
    )

    # Test with midi_note_median > midi_note_max
    with pytest.raises(MockExit):
        validators.validate_midi_note_median(100, {"midi_note_max": 90})
    assert any(
        "Median MIDI note (100) must be less than or equal to maximum MIDI note (90)" in msg
        for msg in mock_logger["error"]
    )


def test_validate_extensions(mock_logger):
    """Test validate_extensions function."""
    # Test with valid extensions
    assert validators.validate_extensions([".wav", ".flac"], {}) == [".wav", ".flac"]

    # Test with extensions that need trimming
    assert validators.validate_extensions([" .wav ", " .flac "], {}) == [".wav", ".flac"]

    # Test with empty extensions
    with pytest.raises(MockExit):
        validators.validate_extensions([], {})
    assert any("Extensions list cannot be empty" in msg for msg in mock_logger["error"])

    # Test with None
    with pytest.raises(MockExit):
        validators.validate_extensions(None, {})
    assert any("Extensions list cannot be empty" in msg for msg in mock_logger["error"])


def test_validate_channels(mock_logger):
    """Test validate_channels function."""
    # Test with valid channels
    assert validators.validate_channels(["kick", "snare"], {}) == ["kick", "snare"]

    # Test with channels that need trimming
    assert validators.validate_channels([" kick ", " snare "], {}) == ["kick", "snare"]

    # Test with empty channels
    with pytest.raises(MockExit):
        validators.validate_channels([], {})
    assert any("Channels list cannot be empty" in msg for msg in mock_logger["error"])

    # Test with None
    with pytest.raises(MockExit):
        validators.validate_channels(None, {})
    assert any("Channels list cannot be empty" in msg for msg in mock_logger["error"])


def test_validate_main_channels(mock_logger):
    """Test validate_main_channels function."""
    # Test with valid main_channels
    assert validators.validate_main_channels(
        ["kick", "snare"], {"channels": ["kick", "snare", "hihat"]}
    ) == ["kick", "snare"]

    # Test with empty main_channels
    assert validators.validate_main_channels([], {}) == []

    # Test with None
    assert validators.validate_main_channels(None, {}) == []

    # Test with main_channels that need trimming
    assert validators.validate_main_channels(
        [" kick ", " snare "], {"channels": ["kick", "snare", "hihat"]}
    ) == ["kick", "snare"]

    # Test with main_channels not in channels
    with pytest.raises(MockExit):
        validators.validate_main_channels(["kick", "invalid"], {"channels": ["kick", "snare"]})
    assert any(
        "Main channel 'invalid' is not in the channels list" in msg for msg in mock_logger["error"]
    )


def test_validate_logo(mock_logger, tmp_path):
    """Test validate_logo function."""
    # Create a temporary file for testing
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    logo_file = source_dir / "logo.png"
    logo_file.write_text("test")

    # Test with valid logo
    assert validators.validate_logo("logo.png", {"source": str(source_dir)}) == "logo.png"

    # Test with nonexistent logo
    with pytest.raises(MockExit):
        validators.validate_logo("nonexistent.png", {"source": str(source_dir)})
    assert any("Logo file does not exist" in msg for msg in mock_logger["error"])

    # Test with None
    assert validators.validate_logo(None, {}) is None

    # Test with empty string
    assert validators.validate_logo("", {}) is None


def test_validate_extra_files(mock_logger, tmp_path):
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
    with pytest.raises(MockExit):
        validators.validate_extra_files(
            ["file1.txt", "nonexistent.txt"], {"source": str(source_dir)}
        )
    assert any("Extra file does not exist" in msg for msg in mock_logger["error"])

    # Test with empty extra_files list
    assert validators.validate_extra_files([], {}) == []

    # Test with None
    assert validators.validate_extra_files(None, {}) == []


def test_validate_website():
    """Test validate_website function."""
    # Test with valid website
    assert validators.validate_website("https://example.com", {}) == "https://example.com"

    # Test with None
    assert validators.validate_website(None, {}) is None

    # Test with empty string
    assert validators.validate_website("", {}) == ""


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


def test_validate_notes():
    """Test validate_notes function."""
    # Test with valid notes
    assert validators.validate_notes("Test notes", {}) == "Test notes"

    # Test with None
    assert validators.validate_notes(None, {}) is None

    # Test with empty string
    assert validators.validate_notes("", {}) == ""


def test_validate_author():
    """Test validate_author function."""
    # Test with valid author
    assert validators.validate_author("Test Author", {}) == "Test Author"

    # Test with None
    assert validators.validate_author(None, {}) is None

    # Test with empty string
    assert validators.validate_author("", {}) == ""


def test_validate_license():
    """Test validate_license function."""
    # Test with valid license
    assert validators.validate_license("MIT License", {}) == "MIT License"

    # Test with None
    assert validators.validate_license(None, {}) == constants.DEFAULT_LICENSE

    # Test with empty string
    assert validators.validate_license("", {}) == constants.DEFAULT_LICENSE
