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
Additional tests for the utils module to improve test coverage.
"""

import os
import shutil
import sys
import tempfile
import unittest
from io import StringIO
from unittest.mock import patch

# Add the parent directory to the path to be able to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from drumgizmo_kits_generator.utils import (
    extract_instrument_name,
    get_file_extension,
    prepare_instrument_directory,
    prepare_target_directory,
    print_summary,
)


class TestUtilsAdditional(unittest.TestCase):
    """Additional tests for the utils module to improve test coverage."""

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
            shutil.rmtree(self.temp_dir)

    def test_extract_instrument_name_with_path(self):
        """Test extract_instrument_name with a file path."""
        # Test with a file path
        file_path = "/path/to/Kick.wav"
        instrument_name = extract_instrument_name(file_path)
        self.assertEqual(instrument_name, "Kick", "Should extract 'Kick' from '/path/to/Kick.wav'")

    def test_extract_instrument_name_with_filename_only(self):
        """Test extract_instrument_name with a filename only."""
        # Test with a filename only
        file_path = "Snare.wav"
        instrument_name = extract_instrument_name(file_path)
        self.assertEqual(instrument_name, "Snare", "Should extract 'Snare' from 'Snare.wav'")

    def test_extract_instrument_name_with_complex_filename(self):
        """Test extract_instrument_name with a complex filename."""
        # Test with a complex filename
        file_path = "Hi-Hat_Open.flac"
        instrument_name = extract_instrument_name(file_path)
        self.assertEqual(
            instrument_name, "Hi-Hat_Open", "Should extract 'Hi-Hat_Open' from 'Hi-Hat_Open.flac'"
        )

    def test_get_file_extension_with_path(self):
        """Test get_file_extension with a file path."""
        # Test with a file path
        file_path = "/path/to/Kick.wav"
        extension = get_file_extension(file_path)
        self.assertEqual(extension, ".wav", "Should extract '.wav' from '/path/to/Kick.wav'")

    def test_get_file_extension_with_filename_only(self):
        """Test get_file_extension with a filename only."""
        # Test with a filename only
        file_path = "Snare.flac"
        extension = get_file_extension(file_path)
        self.assertEqual(extension, ".flac", "Should extract '.flac' from 'Snare.flac'")

    def test_get_file_extension_with_no_extension(self):
        """Test get_file_extension with a file without extension."""
        # Test with a file without extension
        file_path = "Kick"
        extension = get_file_extension(file_path)
        self.assertEqual(extension, "", "Should extract '' from 'Kick'")

    def test_prepare_instrument_directory_success(self):
        """Test prepare_instrument_directory with a valid directory."""
        # Test with a valid directory
        instrument = "Kick"
        target_dir = self.temp_dir
        result = prepare_instrument_directory(instrument, target_dir)
        self.assertTrue(result, "Should return True when successful")

        # Check that the directories were created
        instrument_dir = os.path.join(target_dir, instrument)
        samples_dir = os.path.join(instrument_dir, "samples")
        self.assertTrue(os.path.exists(instrument_dir), "Instrument directory should exist")
        self.assertTrue(os.path.exists(samples_dir), "Samples directory should exist")

    def test_prepare_instrument_directory_permission_error(self):
        """Test prepare_instrument_directory with a permission error."""
        # Test with a permission error
        instrument = "Kick"
        target_dir = self.temp_dir

        # Mock os.makedirs to raise a PermissionError
        with patch("os.makedirs") as mock_makedirs:
            mock_makedirs.side_effect = PermissionError("Permission denied")
            result = prepare_instrument_directory(instrument, target_dir)
            self.assertFalse(result, "Should return False when a permission error occurs")
            self.assertIn("Permission denied", self.mock_stderr.getvalue())

    def test_prepare_instrument_directory_os_error(self):
        """Test prepare_instrument_directory with an OS error."""
        # Test with an OS error
        instrument = "Kick"
        target_dir = self.temp_dir

        # Mock os.makedirs to raise an OSError
        with patch("os.makedirs") as mock_makedirs:
            mock_makedirs.side_effect = OSError("File system error")
            result = prepare_instrument_directory(instrument, target_dir)
            self.assertFalse(result, "Should return False when an OS error occurs")
            self.assertIn("File system error", self.mock_stderr.getvalue())

    def test_prepare_target_directory_success(self):
        """Test prepare_target_directory with a valid directory."""
        # Test with a valid directory
        target_dir = os.path.join(self.temp_dir, "target")
        result = prepare_target_directory(target_dir)
        self.assertTrue(result, "Should return True when successful")
        self.assertTrue(os.path.exists(target_dir), "Target directory should exist")

    def test_prepare_target_directory_existing_dir(self):
        """Test prepare_target_directory with an existing directory."""
        # Test with an existing directory
        target_dir = os.path.join(self.temp_dir, "target")
        os.makedirs(target_dir)
        result = prepare_target_directory(target_dir)
        self.assertTrue(result, "Should return True when successful")
        self.assertTrue(os.path.exists(target_dir), "Target directory should exist")

    def test_prepare_target_directory_permission_error_rmtree(self):
        """Test prepare_target_directory with a permission error during rmtree."""
        # Test with a permission error during rmtree
        target_dir = os.path.join(self.temp_dir, "target")
        os.makedirs(target_dir)

        # Mock shutil.rmtree to raise a PermissionError
        with patch("shutil.rmtree") as mock_rmtree:
            mock_rmtree.side_effect = PermissionError("Permission denied")
            result = prepare_target_directory(target_dir)
            self.assertFalse(result, "Should return False when a permission error occurs")
            self.assertIn("Permission denied", self.mock_stderr.getvalue())

    def test_prepare_target_directory_shutil_error(self):
        """Test prepare_target_directory with a shutil error."""
        # Test with a shutil error
        target_dir = os.path.join(self.temp_dir, "target")
        os.makedirs(target_dir)

        # Mock shutil.rmtree to raise a shutil.Error
        with patch("shutil.rmtree") as mock_rmtree:
            mock_rmtree.side_effect = shutil.Error("Shutil error")
            result = prepare_target_directory(target_dir)
            self.assertFalse(result, "Should return False when a shutil error occurs")
            self.assertIn("Shutil error", self.mock_stderr.getvalue())

    def test_prepare_target_directory_os_error_rmtree(self):
        """Test prepare_target_directory with an OS error during rmtree."""
        # Test with an OS error during rmtree
        target_dir = os.path.join(self.temp_dir, "target")
        os.makedirs(target_dir)

        # Mock shutil.rmtree to raise an OSError
        with patch("shutil.rmtree") as mock_rmtree:
            mock_rmtree.side_effect = OSError("File system error")
            result = prepare_target_directory(target_dir)
            self.assertFalse(result, "Should return False when an OS error occurs")
            self.assertIn("File system error", self.mock_stderr.getvalue())

    def test_prepare_target_directory_permission_error_makedirs(self):
        """Test prepare_target_directory with a permission error during makedirs."""
        # Test with a permission error during makedirs
        target_dir = os.path.join(self.temp_dir, "target")

        # Mock os.makedirs to raise a PermissionError
        with patch("os.makedirs") as mock_makedirs:
            mock_makedirs.side_effect = PermissionError("Permission denied")
            result = prepare_target_directory(target_dir)
            self.assertFalse(result, "Should return False when a permission error occurs")
            self.assertIn("Permission denied", self.mock_stderr.getvalue())

    def test_prepare_target_directory_os_error_makedirs(self):
        """Test prepare_target_directory with an OS error during makedirs."""
        # Test with an OS error during makedirs
        target_dir = os.path.join(self.temp_dir, "target")

        # Mock os.makedirs to raise an OSError
        with patch("os.makedirs") as mock_makedirs:
            mock_makedirs.side_effect = OSError("File system error")
            result = prepare_target_directory(target_dir)
            self.assertFalse(result, "Should return False when an OS error occurs")
            self.assertIn("File system error", self.mock_stderr.getvalue())

    def test_print_summary(self):
        """Test print_summary."""
        # Test print_summary
        metadata = {
            "name": "Test Kit",
            "version": "1.0",
            "description": "Test description",
            "notes": "Test notes",
            "author": "Test Author",
            "license": "CC-BY-SA",
            "samplerate": "44100",
            "website": "https://example.com",
            "logo": "logo.png",
        }
        instruments = ["Kick", "Snare", "Hi-Hat"]
        target_dir = "/path/to/target"

        # Call print_summary
        print_summary(metadata, instruments, target_dir)

        # Check that the output contains all the expected information
        output = self.mock_stderr.getvalue()
        self.assertIn("Processing complete", output)
        self.assertIn("Number of instruments created: 3", output)
        self.assertIn("drumkit.xml", output)
        self.assertIn("midimap.xml", output)
        self.assertIn("Name: Test Kit", output)
        self.assertIn("Version: 1.0", output)
        self.assertIn("Description: Test description", output)
        self.assertIn("Notes: Test notes", output)
        self.assertIn("Author: Test Author", output)
        self.assertIn("License: CC-BY-SA", output)
        self.assertIn("Sample rate: 44100 Hz", output)
        self.assertIn("Website: https://example.com", output)
        self.assertIn("Logo: logo.png", output)

    def test_print_summary_missing_values(self):
        """Test print_summary with missing values."""
        # Test print_summary with missing values
        metadata = {}
        instruments = ["Kick", "Snare", "Hi-Hat"]
        target_dir = "/path/to/target"

        # Call print_summary
        print_summary(metadata, instruments, target_dir)

        # Check that the output contains default values for missing information
        output = self.mock_stderr.getvalue()
        self.assertIn("Name: Unknown", output)
        self.assertIn("Version: Unknown", output)
        self.assertIn("Description: Unknown", output)
        self.assertIn("Notes: None", output)
        self.assertIn("Author: Unknown", output)
        self.assertIn("License: Unknown", output)
        self.assertIn("Sample rate: Unknown Hz", output)
        self.assertIn("Website: None", output)
        self.assertIn("Logo: None", output)


if __name__ == "__main__":
    unittest.main()
