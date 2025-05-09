#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name
# pylint: disable=protected-access
"""
SPDX-License-Identifier: MIT
SPDX-PackageName: DrumGizmo kits generator
SPDX-PackageHomePage: https://github.com/e-picas/drumgizmo-kits-generator
SPDX-FileCopyrightText: 2025 Pierre Cassat (Picas)

Tests for the validators module.
"""

import os

import pytest

from drumgizmo_kits_generator import logger, validators
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
    validators.validate_name("Test Kit", {})  # No exception should be raised

    # Test with empty name
    with pytest.raises(ValidationError):
        validators.validate_name("", {})

    # Test with whitespace-only name
    with pytest.raises(ValidationError):
        validators.validate_name("   ", {})

    # Test with None
    with pytest.raises(ValidationError):
        validators.validate_name(None, {})


def test_validate_samplerate():
    """Test validate_samplerate function."""
    # Test with valid samplerate
    validators.validate_samplerate(44100, {})  # No exception should be raised
    validators.validate_samplerate("44100", {})  # String should be converted to int

    # Test with empty samplerate
    with pytest.raises(ValidationError):
        validators.validate_samplerate("", {})

    # Test with whitespace-only samplerate
    with pytest.raises(ValidationError):
        validators.validate_samplerate("   ", {})

    # Test with None
    with pytest.raises(ValidationError):
        validators.validate_samplerate(None, {})

    # Test with non-numeric string
    with pytest.raises(ValidationError):
        validators.validate_samplerate("not a number", {})

    # Test with negative samplerate
    with pytest.raises(ValidationError):
        validators.validate_samplerate(-1, {})

    # Test with zero samplerate
    with pytest.raises(ValidationError):
        validators.validate_samplerate(0, {})

    # Test with invalid samplerate
    with pytest.raises(ValidationError):
        validators.validate_samplerate("invalid", {})


def test_validate_velocity_levels():
    """Test validate_velocity_levels function."""
    # Test with valid velocity levels
    validators.validate_velocity_levels(3, {})  # No exception should be raised
    validators.validate_velocity_levels("3", {})  # String should be converted to int

    # Test with empty velocity levels
    with pytest.raises(ValidationError):
        validators.validate_velocity_levels(None, {})

    # Test with zero velocity levels
    with pytest.raises(ValidationError):
        validators.validate_velocity_levels(0, {})

    # Test with negative velocity levels
    with pytest.raises(ValidationError):
        validators.validate_velocity_levels(-1, {})

    # Test with invalid type
    with pytest.raises(ValidationError):
        validators.validate_velocity_levels("invalid", {})


def test_validate_midi_note_min():
    """Test validate_midi_note_min function."""
    # Test with valid midi_note_min
    validators.validate_midi_note_min(0, {})  # No exception should be raised
    validators.validate_midi_note_min("60", {})  # String should be converted to int

    # Test with empty midi_note_min
    with pytest.raises(ValidationError):
        validators.validate_midi_note_min(None, {})

    # Test with out-of-range midi_note_min (negative)
    with pytest.raises(ValidationError):
        validators.validate_midi_note_min(-1, {})

    # Test with out-of-range midi_note_min (too high)
    with pytest.raises(ValidationError):
        validators.validate_midi_note_min(128, {})

    # Test with invalid type
    with pytest.raises(ValidationError):
        validators.validate_midi_note_min("invalid", {})


def test_validate_midi_note_max():
    """Test validate_midi_note_max function."""
    # Test with valid midi_note_max
    validators.validate_midi_note_max(127, {})  # No exception should be raised
    validators.validate_midi_note_max("127", {})  # String should be converted to int

    # Test with empty midi_note_max
    with pytest.raises(ValidationError):
        validators.validate_midi_note_max(None, {})

    # Test with out-of-range midi_note_max (negative)
    with pytest.raises(ValidationError):
        validators.validate_midi_note_max(-1, {})

    # Test with out-of-range midi_note_max (too high)
    with pytest.raises(ValidationError):
        validators.validate_midi_note_max(128, {})

    # Test with invalid type
    with pytest.raises(ValidationError):
        validators.validate_midi_note_max("invalid", {})


def test_validate_midi_note_median():
    """Test validate_midi_note_median function."""
    # Test with valid midi_note_median
    validators.validate_midi_note_median(60, {})  # No exception should be raised
    validators.validate_midi_note_median("60", {})  # String should be converted to int
    validators.validate_midi_note_median(0, {})  # 0 is a valid value

    # Test with out-of-range midi_note_median (negative)
    with pytest.raises(ValidationError):
        validators.validate_midi_note_median(-1, {})

    # Test with out-of-range midi_note_median (too high)
    with pytest.raises(ValidationError):
        validators.validate_midi_note_median(128, {})

    # Test with invalid type
    with pytest.raises(ValidationError):
        validators.validate_midi_note_median("invalid", {})


def test_validate_midi_note():
    """Test _validate_midi_note function."""
    # Test with valid midi_note
    validators._validate_midi_note(60, {})  # No exception should be raised
    validators._validate_midi_note("60", {})  # String should be converted to int
    validators._validate_midi_note(0, {})  # 0 is a valid value

    # Test with empty midi_note
    with pytest.raises(ValidationError):
        validators._validate_midi_note("", {})

    # Test with empty midi_note
    with pytest.raises(ValidationError):
        validators._validate_midi_note(None, {})

    # Test with out-of-range midi_note (negative)
    with pytest.raises(ValidationError):
        validators._validate_midi_note(-1, {})

    # Test with out-of-range midi_note (too high)
    with pytest.raises(ValidationError):
        validators._validate_midi_note(128, {})


def test_validate_whole_config():
    """Test validate_whole_config function."""
    # Test with valid configuration
    validators.validate_whole_config(
        {"midi_note_min": 20, "midi_note_max": 100, "midi_note_median": 60}
    )
    validators.validate_whole_config(
        {"midi_note_min": 1, "midi_note_max": 3, "midi_note_median": 2}
    )

    # Test with midi_note_max < midi_note_min (should raise an exception)
    with pytest.raises(ValidationError):
        validators.validate_whole_config(
            {"midi_note_min": 20, "midi_note_max": 10, "midi_note_median": 60}
        )

    # Test with midi_note_median > midi_note_max (should raise an exception)
    with pytest.raises(ValidationError):
        validators.validate_whole_config(
            {"midi_note_median": 20, "midi_note_max": 10, "midi_note_min": 9}
        )

    # Test with midi_note_median < midi_note_min (should raise an exception)
    with pytest.raises(ValidationError):
        validators.validate_whole_config(
            {"midi_note_median": 20, "midi_note_min": 30, "midi_note_max": 40}
        )


def test_validate_extensions():
    """Test validate_extensions function."""
    # Test with valid extensions
    validators.validate_extensions(["wav", "ogg", "flac"], {})  # No exception should be raised
    validators.validate_extensions(("wav", "ogg", "flac"), {})  # Tuple is also valid

    # Test with empty extensions list
    with pytest.raises(ValidationError):
        validators.validate_extensions([], {})

    # Test with None
    with pytest.raises(ValidationError):
        validators.validate_extensions(None, {})

    # Test with non-list value
    with pytest.raises(ValidationError):
        validators.validate_extensions("wav,ogg,flac", {})

    # Test with empty string in extensions
    with pytest.raises(ValidationError):
        validators.validate_extensions(["wav", "", "flac"], {})

    # Test with whitespace-only extension
    with pytest.raises(ValidationError):
        validators.validate_extensions(["wav", "   ", "flac"], {})

    # Test with non-string extension
    with pytest.raises(ValidationError):
        validators.validate_extensions(["wav", 123, "flac"], {})


def test_validate_channels():
    """Test validate_channels function."""
    # Test with valid channels
    validators.validate_channels(["kick", "snare"], {})  # No exception should be raised
    validators.validate_channels(("kick", "snare"), {})  # Tuple is also valid

    # Test with empty channels list
    with pytest.raises(ValidationError):
        validators.validate_channels([], {})

    # Test with None
    with pytest.raises(ValidationError):
        validators.validate_channels(None, {})

    # Test with non-list value
    with pytest.raises(ValidationError):
        validators.validate_channels("kick,snare", {})

    # Test with empty string in channels
    with pytest.raises(ValidationError):
        validators.validate_channels(["kick", "", "snare"], {})

    # Test with whitespace-only channel name
    with pytest.raises(ValidationError):
        validators.validate_channels(["kick", "   ", "snare"], {})

    # Test with non-string channel name
    with pytest.raises(ValidationError):
        validators.validate_channels(["kick", 123, "snare"], {})


def test_validate_main_channels():
    """Test validate_main_channels function."""
    # Test with valid main_channels (list)
    validators.validate_main_channels(
        ["kick", "snare"], {"channels": ["kick", "snare", "hihat"]}
    )  # No exception should be raised

    # Test with valid main_channels (tuple)
    validators.validate_main_channels(
        ("kick", "snare"), {"channels": ["kick", "snare", "hihat"]}
    )  # No exception should be raised

    # Test with empty main_channels
    validators.validate_main_channels(
        [], {"channels": ["kick", "snare"]}
    )  # No exception should be raised

    # Test with non-list value (should raise an exception)
    with pytest.raises(ValidationError):
        validators.validate_main_channels("kick,snare", {"channels": ["kick", "snare", "hihat"]})

    # Test with empty string in main_channels (should raise an exception)
    with pytest.raises(ValidationError):
        validators.validate_main_channels(
            ["kick", "", "snare"], {"channels": ["kick", "snare", "hihat"]}
        )

    # Test with whitespace-only channel name (should raise an exception)
    with pytest.raises(ValidationError):
        validators.validate_main_channels(
            ["kick", "   ", "snare"], {"channels": ["kick", "snare", "hihat"]}
        )

    # Test with non-string channel name (should raise an exception)
    with pytest.raises(ValidationError):
        validators.validate_main_channels(
            ["kick", 123, "snare"], {"channels": ["kick", "snare", "hihat"]}
        )

    # Test with main_channel not in channels (should raise an exception)
    with pytest.raises(ValidationError):
        validators.validate_main_channels(
            ["kick", "toms"], {"channels": ["kick", "snare", "hihat"]}
        )

    # Test with empty channels list (should raise an exception for any main_channel)
    with pytest.raises(ValidationError):
        validators.validate_main_channels(["kick"], {"channels": ["other"]})

    # Test with None channels (should not raise an exception for empty main_channels)
    validators.validate_main_channels([], {"channels": None})  # No exception should be raised

    # Test with None main_channels (should not raise an exception)
    validators.validate_main_channels(
        None, {"channels": ["kick", "snare"]}
    )  # No exception should be raised

    # Test with string channels and list main_channels
    # The validator should raise an exception if channels is a string, not a list
    with pytest.raises(ValidationError):
        validators.validate_main_channels(["kick", "snare"], {"channels": "kick,snare,hihat"})

    # Test with string main_channels and list channels (should raise an exception)
    with pytest.raises(ValidationError):
        validators.validate_main_channels("kick,snare", {"channels": ["kick", "snare", "hihat"]})


def test_validate_logo(tmp_path):
    """Test validate_logo function."""
    # Create a temporary logo file
    logo_file = tmp_path / "logo.png"
    logo_file.write_text("logo content")

    # Test with valid logo path (no source in config)
    validators.validate_logo(str(logo_file), {})  # No exception should be raised

    # Test with valid logo path (with source in config)
    validators.validate_logo("logo.png", {"source": str(tmp_path)})  # No exception should be raised

    # Test with empty logo path (should be valid)
    validators.validate_logo("", {})  # Empty string is valid (no logo)
    validators.validate_logo(None, {})  # None is also valid (no logo)

    # Test with whitespace-only path (should be invalid)
    with pytest.raises(ValidationError):
        validators.validate_logo("   ", {})

    # Test with non-string value (should be invalid)
    with pytest.raises(ValidationError):
        validators.validate_logo(123, {})

    # Test with non-existent file (should be invalid when source is specified)
    with pytest.raises(ValidationError):
        validators.validate_logo("nonexistent.png", {"source": str(tmp_path)})

    # Test with directory instead of file (should be invalid)
    with pytest.raises(ValidationError):
        validators.validate_logo(str(tmp_path), {"source": str(tmp_path)})

    # Test with relative path (should work with source in config)
    relative_path = os.path.relpath(str(logo_file))
    validators.validate_logo(
        relative_path, {"source": str(tmp_path.parent)}
    )  # No exception should be raised


def test_validate_website():
    """Test validate_website function."""
    # Test with valid website
    validators.validate_website("https://example.com", {})  # No exception should be raised
    validators.validate_website("http://example.com", {})  # http is also valid
    validators.validate_website("https://example.com/path?query=test", {})  # With path and query

    # Test with empty website
    validators.validate_website("", {})  # Empty string is valid (no website)

    # Test with non-string value
    with pytest.raises(ValidationError):
        validators.validate_website(123, {})


def test_validate_extra_files(tmp_path):
    """Test validate_extra_files function."""
    # Create temporary files for testing
    file1 = tmp_path / "file1.txt"
    file1.write_text("test")
    file2 = tmp_path / "file2.txt"
    file2.write_text("test")

    # Test with valid extra files
    validators.validate_extra_files([str(file1), str(file2)], {})  # No exception should be raised

    # Test with empty extra files
    validators.validate_extra_files([], {})  # Empty list is valid (no extra files)

    # Test with non-list value
    with pytest.raises(ValidationError):
        validators.validate_extra_files("file1.txt,file2.txt", {})

    # Test with non-existent file
    with pytest.raises(ValidationError):
        validators.validate_extra_files(["nonexistent.txt"], {"source": str(tmp_path)})

    # Test with directory instead of file
    with pytest.raises(ValidationError):
        validators.validate_extra_files([str(tmp_path)], {"source": str(tmp_path)})

    # Test with empty string in files list
    with pytest.raises(ValidationError):
        validators.validate_extra_files(["file1.txt", "", "file2.txt"], {"source": str(tmp_path)})
    # Test with relative paths (should still work)
    relative_path1 = os.path.relpath(str(file1))
    relative_path2 = os.path.relpath(str(file2))
    validators.validate_extra_files(
        [relative_path1, relative_path2], {"source": str(tmp_path)}
    )  # No exception should be raised

    # Test with None value (should not raise an exception)
    validators.validate_extra_files(
        None, {"source": str(tmp_path)}
    )  # No exception should be raised

    # Test with empty string as source (should not raise an exception for relative paths)
    # The validator should not check file existence if source is an empty string
    validators.validate_extra_files(
        [relative_path1, relative_path2], {"source": ""}
    )  # No exception should be raised

    # Test with non-existent source directory (should raise an exception)
    with pytest.raises(ValidationError):
        validators.validate_extra_files(["file1.txt"], {"source": "/nonexistent/directory"})


def test_validate_variations_method():
    """Test validate_variations_method function."""
    # Test with valid variations method (linear)
    validators.validate_variations_method("linear", {})  # No exception should be raised

    # Test with valid variations method (logarithmic)
    validators.validate_variations_method("logarithmic", {})  # No exception should be raised

    # Test with case-insensitive variations method
    validators.validate_variations_method("LINEAR", {})  # No exception should be raised
    validators.validate_variations_method("Logarithmic", {})  # No exception should be raised

    # Test with empty variations method
    with pytest.raises(ValidationError):
        validators.validate_variations_method("", {})

    # Test with whitespace-only variations method
    with pytest.raises(ValidationError):
        validators.validate_variations_method("   ", {})

    # Test with None
    with pytest.raises(ValidationError):
        validators.validate_variations_method(None, {})

    # Test with invalid variations method
    with pytest.raises(ValidationError):
        validators.validate_variations_method("invalid", {})

    # Test with non-string value
    with pytest.raises(ValidationError):
        validators.validate_variations_method(123, {})


def test_validate_version():
    """Test validate_version function."""
    # Test with valid version
    validators.validate_version("1.0", {})  # No exception should be raised
    validators.validate_version("1.0.0", {})  # Multiple dots are valid
    validators.validate_version("0.1.2.3", {})  # Multiple numbers are valid

    # Test with non-string value
    with pytest.raises(ValidationError):
        validators.validate_version(1.0, {})


def test_validate_description():
    """Test validate_description function."""
    # Test with valid description
    validators.validate_description("Test description", {})  # No exception should be raised

    # Test with non-string value
    with pytest.raises(ValidationError):
        validators.validate_description(123, {})

    # Test with multi-line description (should be valid)
    multi_line = "Line 1\nLine 2\nLine 3"
    validators.validate_description(multi_line, {})  # No exception should be raised

    # Test with special characters
    validators.validate_description(
        "Test description with special chars: !@#$%^&*()", {}
    )  # No exception should be raised

    # Test with very long description
    long_description = "A" * 1000
    validators.validate_description(long_description, {})  # No exception should be raised


def test_validate_notes():
    """Test validate_notes function."""
    # Test with valid notes
    validators.validate_notes("Test notes", {})  # No exception should be raised

    # Test with None (should be valid as notes are optional)
    validators.validate_notes(None, {})  # None is valid for optional field

    # Test with non-string value
    with pytest.raises(ValidationError):
        validators.validate_notes(123, {})

    # Test with only whitespace (should be valid as it's equivalent to empty string)
    validators.validate_notes("  ", {})  # Only whitespace is valid for optional field

    # Test with multi-line notes (should be valid)
    multi_line = "Line 1\nLine 2\nLine 3"
    validators.validate_notes(multi_line, {})  # No exception should be raised

    # Test with special characters
    validators.validate_notes(
        "Test notes with special chars: !@#$%^&*()", {}
    )  # No exception should be raised


def test_validate_author():
    """Test validate_author function."""
    # Test with valid author
    validators.validate_author("Test Author", {})  # No exception should be raised

    # Test with non-string value
    with pytest.raises(ValidationError):
        validators.validate_author(123, {})

    # Test with author that needs trimming (should be valid)
    validators.validate_author("  Test Author  ", {})  # No exception should be raised

    # Test with special characters
    validators.validate_author(
        "Author with special chars: !@#$%^&*()", {}
    )  # No exception should be raised


def test_validate_license():
    """Test validate_license function."""
    # Test with valid license
    validators.validate_license("MIT", {})  # No exception should be raised

    # Test with empty license (should be valid as it will use default)
    validators.validate_license("", {})  # No exception should be raised

    # Test with None (should be valid as it will use default)
    validators.validate_license(None, {})  # No exception should be raised

    # Test with non-string value
    with pytest.raises(ValidationError):
        validators.validate_license(123, {})

    # Test with license that needs trimming (should be valid)
    validators.validate_license("  MIT  ", {})  # No exception should be raised

    # Test with special characters
    validators.validate_license(
        "License with special chars: !@#$%^&*()", {}
    )  # No exception should be raised


def test_validate_whole_config_valid():
    """Test validate_whole_config with valid MIDI note range."""
    # Test with valid MIDI note range
    config_data = {
        "midi_note_min": 36,
        "midi_note_median": 48,
        "midi_note_max": 60,
    }
    validators.validate_whole_config(config_data)  # No exception should be raised


def test_validate_whole_config_invalid_range():
    """Test validate_whole_config with invalid MIDI note range."""
    # Test with min > max
    config_data = {
        "midi_note_min": 60,
        "midi_note_max": 36,  # Invalid: min > max
    }
    with pytest.raises(ValidationError):
        validators.validate_whole_config(config_data)


def test_validate_whole_config_median_validation():
    """Test validate_whole_config with median MIDI note validation."""
    # Test with median < min
    config_data = {
        "midi_note_min": 48,
        "midi_note_median": 36,  # Invalid: median < min
        "midi_note_max": 60,
    }
    with pytest.raises(ValidationError):
        validators.validate_whole_config(config_data)

    # Test with median > max
    config_data = {
        "midi_note_min": 36,
        "midi_note_median": 72,  # Invalid: median > max
        "midi_note_max": 60,
    }
    with pytest.raises(ValidationError):
        validators.validate_whole_config(config_data)

    # Test with median = min (should be valid)
    config_data = {
        "midi_note_min": 36,
        "midi_note_median": 36,  # Valid: median = min
        "midi_note_max": 60,
    }
    validators.validate_whole_config(config_data)  # No exception should be raised

    # Test with median = max (should be valid)
    config_data = {
        "midi_note_min": 36,
        "midi_note_median": 60,  # Valid: median = max
        "midi_note_max": 60,
    }
    validators.validate_whole_config(config_data)  # No exception should be raised
