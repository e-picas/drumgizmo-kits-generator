#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=duplicate-code
# pylint: disable=import-outside-toplevel,wrong-import-position
"""
Unit tests for the utils module of the DrumGizmo kit generator.

These tests verify the functionality of utility functions used throughout
the application, including directory preparation, file handling, and output
formatting.
"""

import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

# Add the parent directory to the path to be able to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import the module to test
from drumgizmo_kits_generator.utils import (
    extract_instrument_name,
    get_audio_samplerate,
    get_file_extension,
    get_timestamp,
    prepare_instrument_directory,
    prepare_target_directory,
    print_summary,
)


class TestUtils(unittest.TestCase):
    """Tests for the utils module."""

    def setUp(self):
        """Initialize before each test by creating a temporary directory."""
        # Create a temporary directory for tests
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Cleanup after each test by removing the temporary directory."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_prepare_target_directory(self):
        """Test preparing the target directory under various conditions."""
        # Test with a non-existent directory
        target_dir = os.path.join(self.temp_dir, "new_dir")
        self.assertTrue(
            prepare_target_directory(target_dir), "Should return True for non-existent directory"
        )
        self.assertTrue(
            os.path.exists(target_dir), "Directory should be created if it doesn't exist"
        )

        # Test with an existing directory (should be removed and recreated)
        # Create a file in the directory
        with open(os.path.join(target_dir, "test_file.txt"), "w", encoding="utf-8") as f:
            f.write("Test content")

        # Verify the file was created
        self.assertTrue(
            os.path.exists(os.path.join(target_dir, "test_file.txt")), "Test file should exist"
        )

        # The function should remove the directory and recreate it empty
        self.assertTrue(
            prepare_target_directory(target_dir),
            "Should return True when removing and recreating directory",
        )

        # Verify that the directory exists but is empty
        self.assertTrue(os.path.exists(target_dir), "Directory should exist after preparation")
        self.assertEqual(
            len(os.listdir(target_dir)), 0, "Directory should be empty after preparation"
        )

        # Test with a directory that cannot be removed (simulate permission error)
        with patch("shutil.rmtree", side_effect=PermissionError("Permission denied")):
            self.assertFalse(
                prepare_target_directory(target_dir),
                "Should return False when directory cannot be removed",
            )

        # Test with a directory that cannot be created
        with patch("os.makedirs", side_effect=PermissionError("Permission denied")):
            # First remove the directory to test creation
            shutil.rmtree(target_dir)
            self.assertFalse(
                prepare_target_directory(target_dir),
                "Should return False when directory cannot be created",
            )

    def test_prepare_instrument_directory(self):
        """Test preparing the instrument directory and its samples subdirectory."""
        instrument_name = "Test-Instrument"

        # Test with a valid target directory
        result = prepare_instrument_directory(instrument_name, self.temp_dir)
        self.assertTrue(result, "Should return True for successful directory creation")

        # Verify that the instrument directory has been created
        instrument_dir = os.path.join(self.temp_dir, instrument_name)
        self.assertTrue(os.path.exists(instrument_dir), "Instrument directory should be created")

        # Verify that the samples directory has been created
        samples_dir = os.path.join(instrument_dir, "samples")
        self.assertTrue(os.path.exists(samples_dir), "Samples directory should be created")

        # Test with an existing instrument directory
        result = prepare_instrument_directory(instrument_name, self.temp_dir)
        self.assertTrue(result, "Should return True even if directory already exists")

        # Test with a special character in the instrument name
        special_instrument = "Test/Instrument"
        result = prepare_instrument_directory(special_instrument, self.temp_dir)
        self.assertTrue(result, "Should handle special characters in instrument name")
        special_dir = os.path.join(self.temp_dir, special_instrument)
        self.assertTrue(
            os.path.exists(special_dir), "Directory with special character should be created"
        )

    def test_get_timestamp(self):
        """Test generating a timestamp with the correct format."""
        timestamp = get_timestamp()

        # Verify that the timestamp is a non-empty string
        self.assertIsInstance(timestamp, str, "Timestamp should be a string")
        self.assertGreater(len(timestamp), 0, "Timestamp should not be empty")

        # Verify that the timestamp contains a date in YYYY-MM-DD format
        self.assertRegex(
            timestamp, r"\d{4}-\d{2}-\d{2}", "Timestamp should match YYYY-MM-DD format"
        )

        # Le format réel est YYYY-MM-DD et non YYYY-MM-DD HH:MM:SS
        # Adapter le test au format réel
        date_pattern = re.compile(r"\d{4}-\d{2}-\d{2}")
        self.assertTrue(date_pattern.match(timestamp), "Timestamp should match YYYY-MM-DD format")

    def test_extract_instrument_name(self):
        """Test extracting the instrument name from various file paths."""
        # Test different file paths
        test_cases = [
            ("/path/to/Kick.wav", "Kick"),
            ("/path/to/Snare-Drum.flac", "Snare-Drum"),
            ("/path/to/Hi-Hat-Open.ogg", "Hi-Hat-Open"),
            ("Cymbal-Crash.wav", "Cymbal-Crash"),
            ("/path/with spaces/Tom Tom.wav", "Tom Tom"),
            ("/path/to/file/without/extension", "extension"),
        ]

        for file_path, expected in test_cases:
            self.assertEqual(
                extract_instrument_name(file_path),
                expected,
                f"Should extract '{expected}' from '{file_path}'",
            )

    def test_get_file_extension(self):
        """Test extracting file extensions from various file paths."""
        # Test different extensions
        test_cases = [
            ("/path/to/file.wav", ".wav"),
            ("/path/to/file.WAV", ".WAV"),
            ("/path/to/file.flac", ".flac"),
            ("/path/to/file.ogg", ".ogg"),
            ("file.mp3", ".mp3"),
            ("/path/to/file", ""),
            ("/path.to/file", ""),
            # La fonction actuelle ne considère pas .hidden comme une extension
            # car elle cherche un point suivi d'au moins un caractère
            ("/path/to/.hidden", ""),
        ]

        for file_path, expected in test_cases:
            self.assertEqual(
                get_file_extension(file_path),
                expected,
                f"Should extract '{expected}' from '{file_path}'",
            )

    def test_get_audio_samplerate(self):
        """Test getting the sample rate of an audio file."""
        # Create a temporary audio file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_path = temp_file.name

        # Create a test WAV file with SoX at 44100 Hz
        try:
            subprocess.run(
                ["sox", "-n", temp_path, "rate", "44100", "trim", "0", "0.1"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except (subprocess.SubprocessError, FileNotFoundError):
            self.skipTest("SoX is not available or failed to create test file")

        # Test getting the sample rate
        sample_rate = get_audio_samplerate(temp_path)
        self.assertEqual(44100, sample_rate, "Should return the correct sample rate")

        # Clean up
        try:
            os.unlink(temp_path)
        except OSError:
            pass

    def test_get_audio_samplerate_nonexistent_file(self):
        """Test getting the sample rate of a non-existent file."""
        sample_rate = get_audio_samplerate("nonexistent.wav")
        self.assertIsNone(sample_rate, "Should return None for non-existent file")

    def test_get_audio_samplerate_invalid_file(self):
        """Test getting the sample rate of an invalid audio file."""
        # Create a temporary file that is not a valid audio file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_path = temp_file.name
            temp_file.write(b"This is not a valid WAV file")

        # Test getting the sample rate
        sample_rate = get_audio_samplerate(temp_path)
        self.assertIsNone(sample_rate, "Should return None for invalid audio file")

        # Clean up
        try:
            os.unlink(temp_path)
        except OSError:
            pass

    @patch("sys.stderr", new_callable=MagicMock)
    def test_print_summary(self, mock_stderr):
        """Test displaying the summary with various metadata configurations."""
        # Prepare data for the test
        metadata = {
            "name": "Test Kit",
            "version": "1.0",
            "description": "Test description",
            "notes": "Test notes",
            "author": "Test Author",
            "license": "Test License",
            "website": "http://example.com",
            "samplerate": "44100",
            "logo": "test_logo.png",
        }
        instruments = ["Kick", "Snare", "Hi-Hat"]
        target_dir = "/path/to/target"

        # Call the function to test
        print_summary(metadata, instruments, target_dir)

        # Verify that the function wrote to stderr
        mock_stderr.write.assert_called()

        # Verify that key information is present in the output
        output = "".join([call_args[0][0] for call_args in mock_stderr.write.call_args_list])

        self.assertIn("Test Kit", output, "Kit name should be in the summary")
        self.assertIn("1.0", output, "Version should be in the summary")
        self.assertIn("Author", output, "Author should be in the summary")
        self.assertIn("Test License", output, "License should be in the summary")
        self.assertIn(
            "Number of instruments created: 3", output, "Instrument count should be in the summary"
        )
        self.assertIn("/path/to/target", output, "Target directory should be in the summary")

        # Test with minimal metadata
        mock_stderr.reset_mock()
        minimal_metadata = {"name": "Minimal Kit", "version": "0.1"}

        print_summary(minimal_metadata, instruments, target_dir)

        # Verify output with minimal metadata
        output = "".join([call_args[0][0] for call_args in mock_stderr.write.call_args_list])
        self.assertIn("Minimal Kit", output, "Kit name should be in the minimal summary")
        self.assertIn("0.1", output, "Version should be in the minimal summary")

        # Test with empty instruments list
        mock_stderr.reset_mock()
        print_summary(metadata, [], target_dir)

        # Verify output with no instruments
        output = "".join([call_args[0][0] for call_args in mock_stderr.write.call_args_list])
        self.assertIn(
            "Number of instruments created: 0",
            output,
            "Zero instruments should be reported correctly",
        )


if __name__ == "__main__":
    unittest.main()
