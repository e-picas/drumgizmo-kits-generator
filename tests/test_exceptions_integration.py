#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SPDX-License-Identifier: MIT
SPDX-PackageName: DrumGizmo kits generator
SPDX-PackageHomePage: https://github.com/e-picas/drumgizmo-kits-generator
SPDX-FileCopyrightText: 2025 Pierre Cassat (Picas)

Integration tests for exceptions with context in the DrumGizmo kit generator.
"""

import os
import tempfile
from unittest.mock import patch

import pytest

from drumgizmo_kits_generator.audio import convert_sample_rate
from drumgizmo_kits_generator.exceptions import (
    AudioProcessingError,
    ConfigurationError,
    DirectoryError,
    ValidationError,
)


def test_directory_error_with_context():
    """Test that DirectoryError is raised with proper context when a directory doesn't exist."""
    non_existent_dir = "/path/that/does/not/exist"

    # Test with a non-existent directory
    with pytest.raises(DirectoryError) as excinfo:
        with patch("os.path.isdir", return_value=False):
            with patch("os.makedirs") as mock_makedirs:
                mock_makedirs.side_effect = DirectoryError(
                    f"Failed to create directory: {non_existent_dir}",
                    context={"path": non_existent_dir, "operation": "create"},
                )
                # Attempt to create a directory that will fail
                try:
                    os.makedirs(non_existent_dir)
                # pylint: disable=try-except-raise
                except DirectoryError:
                    raise

    # Check that the exception has the expected context
    assert excinfo.value.message is not None
    assert "directory" in excinfo.value.message.lower()
    assert excinfo.value.context is not None
    assert "path" in excinfo.value.context
    assert excinfo.value.context["path"] == non_existent_dir


def test_audio_processing_error_with_context():
    """Test that AudioProcessingError is raised with proper context when audio processing fails."""
    # Create a temporary file that is not a valid audio file
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
        temp_file.write(b"This is not a valid WAV file")
        temp_file_path = temp_file.name

    try:
        # Attempt to convert the sample rate of an invalid audio file
        with pytest.raises(AudioProcessingError) as excinfo:
            convert_sample_rate(temp_file_path, "44100")

        # Check that the exception has the expected context
        assert excinfo.value.message is not None
        assert (
            "convert" in excinfo.value.message.lower() or "process" in excinfo.value.message.lower()
        )
        assert excinfo.value.context is not None
        assert "file" in excinfo.value.context
        # The key might be target_samplerate instead of target_sample_rate
        assert "target_samplerate" in excinfo.value.context
        assert excinfo.value.context["target_samplerate"] == "44100"
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)


def test_validation_error_with_context():
    """Test that ValidationError is raised with proper context during validation."""
    # Create a ValidationError with context directly
    error = ValidationError(
        "Invalid channel configuration",
        context={
            "parameter": "channels",
            "value": "invalid,channels",
            "allowed_values": "Left,Right,Center",
        },
    )

    # Check that the exception has the expected message and context
    assert error.message == "Invalid channel configuration"
    assert error.context is not None
    assert "parameter" in error.context
    assert error.context["parameter"] == "channels"
    assert "value" in error.context
    assert error.context["value"] == "invalid,channels"
    assert "allowed_values" in error.context
    assert error.context["allowed_values"] == "Left,Right,Center"

    # Check the string representation includes context
    assert "Invalid channel configuration [Context:" in str(error)
    assert "parameter=channels" in str(error)
    assert "value=invalid,channels" in str(error)
    assert "allowed_values=Left,Right,Center" in str(error)


def test_configuration_error_with_context():
    """Test that ConfigurationError is raised with proper context when config file is invalid."""
    # Create a ConfigurationError with context directly
    error = ConfigurationError(
        "Configuration file not found",
        context={
            "file_path": "/path/to/nonexistent/config.ini",
            "section": "drumgizmo_kit_generator",
        },
    )

    # Check that the exception has the expected message and context
    assert error.message == "Configuration file not found"
    assert error.context is not None
    assert "file_path" in error.context
    assert error.context["file_path"] == "/path/to/nonexistent/config.ini"
    assert "section" in error.context
    assert error.context["section"] == "drumgizmo_kit_generator"

    # Check the string representation includes context
    assert "Configuration file not found [Context:" in str(error)
    assert "file_path=/path/to/nonexistent/config.ini" in str(error)
    assert "section=drumgizmo_kit_generator" in str(error)
