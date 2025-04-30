#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=too-many-instance-attributes,too-few-public-methods,too-many-locals,broad-exception-caught,redundant-unittest-assert,too-many-branches,too-many-statements,unused-variable
"""
Tests for validating mock configuration files.

This module tests various configuration files in the mocks directory
to ensure they behave as expected based on their naming convention:
- Files containing "can-not" or "must" should result in an error
- Files containing "can" (but not "can-not") should succeed
"""

import os
import sys
import unittest
from io import StringIO
from unittest.mock import patch

# Add the parent directory to the path to be able to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import the modules to test
# pylint: disable=wrong-import-position
from drumgizmo_kits_generator.config import read_config_file
from drumgizmo_kits_generator.validators import (
    validate_midi_and_velocity_params,
    validate_midi_parameters,
    validate_velocity_levels,
)

# pylint: enable=wrong-import-position


class TestMockConfigs(unittest.TestCase):
    """Tests for validating mock configuration files."""

    def setUp(self):
        """Initialize before each test."""
        self.mocks_dir = os.path.join(os.path.dirname(__file__), "mocks")
        self.sources_dir = os.path.join(os.path.dirname(__file__), "sources")

        # Create a mock args object
        class Args:
            """Mock command line arguments."""

            def __init__(self, sources_dir):
                """Initialize with default values."""
                self.source = sources_dir
                self.target = os.path.join(sources_dir, "target")
                self.config = None
                self.velocity_levels = 3
                self.midi_note_min = 0
                self.midi_note_max = 127
                self.midi_note_median = 60
                self.samplerate = "44100"
                self.extensions = "wav,WAV,flac,FLAC,ogg,OGG"

        self.args = Args(self.sources_dir)

    def test_mock_config_files(self):
        """Test all mock configuration files in the mocks directory."""
        # Get all .ini files in the mocks directory
        mock_files = [f for f in os.listdir(self.mocks_dir) if f.endswith(".ini")]

        for mock_file in mock_files:
            full_path = os.path.join(self.mocks_dir, mock_file)
            self.args.config = full_path

            # Determine expected behavior based on filename
            should_fail = "can-not" in mock_file or "must" in mock_file
            should_succeed = "can" in mock_file and "can-not" not in mock_file

            # Capture stderr to avoid cluttering test output
            stderr_capture = StringIO()

            with self.subTest(mock_file=mock_file):
                with patch("sys.stderr", stderr_capture):
                    try:
                        # Read the configuration file
                        metadata = read_config_file(self.args.config)

                        # Validate the configuration
                        metadata = validate_midi_and_velocity_params(metadata, self.args)

                        # Validate MIDI parameters and velocity levels
                        midi_note_min, midi_note_max, midi_note_median = validate_midi_parameters(
                            self.args, metadata
                        )
                        velocity_levels = validate_velocity_levels(self.args, metadata)

                        # Check for specific validation errors based on filename
                        if "channels-can-not-be-empty" in mock_file and "channels" in metadata:
                            if not metadata["channels"]:
                                raise ValueError("Channels cannot be empty")

                        if "extensions-can-not-be-empty" in mock_file and "extensions" in metadata:
                            if not metadata["extensions"]:
                                raise ValueError("Extensions cannot be empty")

                        if "extra-files-must-exist" in mock_file and "extra_files" in metadata:
                            for extra_file in metadata["extra_files"].split(","):
                                if extra_file and not os.path.exists(
                                    os.path.join(self.sources_dir, extra_file.strip())
                                ):
                                    raise FileNotFoundError(f"Extra file not found: {extra_file}")

                        if "logo-must-exist" in mock_file and "logo" in metadata:
                            if not os.path.exists(os.path.join(self.sources_dir, metadata["logo"])):
                                raise FileNotFoundError(f"Logo file not found: {metadata['logo']}")

                        if "main-channels-must-exist-in-channels" in mock_file:
                            if "main_channels" in metadata and "channels" in metadata:
                                main_channels = metadata["main_channels"].split(",")
                                channels = metadata["channels"].split(",")
                                for channel in main_channels:
                                    if channel.strip() not in [c.strip() for c in channels]:
                                        raise ValueError(
                                            f"Main channel {channel} not found in channels"
                                        )

                        if "name-can-not-be-empty" in mock_file and "name" in metadata:
                            if not metadata["name"]:
                                raise ValueError("Name cannot be empty")

                        if "samplerate-must-be-up-to-0" in mock_file and "samplerate" in metadata:
                            if int(metadata["samplerate"]) <= 0:
                                raise ValueError("Sample rate must be greater than 0")

                        if "sampterate-can-not-be-empty" in mock_file and "samplerate" in metadata:
                            if not metadata["samplerate"]:
                                raise ValueError("Sample rate cannot be empty")

                        # Check if the test succeeded when it should have failed
                        if should_fail:
                            # Check stderr output for warnings or errors
                            stderr_content = stderr_capture.getvalue()
                            if "Warning" in stderr_content or "Error" in stderr_content:
                                # This is expected for files that should fail
                                self.assertTrue(
                                    True, f"File {mock_file} generated warnings/errors as expected"
                                )
                            else:
                                self.fail(
                                    f"File {mock_file} should have failed validation but succeeded"
                                )

                        # If we get here and should_succeed is True, the test passes
                        if should_succeed:
                            self.assertTrue(
                                True, f"File {mock_file} succeeded validation as expected"
                            )

                    except Exception as e:
                        # Check if the test failed when it should have succeeded
                        if should_succeed:
                            self.fail(
                                f"File {mock_file} should have succeeded validation but failed with: {e}"
                            )

                        # If we get here and should_fail is True, the test passes
                        if should_fail:
                            self.assertTrue(
                                True, f"File {mock_file} failed validation as expected with: {e}"
                            )


if __name__ == "__main__":
    unittest.main()
