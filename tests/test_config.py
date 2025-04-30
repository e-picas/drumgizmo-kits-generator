#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=broad-exception-caught
# pylint: disable=import-outside-toplevel,wrong-import-position
"""
Unit tests for the configuration module of the DrumGizmo kit generator.

These tests verify the functionality of configuration file reading and
the correctness of the channel constants used in the application.
"""

import os
import sys
import tempfile
import unittest

# Add the parent directory to the path to be able to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import the module to test
from drumgizmo_kits_generator.config import (
    get_channels_from_metadata,
    get_main_channels_from_metadata,
    process_channels_config,
    read_config_file,
)
from drumgizmo_kits_generator.constants import DEFAULT_CHANNELS, DEFAULT_MAIN_CHANNELS


class TestConfig(unittest.TestCase):
    """Tests for the configuration module."""

    def setUp(self):
        """Initialize before each test by creating test configuration files."""
        self.source_dir = os.path.join(os.path.dirname(__file__), "sources")
        self.config_file = os.path.join(self.source_dir, "drumgizmo-kit.ini")

        # Create a temporary configuration file for tests
        with tempfile.NamedTemporaryFile(delete=False, mode="w") as self.temp_config:
            self.temp_config.write(
                """
kit_name="Temp Test Kit"
kit_version="2.0"
kit_author="Test Author"
kit_license="CC0"
kit_channels=kick,snare,hihat,tom1,tom2,tom3,tom4,ride,crash1,crash2
kit_main_channels=kick,snare,hihat
"""
            )

    def tearDown(self):
        """Clean up after each test."""
        # Remove the temporary configuration file
        if hasattr(self, "temp_config") and os.path.exists(self.temp_config.name):
            os.unlink(self.temp_config.name)

    def test_read_config_file(self):
        """Test reading a configuration file."""
        # Test with a valid configuration file
        metadata = read_config_file(self.temp_config.name)
        self.assertIsNotNone(metadata)
        self.assertEqual(metadata.get("name"), "Temp Test Kit")
        self.assertEqual(metadata.get("version"), "2.0")
        self.assertEqual(metadata.get("author"), "Test Author")
        self.assertEqual(metadata.get("license"), "CC0")

        # Test with a non-existent file
        metadata = read_config_file("non_existent_file.ini")
        self.assertEqual(metadata, {})

    def test_process_channels_config(self):
        """Test processing channels configuration."""
        # Test with valid channels and main channels
        metadata = {"channels": "kick,snare,hihat,tom1,tom2", "main_channels": "kick,snare,hihat"}
        process_channels_config(metadata)
        self.assertEqual(metadata["channels"], ["kick", "snare", "hihat", "tom1", "tom2"])
        self.assertEqual(metadata["main_channels"], ["kick", "snare", "hihat"])

        # Test with invalid main channels (not in channels list)
        metadata = {"channels": "kick,snare,hihat", "main_channels": "kick,snare,hihat,tom1"}
        process_channels_config(metadata)
        self.assertEqual(metadata["channels"], ["kick", "snare", "hihat"])
        self.assertEqual(metadata["main_channels"], ["kick", "snare", "hihat"])

        # Test with empty channels
        metadata = {"channels": "", "main_channels": ""}
        process_channels_config(metadata)
        default_channels_list = [ch.strip() for ch in DEFAULT_CHANNELS.split(",") if ch.strip()]
        default_main_channels_list = [
            ch.strip() for ch in DEFAULT_MAIN_CHANNELS.split(",") if ch.strip()
        ]
        self.assertEqual(metadata["channels"], default_channels_list)
        self.assertEqual(metadata["main_channels"], default_main_channels_list)

        # Test with no channels specified
        metadata = {}
        process_channels_config(metadata)
        default_channels_list = [ch.strip() for ch in DEFAULT_CHANNELS.split(",") if ch.strip()]
        default_main_channels_list = [
            ch.strip() for ch in DEFAULT_MAIN_CHANNELS.split(",") if ch.strip()
        ]
        self.assertEqual(metadata["channels"], default_channels_list)
        self.assertEqual(metadata["main_channels"], default_main_channels_list)

    def test_get_channels_from_metadata(self):
        """Test getting channels from metadata."""
        # Test with channels in metadata
        metadata = {"channels": ["kick", "snare", "hihat"]}
        channels = get_channels_from_metadata(metadata)
        self.assertEqual(channels, ["kick", "snare", "hihat"])

        # Test with no channels in metadata
        metadata = {}
        channels = get_channels_from_metadata(metadata)
        default_channels_list = [ch.strip() for ch in DEFAULT_CHANNELS.split(",") if ch.strip()]
        self.assertEqual(channels, default_channels_list)

    def test_get_main_channels_from_metadata(self):
        """Test getting main channels from metadata."""
        # Test with main channels in metadata
        metadata = {"main_channels": ["kick", "snare"]}
        main_channels = get_main_channels_from_metadata(metadata)
        self.assertEqual(main_channels, ["kick", "snare"])

        # Test with no main channels in metadata
        metadata = {}
        main_channels = get_main_channels_from_metadata(metadata)
        default_main_channels_list = [
            ch.strip() for ch in DEFAULT_MAIN_CHANNELS.split(",") if ch.strip()
        ]
        self.assertEqual(main_channels, default_main_channels_list)


if __name__ == "__main__":
    unittest.main()
