#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=unspecified-encoding
# pylint: disable=R0801 # code duplication # code duplication
"""
SPDX-License-Identifier: MIT
SPDX-PackageName: DrumGizmo kits generator
SPDX-FileCopyrightText: 2023 E-Picas <drumgizmo@e-picas.fr>
SPDX-FileType: SOURCE

Additional tests for the config.py module
"""

import os
import tempfile
from unittest.mock import patch

import pytest

from drumgizmo_kits_generator.config import (
    load_config_file,
    transform_configuration,
    validate_configuration,
)
from drumgizmo_kits_generator.exceptions import ConfigurationError, ValidationError


def test_load_config_file_with_invalid_ini():
    """Test load_config_file with an invalid INI file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create an invalid INI file (missing section)
        config_file = os.path.join(temp_dir, "invalid.ini")
        with open(config_file, "w") as f:
            f.write("invalid_key=value\n")  # No section header

        # Test loading the invalid file
        with pytest.raises(ConfigurationError) as excinfo:
            load_config_file(config_file)

        assert "Error parsing configuration file" in str(excinfo.value)


def test_load_config_file_with_missing_section():
    """Test load_config_file with a missing required section."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create an INI file with a wrong section
        config_file = os.path.join(temp_dir, "wrong_section.ini")
        with open(config_file, "w") as f:
            f.write("[wrong_section]\n")
            f.write("key=value\n")

        # Test loading the file with missing required section
        # Note: This doesn't raise an exception, it just returns an empty config
        result = load_config_file(config_file)

        # Should return an empty dictionary
        assert isinstance(result, dict)
        assert len(result) == 0


def test_transform_configuration_with_valid_data():
    """Test transform_configuration with valid data."""
    # Create a test configuration
    config_data = {
        "velocity_levels": "4",
        "midi_note_min": "36",
        "midi_note_max": "84",
        "midi_note_median": "60",
        "samplerate": "44100",
        "extensions": ".wav,.flac",
        "channels": "kick,snare,hihat",
        "main_channels": "kick,snare",
    }

    # Transform the configuration
    transformed = transform_configuration(config_data)

    # Verify transformations
    assert transformed["velocity_levels"] == 4  # Converted to int
    assert transformed["midi_note_min"] == 36  # Converted to int
    assert transformed["midi_note_max"] == 84  # Converted to int
    assert transformed["midi_note_median"] == 60  # Converted to int
    assert transformed["samplerate"] == 44100  # Converted to int
    assert transformed["extensions"] == [".wav", ".flac"]  # Split into list
    assert transformed["channels"] == ["kick", "snare", "hihat"]  # Split into list
    assert transformed["main_channels"] == ["kick", "snare"]  # Split into list


def test_transform_configuration_with_invalid_data():
    """Test transform_configuration with invalid data."""
    # Create a test configuration with invalid data
    config_data = {
        "velocity_levels": "invalid",  # Should be a number
        "midi_note_min": "36",
        "midi_note_max": "84",
        "midi_note_median": "60",
    }

    # Create a mock transformer that raises an exception
    def mock_transform_velocity_levels(value):
        raise ValueError("Invalid velocity levels value")

    # Patch the transformer function
    with patch(
        "drumgizmo_kits_generator.transformers.transform_velocity_levels",
        side_effect=mock_transform_velocity_levels,
    ):
        # Test that an exception is raised
        with pytest.raises(ConfigurationError) as excinfo:
            transform_configuration(config_data)

        assert "Failed to transform configuration" in str(excinfo.value)


def test_validate_configuration_with_valid_data():
    """Test validate_configuration with valid data."""
    # Create a valid configuration
    config_data = {
        "name": "Test Kit",
        "version": "1.0",
        "velocity_levels": 4,
        "midi_note_min": 36,
        "midi_note_max": 84,
        "midi_note_median": 60,
        "samplerate": "44100",
        "extensions": [".wav", ".flac"],
        "channels": ["kick", "snare", "hihat"],
        "main_channels": ["kick", "snare"],
    }

    # Should not raise an exception
    with patch("drumgizmo_kits_generator.validators.validate_whole_config"):
        validate_configuration(config_data)


def test_validate_configuration_with_invalid_data():
    """Test validate_configuration with invalid data."""
    # Create an invalid configuration (midi_note_max < midi_note_min)
    config_data = {
        "name": "Test Kit",
        "version": "1.0",
        "velocity_levels": 4,
        "midi_note_min": 84,  # Higher than max
        "midi_note_max": 36,  # Lower than min
        "midi_note_median": 60,
        "samplerate": "44100",
    }

    # Should raise a ValidationError
    with pytest.raises(ValidationError):
        with patch(
            "drumgizmo_kits_generator.validators.validate_whole_config",
            side_effect=ValidationError("MIDI note range is invalid"),
        ):
            validate_configuration(config_data)
