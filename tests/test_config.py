#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for the configuration module of the DrumGizmo kit generator.

These tests verify the functionality of configuration file reading and
the correctness of the channel constants used in the application.
"""

import os
import sys
import unittest
import tempfile

# Add the parent directory to the path to be able to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the module to test
# pylint: disable-next=wrong-import-position
from config import read_config_file, CHANNELS, MAIN_CHANNELS

class TestConfig(unittest.TestCase):
    """Tests for the configuration module."""

    def setUp(self):
        """Initialize before each test by creating test configuration files."""
        self.source_dir = os.path.join(os.path.dirname(__file__), 'sources')
        self.config_file = os.path.join(self.source_dir, 'drumgizmo-kit.ini')

        # Create a temporary configuration file for tests
        # pylint: disable-next=consider-using-with
        self.temp_config = tempfile.NamedTemporaryFile(delete=False, mode='w')
        # pylint: disable-next=consider-using-with
        self.temp_config.write('''
KIT_NAME="Temp Test Kit"
KIT_VERSION="2.0"
KIT_DESCRIPTION="Temporary test description"
KIT_NOTES="Temporary test notes"
KIT_AUTHOR="Test Author"
KIT_LICENSE="Test License"
KIT_WEBSITE="http://example.com"
KIT_SAMPLERATE="48000"
KIT_INSTRUMENT_PREFIX="TempTest"
KIT_LOGO="test_logo.png"
KIT_EXTRA_FILES="file1.txt,file2.txt"
''')
        self.temp_config.close()

        # Create an empty config file for testing defaults
        # pylint: disable-next=consider-using-with
        self.empty_config = tempfile.NamedTemporaryFile(delete=False, mode='w')
        self.empty_config.close()

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
        self.assertEqual(config.get('name', ''), 'Test Kit', "Kit name should match")
        self.assertEqual(config.get('version', ''), '1.0', "Version should match")
        self.assertEqual(config['description'], 'This is a description', "Description should match")
        self.assertEqual(config['notes'], 'DrumGizmo kit generated for testing purpose', "Notes should match")
        self.assertEqual(config['author'], 'Piero', "Author should match")
        self.assertEqual(config['license'], 'CC-BY-SA', "License should match")
        self.assertEqual(config['website'], 'https://picas.fr/', "Website should match")
        self.assertEqual(config['samplerate'], '44100', "Sample rate should match")
        self.assertEqual(config['instrument_prefix'], 'Test', "Instrument prefix should match")
        self.assertEqual(config['logo'], 'pngtree-music-notes-png-image_8660757.png', "Logo should match")
        self.assertEqual(config['extra_files'], 'Lorem Ipsum.pdf', "Extra files should match")

        # Verify the config is a dictionary with the expected number of keys
        self.assertIsInstance(config, dict, "Config should be a dictionary")
        self.assertGreaterEqual(len(config), 11, "Config should have at least 11 keys")

    def test_read_temp_config_file(self):
        """Test reading a temporary configuration file with custom values."""
        # Read the temporary configuration file
        config = read_config_file(self.temp_config.name)

        # Verify the values
        self.assertEqual(config['name'], 'Temp Test Kit', "Kit name should match")
        self.assertEqual(config['version'], '2.0', "Version should match")
        self.assertEqual(config['description'], 'Temporary test description', "Description should match")
        self.assertEqual(config['notes'], 'Temporary test notes', "Notes should match")
        self.assertEqual(config['author'], 'Test Author', "Author should match")
        self.assertEqual(config['license'], 'Test License', "License should match")
        self.assertEqual(config['website'], 'http://example.com', "Website should match")
        self.assertEqual(config['samplerate'], '48000', "Sample rate should match")
        self.assertEqual(config['instrument_prefix'], 'TempTest', "Instrument prefix should match")
        self.assertEqual(config['logo'], 'test_logo.png', "Logo should match")
        self.assertEqual(config['extra_files'], 'file1.txt,file2.txt', "Extra files should match")

    def test_read_empty_config_file(self):
        """Test reading an empty configuration file to verify default values."""
        # Read the empty configuration file
        config = read_config_file(self.empty_config.name)

        # Verify that default values are used
        self.assertEqual(config.get('name', ''), '', "Empty name should be returned")
        self.assertEqual(config.get('version', ''), '', "Empty version should be returned")
        self.assertEqual(config.get('description', ''), '', "Empty description should be returned")

        # Verify the config is a dictionary
        self.assertIsInstance(config, dict, "Config should be a dictionary")

    def test_read_nonexistent_config_file(self):
        """Test reading a non-existent configuration file."""
        # Try to read a non-existent file
        config = read_config_file('/path/to/nonexistent/file.ini')

        # Verify that an empty dictionary is returned
        self.assertIsInstance(config, dict, "Config should be a dictionary")
        self.assertEqual(len(config), 0, "Config should be empty for non-existent file")

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


if __name__ == '__main__':
    unittest.main()
