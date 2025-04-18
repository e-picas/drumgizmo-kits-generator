#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for the audio module of the DrumGizmo kit generator.

These tests verify the functionality of audio file handling operations
including finding, copying, and creating volume variations of audio files.
"""

import os
import sys
import unittest
import tempfile
import shutil
from unittest.mock import patch, MagicMock

# Add the parent directory to the path to be able to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the module to test
# pylint: disable-next=wrong-import-position
from audio import (
    find_audio_files,
    copy_sample_file,
    create_volume_variations
)


class TestAudio(unittest.TestCase):
    """Tests for the audio module."""

    def setUp(self):
        """Initialize before each test by creating a temporary directory and test files."""
        # Create a temporary directory for tests
        self.temp_dir = tempfile.mkdtemp()
        self.source_dir = os.path.join(os.path.dirname(__file__), 'sources')

        # Create test audio files
        self.test_files = [
            os.path.join(self.temp_dir, "test1.wav"),
            os.path.join(self.temp_dir, "test2.flac"),
            os.path.join(self.temp_dir, "test3.ogg"),
            os.path.join(self.temp_dir, "test4.txt")  # Non-audio file
        ]

        for file_path in self.test_files:
            # pylint: disable-next=unspecified-encoding
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
        self.assertEqual(len(audio_files), 3, "Should find exactly 3 audio files with default extensions")
        self.assertIn(os.path.join(self.temp_dir, "test1.wav"), audio_files, "WAV file should be included")
        self.assertIn(os.path.join(self.temp_dir, "test2.flac"), audio_files, "FLAC file should be included")
        self.assertIn(os.path.join(self.temp_dir, "test3.ogg"), audio_files, "OGG file should be included")
        self.assertNotIn(os.path.join(self.temp_dir, "test4.txt"), audio_files, "Text file should not be included")

        # Test with specific extensions
        audio_files = find_audio_files(self.temp_dir, extensions=["wav"])
        self.assertEqual(len(audio_files), 1, "Should find only 1 file with WAV extension")
        self.assertIn(os.path.join(self.temp_dir, "test1.wav"), audio_files, "Only WAV file should be included")

        # Test with empty directory
        empty_dir = os.path.join(self.temp_dir, "empty")
        os.makedirs(empty_dir, exist_ok=True)
        audio_files = find_audio_files(empty_dir, extensions=["wav", "flac", "ogg"])
        self.assertEqual(len(audio_files), 0, "Should find no files in empty directory")

    @patch('shutil.copy2')
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

    @patch('shutil.copy2')
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

    @patch('subprocess.run')
    def test_create_volume_variations(self, mock_run):
        """Test creating volume variations of an audio file."""
        # Configure the mock
        mock_run.return_value = MagicMock(returncode=0)

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

        # Verify the result - la fonction ne retourne pas de valeur, donc pas de vérification de retour
        self.assertEqual(mock_run.call_count, 9, "Should create 9 variations (2-10)")

        # Verify the command arguments for the first call
        args, _ = mock_run.call_args_list[0]
        cmd = args[0]
        self.assertIn("sox", cmd[0], "Should use sox command")
        self.assertIn(f"1-{instrument}.wav", cmd[1], "Should use the source file")
        self.assertIn(f"2-{instrument}.wav", cmd[2], "Should create the target file")
        self.assertIn("vol", cmd[3], "Should use the vol effect")

    @patch('subprocess.run')
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


if __name__ == '__main__':
    unittest.main()
