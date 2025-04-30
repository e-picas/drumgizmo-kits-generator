#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-locals
# pylint: disable=broad-exception-caught
# pylint: disable=redundant-unittest-assert
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
# pylint: disable=unused-variable
# pylint: disable=unspecified-encoding
# pylint: disable=consider-using-with
# pylint: disable=import-outside-toplevel,wrong-import-position
"""
Additional tests for the config module to improve test coverage.
"""

import os
import sys
import tempfile
import unittest
from io import StringIO
from unittest.mock import patch

# Add the parent directory to the path to be able to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from drumgizmo_kits_generator.config import (
    _process_channel_list,
    parse_config_line,
    read_config_file,
)


class TestConfigAdditional(unittest.TestCase):
    """Additional tests for the config module to improve test coverage."""

    def setUp(self):
        """Initialize before each test."""
        # Create a temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()

        # Create a mock for sys.stderr to capture output
        self.stderr_patcher = patch("sys.stderr", new_callable=StringIO)
        self.mock_stderr = self.stderr_patcher.start()

    def tearDown(self):
        """Clean up after each test."""
        # Stop the stderr patcher
        self.stderr_patcher.stop()

        # Remove the temporary directory
        if os.path.exists(self.temp_dir):
            os.rmdir(self.temp_dir)

    def test_parse_config_line_with_quotes_format(self):
        """Test parse_config_line with KEY_NAME="value" format."""
        # Test with KEY_NAME="value" format
        line = 'kit_name="Test Kit"'
        key, value = parse_config_line(line)
        self.assertEqual(key, "kit_name", "Key should be 'kit_name'")
        self.assertEqual(value, "Test Kit", "Value should be 'Test Kit'")

    def test_parse_config_line_with_quotes_and_spaces(self):
        """Test parse_config_line with KEY_NAME = "value" format."""
        # Test with KEY_NAME = "value" format
        line = 'kit_name = "Test Kit"'
        key, value = parse_config_line(line)
        self.assertEqual(key, "kit_name", "Key should be 'kit_name'")
        self.assertEqual(value, "Test Kit", "Value should be 'Test Kit'")

    def test_parse_config_line_with_invalid_format(self):
        """Test parse_config_line with invalid format."""
        # Test with a truly invalid format
        line = "kit_name Test Kit"  # No equals sign or quotes
        key, value = parse_config_line(line)
        self.assertEqual(key, "", "Key should be empty for invalid format")
        self.assertEqual(value, "", "Value should be empty for invalid format")

    def test_read_config_file_unicode_decode_error(self):
        """Test read_config_file with a UnicodeDecodeError."""
        # Test with a UnicodeDecodeError
        config_file = os.path.join(self.temp_dir, "config.ini")

        # Mock os.path.isfile to return True
        with patch("os.path.isfile", return_value=True):
            # Mock open to raise a UnicodeDecodeError
            with patch("builtins.open") as mock_file:
                mock_file.side_effect = UnicodeDecodeError(
                    "utf-8", b"\x80", 0, 1, "invalid start byte"
                )

                # Call read_config_file
                result = read_config_file(config_file)

                # Check that the result is an empty dictionary
                self.assertEqual(
                    result, {}, "Should return an empty dictionary when a UnicodeDecodeError occurs"
                )

                # Check that the output contains the expected error message
                output = self.mock_stderr.getvalue()
                self.assertIn("Unicode decode error", output)

    def test_read_config_file_permission_error(self):
        """Test read_config_file with a PermissionError."""
        # Test with a PermissionError
        config_file = os.path.join(self.temp_dir, "config.ini")

        # Mock os.path.isfile to return True
        with patch("os.path.isfile", return_value=True):
            # Mock open to raise a PermissionError
            with patch("builtins.open") as mock_file:
                mock_file.side_effect = PermissionError("Permission denied")

                # Call read_config_file
                result = read_config_file(config_file)

                # Check that the result is an empty dictionary
                self.assertEqual(
                    result, {}, "Should return an empty dictionary when a PermissionError occurs"
                )

                # Check that the output contains the expected error message
                output = self.mock_stderr.getvalue()
                self.assertIn("Permission denied", output)

    def test_read_config_file_os_error(self):
        """Test read_config_file with an OSError."""
        # Test with an OSError
        config_file = os.path.join(self.temp_dir, "config.ini")

        # Mock os.path.isfile to return True
        with patch("os.path.isfile", return_value=True):
            # Mock open to raise an OSError
            with patch("builtins.open") as mock_file:
                mock_file.side_effect = OSError("File system error")

                # Call read_config_file
                result = read_config_file(config_file)

                # Check that the result is an empty dictionary
                self.assertEqual(
                    result, {}, "Should return an empty dictionary when an OSError occurs"
                )

                # Check that the output contains the expected error message
                output = self.mock_stderr.getvalue()
                self.assertIn("File system error", output)

    def test_process_channel_list_with_empty_value(self):
        """Test _process_channel_list with an empty value."""
        # Test with an empty value
        channels_value = ""
        default_channels = "AmbL,AmbR"
        channel_type = "channels"

        # Call _process_channel_list
        result = _process_channel_list(channels_value, default_channels, channel_type)

        # Check that the result is equivalent to the default channels processed as a list
        expected_result = ["AmbL", "AmbR"]
        self.assertEqual(
            result, expected_result, "Should return default channels when the value is empty"
        )

        # Check that the output contains the expected message
        output = self.mock_stderr.getvalue()
        self.assertIn("Empty channels list", output)

    def test_process_channel_list_with_valid_value(self):
        """Test _process_channel_list with a valid value."""
        # Test with a valid value
        channels_value = "L,R,C"
        default_channels = ["AmbL", "AmbR"]
        channel_type = "channels"

        # Call _process_channel_list
        result = _process_channel_list(channels_value, default_channels, channel_type)

        # Check that the result contains the expected channels
        self.assertEqual(result, ["L", "R", "C"], "Should return the specified channels")

        # Check that the output contains the expected message
        output = self.mock_stderr.getvalue()
        self.assertIn("Using custom channels from metadata", output)


if __name__ == "__main__":
    unittest.main()
