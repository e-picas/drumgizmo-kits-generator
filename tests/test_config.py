#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=broad-exception-caught
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
# pylint: disable-next=wrong-import-position
from drumgizmo_kits_generator.config import (
    CHANNELS,
    DEFAULT_CHANNELS,
    DEFAULT_MAIN_CHANNELS,
    MAIN_CHANNELS,
    _config,
    get_channels,
    get_main_channels,
    read_config_file,
    update_channels_config,
)


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
kit_description="Temporary test description"
kit_notes="Temporary test notes"
kit_author="Test Author"
kit_license="Test License"
kit_website="http://example.com"
kit_samplerate="48000"
kit_logo="test_logo.png"
kit_extra_files="file1.txt,file2.txt"
"""
            )

        # Create an empty config file for testing defaults
        with tempfile.NamedTemporaryFile(delete=False, mode="w") as self.empty_config:
            pass

    def tearDown(self):
        """Cleanup after each test by removing temporary files."""
        if os.path.exists(self.temp_config.name):
            os.unlink(self.temp_config.name)
        if os.path.exists(self.empty_config.name):
            os.unlink(self.empty_config.name)

    def test_read_config_file(self):
        """Test reading a standard configuration file with all expected values."""
        # Read the existing configuration file
        config = read_config_file(self.config_file)

        # Verify the values
        self.assertEqual(config.get("name", ""), "Test Kit", "Kit name should match")
        self.assertEqual(config.get("version", ""), "1.0", "Version should match")
        self.assertEqual(config["description"], "This is a description", "Description should match")
        self.assertEqual(
            config["notes"], "DrumGizmo kit generated for testing purpose", "Notes should match"
        )
        self.assertEqual(config["author"], "Piero", "Author should match")
        self.assertEqual(config["license"], "CC-BY-SA", "License should match")
        self.assertEqual(config["website"], "https://picas.fr/", "Website should match")
        self.assertEqual(config["samplerate"], "44100", "Sample rate should match")
        self.assertEqual(
            config["logo"], "pngtree-music-notes-png-image_8660757.png", "Logo should match"
        )
        self.assertEqual(config["extra_files"], "Lorem Ipsum.pdf", "Extra files should match")

        # Verify the config is a dictionary with the expected number of keys
        self.assertIsInstance(config, dict, "Config should be a dictionary")
        self.assertGreaterEqual(len(config), 10, "Config should have at least 10 keys")

    def test_read_temp_config_file(self):
        """Test reading a temporary configuration file with custom values."""
        # Read the temporary configuration file
        config = read_config_file(self.temp_config.name)

        # Verify the values
        self.assertEqual(config["name"], "Temp Test Kit", "Kit name should match")
        self.assertEqual(config["version"], "2.0", "Version should match")
        self.assertEqual(
            config["description"], "Temporary test description", "Description should match"
        )
        self.assertEqual(config["notes"], "Temporary test notes", "Notes should match")
        self.assertEqual(config["author"], "Test Author", "Author should match")
        self.assertEqual(config["license"], "Test License", "License should match")
        self.assertEqual(config["website"], "http://example.com", "Website should match")
        self.assertEqual(config["samplerate"], "48000", "Sample rate should match")
        self.assertEqual(config["logo"], "test_logo.png", "Logo should match")
        self.assertEqual(config["extra_files"], "file1.txt,file2.txt", "Extra files should match")

    def test_read_empty_config_file(self):
        """Test reading an empty configuration file to verify default values."""
        # Read the empty configuration file
        config = read_config_file(self.empty_config.name)

        # Verify that default values are used
        self.assertEqual(config.get("name", ""), "", "Empty name should be returned")
        self.assertEqual(config.get("version", ""), "", "Empty version should be returned")
        self.assertEqual(config.get("description", ""), "", "Empty description should be returned")

        # Verify the config is a dictionary
        self.assertIsInstance(config, dict, "Config should be a dictionary")

    def test_read_nonexistent_config_file(self):
        """Test reading a non-existent configuration file."""
        # Try to read a non-existent file
        config = read_config_file("/path/to/nonexistent/file.ini")

        # Verify that an empty dictionary is returned
        self.assertIsInstance(config, dict, "Config should be a dictionary")
        self.assertEqual(len(config), 0, "Config should be empty for non-existent file")

    def test_read_config_file_with_channel_options(self):
        """Test reading a configuration file with channel options."""
        # Create a temporary configuration file with channel options
        with tempfile.NamedTemporaryFile(delete=False, mode="w") as temp_config:
            temp_config.write(
                """
kit_name="Channel Test Kit"
kit_version="1.0"
KIT_CHANNELS="Left,Right,Center"
KIT_MAIN_CHANNELS="Center"
"""
            )
            temp_config_name = temp_config.name

        try:
            # Read the configuration file
            config = read_config_file(temp_config_name)

            # Verify the values in the config dictionary
            self.assertEqual(config["name"], "Channel Test Kit", "Kit name should match")
            self.assertEqual(config["version"], "1.0", "Version should match")
            self.assertEqual(config["channels"], "Left,Right,Center", "Channels should match")
            self.assertEqual(config["main_channels"], "Center", "Main channels should match")

            # Verify that the channels were updated in the _config dictionary
            self.assertEqual(
                _config["channels"], ["Left", "Right", "Center"], "Channels should be updated"
            )
            self.assertEqual(
                _config["main_channels"], ["Center"], "Main channels should be updated"
            )

        finally:
            # Clean up
            if os.path.exists(temp_config_name):
                os.unlink(temp_config_name)

    def test_read_config_file_with_special_channel_names(self):
        """Test reading a configuration file with special channel names (spaces, numbers)."""
        # Create a temporary configuration file with special channel names
        with tempfile.NamedTemporaryFile(delete=False, mode="w") as temp_config:
            temp_config.write(
                """
kit_name="Special Channel Test Kit"
kit_version="1.0"
KIT_CHANNELS="Left Channel, Right Channel, Center 123"
KIT_MAIN_CHANNELS="Center 123"
"""
            )
            temp_config_name = temp_config.name

        try:
            # Read the configuration file
            config = read_config_file(temp_config_name)

            # Verify the values in the config dictionary
            self.assertEqual(config["name"], "Special Channel Test Kit", "Kit name should match")
            self.assertEqual(config["version"], "1.0", "Version should match")
            self.assertEqual(
                config["channels"],
                "Left Channel, Right Channel, Center 123",
                "Channels should match",
            )
            self.assertEqual(config["main_channels"], "Center 123", "Main channels should match")

            # Verify that the channels were updated in the _config dictionary
            self.assertEqual(
                _config["channels"],
                ["Left Channel", "Right Channel", "Center 123"],
                "Channels with spaces and numbers should be processed correctly",
            )
            self.assertEqual(
                _config["main_channels"],
                ["Center 123"],
                "Main channels with spaces and numbers should be processed correctly",
            )

        finally:
            # Clean up
            if os.path.exists(temp_config_name):
                os.unlink(temp_config_name)

    def test_channels_constants(self):
        """Test the channel constants to ensure they are correctly defined."""
        # Verify that the channel constants are correctly defined
        self.assertIsInstance(CHANNELS, list, "CHANNELS should be a list")
        self.assertIsInstance(MAIN_CHANNELS, list, "MAIN_CHANNELS should be a list")

        # Verify that there are channels defined
        self.assertGreater(len(CHANNELS), 0, "CHANNELS should not be empty")
        self.assertGreater(len(MAIN_CHANNELS), 0, "MAIN_CHANNELS should not be empty")

        # Verify that the main channels are included in the complete list of channels
        for channel in MAIN_CHANNELS:
            self.assertIn(channel, CHANNELS, f"Channel {channel} should be in CHANNELS list")

        # Verify that all channels are strings
        for channel in CHANNELS:
            self.assertIsInstance(channel, str, "Each channel should be a string")

    def test_get_channels(self):
        """Test the get_channels function."""
        # Test with default channels
        channels = get_channels()
        self.assertIsInstance(channels, list, "Channels should be a list")
        self.assertEqual(channels, CHANNELS, "Default channels should match")

        # Test with custom channels
        custom_channels = ["channel1", "channel2", "channel3"]
        _config["channels"] = custom_channels
        channels = get_channels()
        self.assertIsInstance(channels, list, "Channels should be a list")
        self.assertEqual(channels, custom_channels, "Custom channels should match")

    def test_get_main_channels(self):
        """Test the get_main_channels function."""
        # Test with default main channels
        main_channels = get_main_channels()
        self.assertIsInstance(main_channels, list, "Main channels should be a list")
        self.assertEqual(main_channels, MAIN_CHANNELS, "Default main channels should match")

        # Test with custom main channels
        custom_main_channels = ["main_channel1", "main_channel2", "main_channel3"]
        _config["main_channels"] = custom_main_channels
        main_channels = get_main_channels()
        self.assertIsInstance(main_channels, list, "Main channels should be a list")
        self.assertEqual(main_channels, custom_main_channels, "Custom main channels should match")

    def test_update_channels_config(self):
        """Test the update_channels_config function."""
        # Reset config to defaults before testing
        _config["channels"] = DEFAULT_CHANNELS.copy()
        _config["main_channels"] = DEFAULT_MAIN_CHANNELS.copy()

        # Test with empty metadata (should not change anything)
        metadata = {}
        update_channels_config(metadata)
        self.assertEqual(
            _config["channels"],
            DEFAULT_CHANNELS,
            "Channels should remain default with empty metadata",
        )
        self.assertEqual(
            _config["main_channels"],
            DEFAULT_MAIN_CHANNELS,
            "Main channels should remain default with empty metadata",
        )

        # Test with custom channels in metadata
        metadata = {"channels": "channel1,channel2,channel3", "main_channels": "channel1"}
        update_channels_config(metadata)
        self.assertEqual(
            _config["channels"],
            ["channel1", "channel2", "channel3"],
            "Channels should be updated from metadata",
        )
        self.assertEqual(
            _config["main_channels"], ["channel1"], "Main channels should be updated from metadata"
        )

        # Test with spaces in channel names
        metadata = {"channels": "channel 1, channel 2, channel 3", "main_channels": "channel 1"}
        update_channels_config(metadata)
        self.assertEqual(
            _config["channels"],
            ["channel 1", "channel 2", "channel 3"],
            "Channels with spaces should be handled correctly",
        )
        self.assertEqual(
            _config["main_channels"],
            ["channel 1"],
            "Main channels with spaces should be handled correctly",
        )

        # Test with empty channel values
        metadata = {"channels": "", "main_channels": ""}
        # Reset config to non-default values first
        _config["channels"] = ["test1", "test2"]
        _config["main_channels"] = ["test1"]
        update_channels_config(metadata)
        self.assertEqual(
            _config["channels"],
            ["test1", "test2"],
            "Empty channel string should not update channels",
        )
        self.assertEqual(
            _config["main_channels"],
            ["test1"],
            "Empty main channel string should not update main channels",
        )

    def test_update_channels_config_with_different_types(self):
        """Test the update_channels_config function with different types of values."""
        # Reset config to defaults before testing
        _config["channels"] = DEFAULT_CHANNELS.copy()
        _config["main_channels"] = DEFAULT_MAIN_CHANNELS.copy()

        # Test with numeric values (should be converted to string by the INI parser)
        metadata = {"channels": "123,456", "main_channels": "789"}
        update_channels_config(metadata)
        self.assertEqual(
            _config["channels"],
            ["123", "456"],
            "Numeric channels should be processed as strings",
        )
        self.assertEqual(
            _config["main_channels"],
            ["789"],
            "Numeric main channels should be processed as strings",
        )

        # Test with special characters
        metadata = {"channels": "ch-1,ch_2,ch.3", "main_channels": "ch-1"}
        update_channels_config(metadata)
        self.assertEqual(
            _config["channels"],
            ["ch-1", "ch_2", "ch.3"],
            "Channels with special characters should be processed correctly",
        )
        self.assertEqual(
            _config["main_channels"],
            ["ch-1"],
            "Main channels with special characters should be processed correctly",
        )

        # Test with empty items in the list
        metadata = {"channels": "ch1,,ch2,  ,ch3", "main_channels": "ch1,,"}
        update_channels_config(metadata)
        self.assertEqual(
            _config["channels"],
            ["ch1", "ch2", "ch3"],
            "Empty items in channels list should be filtered out",
        )
        self.assertEqual(
            _config["main_channels"],
            ["ch1"],
            "Empty items in main channels list should be filtered out",
        )

    def test_update_channels_config_with_non_string_values(self):
        """Test the update_channels_config function with non-string values."""
        # Reset config to defaults before testing
        _config["channels"] = DEFAULT_CHANNELS.copy()
        _config["main_channels"] = DEFAULT_MAIN_CHANNELS.copy()

        # Test with non-string values (should be converted to string)
        try:
            metadata = {"channels": 123, "main_channels": 456}
            update_channels_config(metadata)
            # The function should convert non-string values to string
            self.assertEqual(
                _config["channels"],
                ["123"],
                "Non-string channels value should be converted to string",
            )
            self.assertEqual(
                _config["main_channels"],
                ["456"],
                "Non-string main channels value should be converted to string",
            )
        except Exception as e:
            self.fail(f"update_channels_config raised an exception with non-string values: {e}")

        # Test with None values (should be converted to string "None")
        try:
            # Reset config to defaults before testing
            _config["channels"] = DEFAULT_CHANNELS.copy()
            _config["main_channels"] = DEFAULT_MAIN_CHANNELS.copy()

            metadata = {"channels": None, "main_channels": None}
            update_channels_config(metadata)
            # The function should convert None values to string "None"
            self.assertEqual(
                _config["channels"],
                ["None"],
                "None channels value should be converted to string 'None'",
            )
            self.assertEqual(
                _config["main_channels"],
                ["None"],
                "None main channels value should be converted to string 'None'",
            )
        except Exception as e:
            self.fail(f"update_channels_config raised an exception with None values: {e}")

    def test_update_channels_config_with_spaces_and_numbers(self):
        """Test the update_channels_config function with spaces and numbers in channel names."""
        # Reset config to defaults before testing
        _config["channels"] = DEFAULT_CHANNELS.copy()
        _config["main_channels"] = DEFAULT_MAIN_CHANNELS.copy()

        # Test with channel names containing spaces
        metadata = {
            "channels": "Left Channel, Right Channel, Center Channel",
            "main_channels": "Center Channel",
        }
        update_channels_config(metadata)
        self.assertEqual(
            _config["channels"],
            ["Left Channel", "Right Channel", "Center Channel"],
            "Channels with spaces should be processed correctly",
        )
        self.assertEqual(
            _config["main_channels"],
            ["Center Channel"],
            "Main channels with spaces should be processed correctly",
        )

        # Test with channel names containing numbers
        metadata = {"channels": "Channel1, Channel2, Channel3", "main_channels": "Channel1"}
        update_channels_config(metadata)
        self.assertEqual(
            _config["channels"],
            ["Channel1", "Channel2", "Channel3"],
            "Channels with numbers should be processed correctly",
        )
        self.assertEqual(
            _config["main_channels"],
            ["Channel1"],
            "Main channels with numbers should be processed correctly",
        )

        # Test with channel names that are just numbers
        metadata = {"channels": "1, 2, 3", "main_channels": "1"}
        update_channels_config(metadata)
        self.assertEqual(
            _config["channels"],
            ["1", "2", "3"],
            "Channels that are just numbers should be processed correctly",
        )
        self.assertEqual(
            _config["main_channels"],
            ["1"],
            "Main channels that are just numbers should be processed correctly",
        )

        # Test with channel names containing spaces and numbers
        metadata = {"channels": "Channel 1, Channel 2, Channel 3", "main_channels": "Channel 1"}
        update_channels_config(metadata)
        self.assertEqual(
            _config["channels"],
            ["Channel 1", "Channel 2", "Channel 3"],
            "Channels with spaces and numbers should be processed correctly",
        )
        self.assertEqual(
            _config["main_channels"],
            ["Channel 1"],
            "Main channels with spaces and numbers should be processed correctly",
        )

        # Test with channel names containing leading and trailing spaces
        metadata = {
            "channels": "  Channel1  ,  Channel2  ,  Channel3  ",
            "main_channels": "  Channel1  ",
        }
        update_channels_config(metadata)
        self.assertEqual(
            _config["channels"],
            ["Channel1", "Channel2", "Channel3"],
            "Channels with leading and trailing spaces should be processed correctly",
        )
        self.assertEqual(
            _config["main_channels"],
            ["Channel1"],
            "Main channels with leading and trailing spaces should be processed correctly",
        )


if __name__ == "__main__":
    unittest.main()
