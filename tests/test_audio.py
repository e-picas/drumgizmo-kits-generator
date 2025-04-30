#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=unspecified-encoding
"""
Unit tests for the audio module of the DrumGizmo kit generator.

These tests verify the functionality of audio file handling operations
including finding, copying, and creating volume variations of audio files.
"""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

# Add the parent directory to the path to be able to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import the module to test
# pylint: disable-next=wrong-import-position
from drumgizmo_kits_generator.audio import (
    convert_sample_rate,
    copy_sample_file,
    create_volume_variations,
    find_audio_files,
)


class TestAudio(unittest.TestCase):
    """Tests for the audio module."""

    def setUp(self):
        """Initialize before each test by creating a temporary directory and test files."""
        # Create a temporary directory for tests
        self.temp_dir = tempfile.mkdtemp()
        self.source_dir = os.path.join(os.path.dirname(__file__), "sources")

        # Create test audio files
        self.test_files = [
            os.path.join(self.temp_dir, "test1.wav"),
            os.path.join(self.temp_dir, "test2.flac"),
            os.path.join(self.temp_dir, "test3.ogg"),
            os.path.join(self.temp_dir, "test4.txt"),  # Non-audio file
        ]

        for file_path in self.test_files:
            with open(file_path, "w") as f:
                f.write("Test content")

    def tearDown(self):
        """Cleanup after each test by removing the temporary directory."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_find_audio_files(self):
        """Test finding audio files with different extension filters."""
        # Test with default extensions
        audio_files = find_audio_files(self.temp_dir, extensions=["wav", "flac", "ogg"])
        self.assertEqual(
            len(audio_files), 3, "Should find exactly 3 audio files with default extensions"
        )
        self.assertIn(
            os.path.join(self.temp_dir, "test1.wav"), audio_files, "WAV file should be included"
        )
        self.assertIn(
            os.path.join(self.temp_dir, "test2.flac"), audio_files, "FLAC file should be included"
        )
        self.assertIn(
            os.path.join(self.temp_dir, "test3.ogg"), audio_files, "OGG file should be included"
        )
        self.assertNotIn(
            os.path.join(self.temp_dir, "test4.txt"),
            audio_files,
            "Text file should not be included",
        )

        # Test with specific extensions
        audio_files = find_audio_files(self.temp_dir, extensions=["wav"])
        self.assertEqual(len(audio_files), 1, "Should find only 1 file with WAV extension")
        self.assertIn(
            os.path.join(self.temp_dir, "test1.wav"),
            audio_files,
            "Only WAV file should be included",
        )

        # Test with empty directory
        empty_dir = os.path.join(self.temp_dir, "empty")
        os.makedirs(empty_dir, exist_ok=True)
        audio_files = find_audio_files(empty_dir, extensions=["wav", "flac", "ogg"])
        self.assertEqual(len(audio_files), 0, "Should find no files in empty directory")

    @patch("shutil.copy2")
    def test_copy_sample_file(self, mock_copy2):
        """Test copying an audio file to a target location."""
        # Configure the mock
        mock_copy2.return_value = True

        # Test with a valid file
        source_file = os.path.join(self.temp_dir, "test1.wav")
        target_dir = os.path.join(self.temp_dir, "target")
        os.makedirs(target_dir, exist_ok=True)
        target_file = os.path.join(target_dir, "test1.wav")

        # Call the function
        result = copy_sample_file(source_file, target_file)

        # Verify the result
        self.assertTrue(result, "Function should return True for successful copy")
        mock_copy2.assert_called_once_with(source_file, target_file)

    @patch("shutil.copy2")
    def test_copy_sample_file_nonexistent(self, mock_copy2):
        """Test copying a non-existent audio file."""
        # Configure the mock to raise FileNotFoundError
        mock_copy2.side_effect = FileNotFoundError("File not found")

        # Test with a non-existent file
        source_file = os.path.join(self.temp_dir, "nonexistent.wav")
        target_file = os.path.join(self.temp_dir, "target", "nonexistent.wav")

        # Call the function
        result = copy_sample_file(source_file, target_file)

        # Verify the result
        self.assertFalse(result, "Function should return False for failed copy")
        mock_copy2.assert_called_once_with(source_file, target_file)

    @patch("drumgizmo_kits_generator.audio.subprocess.run")
    def test_create_volume_variations(self, mock_run):
        """Test creating volume variations for a sample."""
        # Create a test instrument directory
        instrument = "test_instrument"
        instrument_dir = os.path.join(self.temp_dir, instrument)
        os.makedirs(instrument_dir, exist_ok=True)

        # Create a samples directory
        samples_dir = os.path.join(instrument_dir, "samples")
        os.makedirs(samples_dir, exist_ok=True)

        # Create a sample file
        sample_file = os.path.join(samples_dir, f"1-{instrument}.wav")
        # pylint: disable-next=unspecified-encoding
        with open(sample_file, "w") as f:
            f.write("dummy audio data")

        # Mock the subprocess.run function
        mock_run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout=b"", stderr=b""
        )

        # Call the function with default velocity levels (10)
        create_volume_variations(instrument, self.temp_dir, ".wav")

        # Check that subprocess.run was called 9 times (for samples 2-10)
        self.assertEqual(mock_run.call_count, 9, "Should create 9 volume variations")

        # Test with custom velocity levels
        mock_run.reset_mock()
        create_volume_variations(instrument, self.temp_dir, ".wav", velocity_levels=5)

        # Check that subprocess.run was called 4 times (for samples 2-5)
        self.assertEqual(mock_run.call_count, 4, "Should create 4 volume variations")

        # Test with only 1 velocity level (should skip variations)
        mock_run.reset_mock()
        create_volume_variations(instrument, self.temp_dir, ".wav", velocity_levels=1)

        # Check that subprocess.run was not called
        self.assertEqual(mock_run.call_count, 0, "Should not create any variations")

    @patch("drumgizmo_kits_generator.audio.subprocess.run")
    def test_create_volume_variations_called_process_error(self, mock_subprocess_run):
        """Test error handling in create_volume_variations with CalledProcessError."""
        # Create a test instrument directory
        instrument_name = "test_instrument"
        instrument_dir = os.path.join(self.temp_dir, instrument_name)
        samples_dir = os.path.join(instrument_dir, "samples")
        os.makedirs(samples_dir, exist_ok=True)

        # Create a test sample file
        sample_file = os.path.join(samples_dir, f"1-{instrument_name}.wav")
        with open(sample_file, "w") as f:
            f.write("Test sample content")

        # Configure the mock to raise an exception
        mock_subprocess_run.side_effect = subprocess.CalledProcessError(
            1, ["sox"], output=b"Test output", stderr=b"Test error"
        )

        # Redirect stderr to avoid cluttering test output
        original_stderr = sys.stderr
        with open(os.devnull, "w", encoding="utf-8") as devnull:
            sys.stderr = devnull
            try:
                # Call the function
                create_volume_variations(instrument_name, self.temp_dir, ".wav", 3)

                # Verify that subprocess.run was called
                self.assertEqual(mock_subprocess_run.call_count, 2)
            finally:
                # Restore stderr
                sys.stderr = original_stderr

    @patch("drumgizmo_kits_generator.audio.subprocess.run")
    def test_create_volume_variations_generic_exception(self, mock_subprocess_run):
        """Test generic error handling in create_volume_variations."""
        # Create a test instrument directory
        instrument_name = "test_instrument"
        instrument_dir = os.path.join(self.temp_dir, instrument_name)
        samples_dir = os.path.join(instrument_dir, "samples")
        os.makedirs(samples_dir, exist_ok=True)

        # Create a test sample file
        sample_file = os.path.join(samples_dir, f"1-{instrument_name}.wav")
        with open(sample_file, "w") as f:
            f.write("Test sample content")

        # Configure the mock to raise a generic exception
        mock_subprocess_run.side_effect = Exception("Test generic error")

        # Redirect stderr to avoid cluttering test output
        original_stderr = sys.stderr
        with open(os.devnull, "w", encoding="utf-8") as devnull:
            sys.stderr = devnull
            try:
                # Call the function
                create_volume_variations(instrument_name, self.temp_dir, ".wav", 3)
            finally:
                # Restore stderr
                sys.stderr = original_stderr

    @patch("subprocess.run")
    def test_create_volume_variations_error(self, mock_run):
        """Test error handling when creating volume variations."""
        # Configure the mock to simulate an error
        mock_run.return_value = MagicMock(returncode=1)

        # Test with a valid file
        instrument = "test_instrument"
        instrument_dir = os.path.join(self.temp_dir, instrument)
        samples_dir = os.path.join(instrument_dir, "samples")
        os.makedirs(samples_dir, exist_ok=True)

        # Create the source file
        source_file = os.path.join(samples_dir, f"1-{instrument}.wav")
        with open(source_file, "w", encoding="utf-8") as f:
            f.write("Test content")

        # Call the function
        create_volume_variations(instrument, self.temp_dir, ".wav")

        # Verify the result - la fonction continue même en cas d'erreur
        # La fonction ne retourne pas de valeur et continue malgré les erreurs
        self.assertEqual(mock_run.call_count, 9, "La fonction devrait continuer malgré les erreurs")

    def test_convert_sample_rate(self):
        """Test converting the sample rate of a file."""
        # Create a temporary source file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as source_file:
            source_path = source_file.name

        # Create a temporary destination file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as dest_file:
            dest_path = dest_file.name

        # Create a test WAV file with SoX
        try:
            subprocess.run(
                ["sox", "-n", source_path, "rate", "44100", "trim", "0", "0.1"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except (subprocess.SubprocessError, FileNotFoundError):
            self.skipTest("SoX is not available or failed to create test file")

        # Test converting the sample rate
        result = convert_sample_rate(source_path, dest_path, "48000")
        self.assertTrue(result, "Sample rate conversion should succeed")

        # Check that the destination file exists
        self.assertTrue(os.path.exists(dest_path), "Destination file should exist")

        # Check that the sample rate was actually converted
        try:
            output = subprocess.run(
                ["soxi", "-r", dest_path],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            sample_rate = output.stdout.strip()
            self.assertEqual("48000", sample_rate, "Sample rate should be 48000 Hz")
        except (subprocess.SubprocessError, FileNotFoundError):
            self.skipTest("soxi is not available or failed to get sample rate")

        # Clean up
        try:
            os.unlink(source_path)
            os.unlink(dest_path)
        except OSError:
            pass

    def test_convert_sample_rate_error(self):
        """Test error handling in convert_sample_rate."""
        # Test with non-existent source file
        result = convert_sample_rate("nonexistent.wav", "output.wav", "48000")
        self.assertFalse(result, "Should return False for non-existent source file")

    def test_copy_sample_file_with_conversion(self):
        """Test copying a sample file with sample rate conversion."""
        # Create a temporary source file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as source_file:
            source_path = source_file.name

        # Create a temporary destination file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as dest_file:
            dest_path = dest_file.name

        # Create a test WAV file with SoX
        try:
            subprocess.run(
                ["sox", "-n", source_path, "rate", "44100", "trim", "0", "0.1"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except (subprocess.SubprocessError, FileNotFoundError):
            self.skipTest("SoX is not available or failed to create test file")

        # Test copying with sample rate conversion
        result = copy_sample_file(source_path, dest_path, "48000")
        self.assertTrue(result, "File copy with conversion should succeed")

        # Check that the destination file exists
        self.assertTrue(os.path.exists(dest_path), "Destination file should exist")

        # Check that the sample rate was actually converted
        try:
            output = subprocess.run(
                ["soxi", "-r", dest_path],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            sample_rate = output.stdout.strip()
            self.assertEqual("48000", sample_rate, "Sample rate should be 48000 Hz")
        except (subprocess.SubprocessError, FileNotFoundError):
            self.skipTest("soxi is not available or failed to get sample rate")

        # Clean up
        try:
            os.unlink(source_path)
            os.unlink(dest_path)
        except OSError:
            pass

    def test_copy_sample_file_same_rate(self):
        """Test copying a sample file when source and target sample rates are the same."""
        # Create a temporary source file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as source_file:
            source_path = source_file.name

        # Create a temporary destination file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as dest_file:
            dest_path = dest_file.name

        # Create a test WAV file with SoX
        try:
            subprocess.run(
                ["sox", "-n", source_path, "rate", "44100", "trim", "0", "0.1"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except (subprocess.SubprocessError, FileNotFoundError):
            self.skipTest("SoX is not available or failed to create test file")

        # Test copying with the same sample rate
        result = copy_sample_file(source_path, dest_path, "44100")
        self.assertTrue(result, "File copy with same rate should succeed")

        # Check that the destination file exists
        self.assertTrue(os.path.exists(dest_path), "Destination file should exist")

        # Clean up
        try:
            os.unlink(source_path)
            os.unlink(dest_path)
        except OSError:
            pass

    def test_copy_sample_file_no_conversion(self):
        """Test copying a sample file without sample rate conversion."""
        # Create a temporary source file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as source_file:
            source_path = source_file.name

        # Create a temporary destination file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as dest_file:
            dest_path = dest_file.name

        # Create a test WAV file with SoX
        try:
            subprocess.run(
                ["sox", "-n", source_path, "rate", "44100", "trim", "0", "0.1"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except (subprocess.SubprocessError, FileNotFoundError):
            self.skipTest("SoX is not available or failed to create test file")

        # Test copying without sample rate conversion
        result = copy_sample_file(source_path, dest_path)
        self.assertTrue(result, "File copy without conversion should succeed")

        # Check that the destination file exists
        self.assertTrue(os.path.exists(dest_path), "Destination file should exist")

        # Clean up
        try:
            os.unlink(source_path)
            os.unlink(dest_path)
        except OSError:
            pass


if __name__ == "__main__":
    unittest.main()
