#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for the validators module of the DrumGizmo kit generator.

These tests verify the functionality of the validators module that handles
validation of metadata, MIDI parameters, and velocity levels.
"""

import os
import sys
import unittest
from typing import Any, Dict
from unittest.mock import MagicMock

# Add the parent directory to the path to be able to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# pylint: disable=wrong-import-position
# Import the modules to test
from drumgizmo_kits_generator.constants import (
    DEFAULT_EXTENSIONS,
    DEFAULT_MIDI_NOTE_MAX,
    DEFAULT_MIDI_NOTE_MEDIAN,
    DEFAULT_MIDI_NOTE_MIN,
    DEFAULT_VELOCITY_LEVELS,
)
from drumgizmo_kits_generator.validators import (
    validate_metadata_numeric_value,
    validate_midi_and_velocity_params,
    validate_midi_parameters,
    validate_velocity_levels,
)

# pylint: enable=wrong-import-position


class TestValidators(unittest.TestCase):
    """Tests for the validators module."""

    def test_validate_metadata_numeric_value(self):
        """Test validation of numeric metadata values."""
        # Test valid integer
        metadata = {"test_key": "42"}
        validate_metadata_numeric_value(metadata, "test_key")
        self.assertEqual(metadata["test_key"], 42, "Should convert string to integer")

        # Test invalid integer
        metadata = {"test_key": "not_an_integer"}
        with open(os.devnull, "w", encoding="utf-8") as devnull:
            original_stderr = sys.stderr
            sys.stderr = devnull
            try:
                validate_metadata_numeric_value(metadata, "test_key")
                self.assertNotIn("test_key", metadata, "Should remove invalid value from metadata")
            finally:
                sys.stderr = original_stderr

    def test_validate_midi_and_velocity_params(self):
        """Test validation of MIDI and velocity parameters."""
        # Create mock arguments
        args = MagicMock()
        args.midi_note_min = DEFAULT_MIDI_NOTE_MIN
        args.midi_note_max = DEFAULT_MIDI_NOTE_MAX
        args.midi_note_median = DEFAULT_MIDI_NOTE_MEDIAN
        args.velocity_levels = DEFAULT_VELOCITY_LEVELS
        args.extensions = ".wav,.flac"

        # Test valid values
        metadata = {
            "midi_note_min": "60",
            "midi_note_max": "72",
            "midi_note_median": "66",
            "velocity_levels": "5",
            "extensions": ".wav,.flac,.ogg",
        }
        with open(os.devnull, "w", encoding="utf-8") as devnull:
            original_stderr = sys.stderr
            sys.stderr = devnull
            try:
                result = validate_midi_and_velocity_params(metadata, args)
                self.assertEqual(result["midi_note_min"], 60, "Should convert string to integer")
                self.assertEqual(result["midi_note_max"], 72, "Should convert string to integer")
                self.assertEqual(result["midi_note_median"], 66, "Should convert string to integer")
                self.assertEqual(result["velocity_levels"], 5, "Should convert string to integer")
                self.assertEqual(
                    result["extensions"], ".wav,.flac,.ogg", "Should keep valid extensions"
                )
            finally:
                sys.stderr = original_stderr

        # Test invalid values
        metadata = {
            "midi_note_min": "invalid",
            "midi_note_max": "invalid",
            "midi_note_median": "invalid",
            "velocity_levels": "invalid",
            "extensions": "",
        }
        # Make sure args.extensions is different from DEFAULT_EXTENSIONS to trigger validation
        args.extensions = DEFAULT_EXTENSIONS
        with open(os.devnull, "w", encoding="utf-8") as devnull:
            original_stderr = sys.stderr
            sys.stderr = devnull
            try:
                result = validate_midi_and_velocity_params(metadata, args)
                self.assertNotIn("midi_note_min", result, "Should remove invalid value")
                self.assertNotIn("midi_note_max", result, "Should remove invalid value")
                self.assertNotIn("midi_note_median", result, "Should remove invalid value")
                self.assertNotIn("velocity_levels", result, "Should remove invalid value")
                self.assertNotIn("extensions", result, "Should remove empty extensions")
            finally:
                sys.stderr = original_stderr

    def test_validate_midi_parameters(self):
        """Test validation of MIDI parameters."""
        # Create mock arguments
        args = MagicMock()
        args.midi_note_min = DEFAULT_MIDI_NOTE_MIN
        args.midi_note_max = DEFAULT_MIDI_NOTE_MAX
        args.midi_note_median = DEFAULT_MIDI_NOTE_MEDIAN

        # Test valid values
        metadata: Dict[str, Any] = {
            "midi_note_min": 60,
            "midi_note_max": 72,
            "midi_note_median": 66,
        }
        with open(os.devnull, "w", encoding="utf-8") as devnull:
            original_stderr = sys.stderr
            sys.stderr = devnull
            try:
                min_note, max_note, median_note = validate_midi_parameters(args, metadata)
                self.assertEqual(min_note, 60, "Should use metadata value")
                self.assertEqual(max_note, 72, "Should use metadata value")
                self.assertEqual(median_note, 66, "Should use metadata value")
            finally:
                sys.stderr = original_stderr

        # Test invalid values
        metadata = {
            "midi_note_min": 200,  # Invalid (> 127)
            "midi_note_max": -10,  # Invalid (< 0)
            "midi_note_median": 300,  # Invalid (> 127)
        }
        with open(os.devnull, "w", encoding="utf-8") as devnull:
            original_stderr = sys.stderr
            sys.stderr = devnull
            try:
                min_note, max_note, median_note = validate_midi_parameters(args, metadata)
                self.assertEqual(min_note, DEFAULT_MIDI_NOTE_MIN, "Should use default value")
                self.assertEqual(max_note, DEFAULT_MIDI_NOTE_MAX, "Should use default value")
                self.assertEqual(median_note, DEFAULT_MIDI_NOTE_MEDIAN, "Should use default value")
            finally:
                sys.stderr = original_stderr

    def test_validate_velocity_levels(self):
        """Test validation of velocity levels."""
        # Create mock arguments
        args = MagicMock()
        args.velocity_levels = DEFAULT_VELOCITY_LEVELS

        # Test valid value
        metadata: Dict[str, Any] = {"velocity_levels": 5}
        with open(os.devnull, "w", encoding="utf-8") as devnull:
            original_stderr = sys.stderr
            sys.stderr = devnull
            try:
                velocity_levels = validate_velocity_levels(args, metadata)
                self.assertEqual(velocity_levels, 5, "Should use metadata value")
            finally:
                sys.stderr = original_stderr

        # Test invalid value
        metadata = {"velocity_levels": 0}  # Invalid (< 1)
        with open(os.devnull, "w", encoding="utf-8") as devnull:
            original_stderr = sys.stderr
            sys.stderr = devnull
            try:
                velocity_levels = validate_velocity_levels(args, metadata)
                self.assertEqual(
                    velocity_levels, DEFAULT_VELOCITY_LEVELS, "Should use default value"
                )
            finally:
                sys.stderr = original_stderr

        # Test invalid type
        metadata = {"velocity_levels": "not_an_integer"}
        with open(os.devnull, "w", encoding="utf-8") as devnull:
            original_stderr = sys.stderr
            sys.stderr = devnull
            try:
                velocity_levels = validate_velocity_levels(args, metadata)
                self.assertEqual(
                    velocity_levels, DEFAULT_VELOCITY_LEVELS, "Should use default value"
                )
            finally:
                sys.stderr = original_stderr


if __name__ == "__main__":
    unittest.main()
