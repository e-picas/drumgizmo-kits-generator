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
Additional tests for the audio module to improve test coverage.
"""

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from io import StringIO
from unittest.mock import MagicMock, patch

# Add the parent directory to the path to be able to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from drumgizmo_kits_generator.audio import (
    copy_sample_file,
    create_volume_variations,
    find_audio_files,
)


class TestAudioAdditional(unittest.TestCase):
    """Additional tests for the audio module to improve test coverage."""

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

    def test_create_volume_variations_single_level(self):
        """Test create_volume_variations with a single velocity level."""
        # Test with a single velocity level
        instrument = "Kick"
        kit_dir = self.temp_dir
        extension = ".wav"
        velocity_levels = 1

        # Create the necessary directories
        instrument_dir = os.path.join(kit_dir, instrument)
        samples_dir = os.path.join(instrument_dir, "samples")
        os.makedirs(samples_dir)

        # Create a dummy source file
        source_file = os.path.join(samples_dir, f"1-{instrument}{extension}")
        with open(source_file, "w") as f:
            f.write("dummy audio data")

        # Call create_volume_variations
        create_volume_variations(instrument, kit_dir, extension, velocity_levels)

        # Check that the output contains the expected message
        output = self.mock_stderr.getvalue()
        self.assertIn("Skipping volume variations", output)

        # Check that no additional files were created
        files = os.listdir(samples_dir)
        self.assertEqual(len(files), 1, "Should only have the original file")

    def test_create_volume_variations_sox_not_found(self):
        """Test create_volume_variations when SoX is not found."""
        # Test when SoX is not found
        instrument = "Kick"
        kit_dir = self.temp_dir
        extension = ".wav"
        velocity_levels = 3

        # Create the necessary directories
        instrument_dir = os.path.join(kit_dir, instrument)
        samples_dir = os.path.join(instrument_dir, "samples")
        os.makedirs(samples_dir)

        # Create a dummy source file
        source_file = os.path.join(samples_dir, f"1-{instrument}{extension}")
        with open(source_file, "w") as f:
            f.write("dummy audio data")

        # Mock subprocess.run to raise a FileNotFoundError
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError("SoX command not found")

            # Call create_volume_variations
            create_volume_variations(instrument, kit_dir, extension, velocity_levels)

            # Check that the output contains the expected error message
            output = self.mock_stderr.getvalue()
            self.assertIn("SoX command not found", output)

    def test_create_volume_variations_permission_error(self):
        """Test create_volume_variations with a permission error."""
        # Test with a permission error
        instrument = "Kick"
        kit_dir = self.temp_dir
        extension = ".wav"
        velocity_levels = 3

        # Create the necessary directories
        instrument_dir = os.path.join(kit_dir, instrument)
        samples_dir = os.path.join(instrument_dir, "samples")
        os.makedirs(samples_dir)

        # Create a dummy source file
        source_file = os.path.join(samples_dir, f"1-{instrument}{extension}")
        with open(source_file, "w") as f:
            f.write("dummy audio data")

        # Mock subprocess.run to raise a PermissionError
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = PermissionError("Permission denied")

            # Call create_volume_variations
            create_volume_variations(instrument, kit_dir, extension, velocity_levels)

            # Check that the output contains the expected error message
            output = self.mock_stderr.getvalue()
            self.assertIn("Permission denied", output)

    def test_create_volume_variations_os_error(self):
        """Test create_volume_variations with an OS error."""
        # Test with an OS error
        instrument = "Kick"
        kit_dir = self.temp_dir
        extension = ".wav"
        velocity_levels = 3

        # Create the necessary directories
        instrument_dir = os.path.join(kit_dir, instrument)
        samples_dir = os.path.join(instrument_dir, "samples")
        os.makedirs(samples_dir)

        # Create a dummy source file
        source_file = os.path.join(samples_dir, f"1-{instrument}{extension}")
        with open(source_file, "w") as f:
            f.write("dummy audio data")

        # Mock subprocess.run to raise an OSError
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = OSError("File system error")

            # Call create_volume_variations
            create_volume_variations(instrument, kit_dir, extension, velocity_levels)

            # Check that the output contains the expected error message
            output = self.mock_stderr.getvalue()
            self.assertIn("File system error", output)

    def test_create_volume_variations_subprocess_error(self):
        """Test create_volume_variations with a subprocess error."""
        # Test with a subprocess error
        instrument = "Kick"
        kit_dir = self.temp_dir
        extension = ".wav"
        velocity_levels = 3

        # Create the necessary directories
        instrument_dir = os.path.join(kit_dir, instrument)
        samples_dir = os.path.join(instrument_dir, "samples")
        os.makedirs(samples_dir)

        # Create a dummy source file
        source_file = os.path.join(samples_dir, f"1-{instrument}{extension}")
        with open(source_file, "w") as f:
            f.write("dummy audio data")

        # Mock subprocess.run to raise a CalledProcessError
        with patch("subprocess.run") as mock_run:
            mock_process_error = subprocess.CalledProcessError(
                1, ["sox"], output="", stderr="Error"
            )
            mock_process_error.stdout = "stdout"
            mock_process_error.stderr = "stderr"
            mock_run.side_effect = mock_process_error

            # Call create_volume_variations
            create_volume_variations(instrument, kit_dir, extension, velocity_levels)

            # Check that the output contains the expected error messages
            output = self.mock_stderr.getvalue()
            self.assertIn("Error creating volume variation", output)
            self.assertIn("Command output", output)
            self.assertIn("Command error", output)

    def test_create_volume_variations_with_target_samplerate(self):
        """Test create_volume_variations with a target sample rate."""
        # Test with a target sample rate
        instrument = "Kick"
        kit_dir = self.temp_dir
        extension = ".wav"
        velocity_levels = 3
        target_samplerate = "44100"

        # Create the necessary directories
        instrument_dir = os.path.join(kit_dir, instrument)
        samples_dir = os.path.join(instrument_dir, "samples")
        os.makedirs(samples_dir)

        # Create a dummy source file
        source_file = os.path.join(samples_dir, f"1-{instrument}{extension}")
        with open(source_file, "w") as f:
            f.write("dummy audio data")

        # Mock subprocess.run to return successfully
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock()

            # Call create_volume_variations
            create_volume_variations(
                instrument, kit_dir, extension, velocity_levels, target_samplerate
            )

            # Check that subprocess.run was called with the correct arguments
            calls = mock_run.call_args_list
            self.assertEqual(
                len(calls),
                velocity_levels - 1,
                "Should call subprocess.run for each velocity level except the first",
            )

            # Check that the target sample rate was included in the command
            for call in calls:
                args, kwargs = call
                cmd = args[0]
                self.assertIn("-r", cmd, "Command should include -r option for sample rate")
                self.assertIn(
                    target_samplerate, cmd, "Command should include the target sample rate"
                )

    def test_copy_sample_file_success(self):
        """Test copy_sample_file with a successful copy."""
        # Test with a successful copy
        source_file = os.path.join(self.temp_dir, "source.wav")
        dest_file = os.path.join(self.temp_dir, "dest.wav")

        # Create a dummy source file
        with open(source_file, "w") as f:
            f.write("dummy audio data")

        # Call copy_sample_file
        result = copy_sample_file(source_file, dest_file)

        # Check that the file was copied successfully
        self.assertTrue(result, "Should return True when successful")
        self.assertTrue(os.path.exists(dest_file), "Destination file should exist")

    def test_copy_sample_file_with_target_samplerate(self):
        """Test copy_sample_file with a target sample rate."""
        # Test with a target sample rate
        source_file = os.path.join(self.temp_dir, "source.wav")
        dest_file = os.path.join(self.temp_dir, "dest.wav")
        target_samplerate = "44100"

        # Create a dummy source file
        with open(source_file, "w") as f:
            f.write("dummy audio data")

        # Mock convert_sample_rate to return True
        with patch("drumgizmo_kits_generator.audio.convert_sample_rate") as mock_convert:
            mock_convert.return_value = True

            # Call copy_sample_file
            result = copy_sample_file(source_file, dest_file, target_samplerate)

            # Check that convert_sample_rate was called with the correct arguments
            mock_convert.assert_called_once_with(source_file, dest_file, target_samplerate)

            # Check that the result is True
            self.assertTrue(result, "Should return True when successful")

    def test_copy_sample_file_file_not_found(self):
        """Test copy_sample_file with a file not found error."""
        # Test with a file not found error
        source_file = os.path.join(self.temp_dir, "nonexistent.wav")
        dest_file = os.path.join(self.temp_dir, "dest.wav")

        # Call copy_sample_file
        result = copy_sample_file(source_file, dest_file)

        # Check that the result is False
        self.assertFalse(result, "Should return False when the source file doesn't exist")

        # Check that the output contains the expected error message
        output = self.mock_stderr.getvalue()
        self.assertIn("File not found", output)

    def test_copy_sample_file_permission_error(self):
        """Test copy_sample_file with a permission error."""
        # Test with a permission error
        source_file = os.path.join(self.temp_dir, "source.wav")
        dest_file = os.path.join(self.temp_dir, "dest.wav")

        # Create a dummy source file
        with open(source_file, "w") as f:
            f.write("dummy audio data")

        # Mock shutil.copy2 to raise a PermissionError
        with patch("shutil.copy2") as mock_copy:
            mock_copy.side_effect = PermissionError("Permission denied")

            # Call copy_sample_file
            result = copy_sample_file(source_file, dest_file)

            # Check that the result is False
            self.assertFalse(result, "Should return False when a permission error occurs")

            # Check that the output contains the expected error message
            output = self.mock_stderr.getvalue()
            self.assertIn("Permission denied", output)

    def test_copy_sample_file_shutil_error(self):
        """Test copy_sample_file with a shutil error."""
        # Test with a shutil error
        source_file = os.path.join(self.temp_dir, "source.wav")
        dest_file = os.path.join(self.temp_dir, "dest.wav")

        # Create a dummy source file
        with open(source_file, "w") as f:
            f.write("dummy audio data")

        # Mock shutil.copy2 to raise a shutil.Error
        with patch("shutil.copy2") as mock_copy:
            mock_copy.side_effect = shutil.Error("Shutil error")

            # Call copy_sample_file
            result = copy_sample_file(source_file, dest_file)

            # Check that the result is False
            self.assertFalse(result, "Should return False when a shutil error occurs")

            # Check that the output contains the expected error message
            output = self.mock_stderr.getvalue()
            self.assertIn("Shutil error", output)

    def test_copy_sample_file_os_error(self):
        """Test copy_sample_file with an OS error."""
        # Test with an OS error
        source_file = os.path.join(self.temp_dir, "source.wav")
        dest_file = os.path.join(self.temp_dir, "dest.wav")

        # Create a dummy source file
        with open(source_file, "w") as f:
            f.write("dummy audio data")

        # Mock shutil.copy2 to raise an OSError
        with patch("shutil.copy2") as mock_copy:
            mock_copy.side_effect = OSError("File system error")

            # Call copy_sample_file
            result = copy_sample_file(source_file, dest_file)

            # Check that the result is False
            self.assertFalse(result, "Should return False when an OS error occurs")

            # Check that the output contains the expected error message
            output = self.mock_stderr.getvalue()
            self.assertIn("File system error", output)

    def test_find_audio_files_empty_extensions(self):
        """Test find_audio_files with empty extensions."""
        # Test with empty extensions
        source_dir = self.temp_dir
        extensions = ""

        # Call find_audio_files
        result = find_audio_files(source_dir, extensions)

        # Check that the result is an empty list
        self.assertEqual(result, [], "Should return an empty list when extensions is empty")

    def test_find_audio_files_with_list_extensions(self):
        """Test find_audio_files with a list of extensions."""
        # Test with a list of extensions
        source_dir = self.temp_dir
        extensions = [".wav", ".flac"]

        # Create dummy files with different extensions
        self._create_test_audio_files(source_dir)

        # Call find_audio_files
        result = find_audio_files(source_dir, extensions)

        # Check that the result contains the expected files
        self.assertEqual(len(result), 2, "Should find 2 files")
        self.assertIn(os.path.join(source_dir, "test.wav"), result, "Should find the wav file")
        self.assertIn(os.path.join(source_dir, "test.flac"), result, "Should find the flac file")

    def test_find_audio_files_with_string_extensions(self):
        """Test find_audio_files with a string of extensions."""
        # Test with a string of extensions
        source_dir = self.temp_dir
        extensions = ".wav,.flac"

        # Create dummy files with different extensions
        self._create_test_audio_files(source_dir)

        # Call find_audio_files
        result = find_audio_files(source_dir, extensions)

        # Check that the result contains the expected files
        self.assertEqual(len(result), 2, "Should find 2 files")
        self.assertIn(os.path.join(source_dir, "test.wav"), result, "Should find the wav file")
        self.assertIn(os.path.join(source_dir, "test.flac"), result, "Should find the flac file")

    def test_find_audio_files_with_extensions_without_dot(self):
        """Test find_audio_files with extensions without a dot."""
        # Test with extensions without a dot
        source_dir = self.temp_dir
        extensions = "wav,flac"

        # Create dummy files with different extensions
        self._create_test_audio_files(source_dir)

        # Call find_audio_files
        result = find_audio_files(source_dir, extensions)

        # Check that the result contains the expected files
        self.assertEqual(len(result), 2, "Should find 2 files")
        self.assertIn(os.path.join(source_dir, "test.wav"), result, "Should find the wav file")
        self.assertIn(os.path.join(source_dir, "test.flac"), result, "Should find the flac file")

    def test_find_audio_files_with_whitespace(self):
        """Test find_audio_files with extensions containing whitespace."""
        # Test with extensions containing whitespace
        source_dir = self.temp_dir
        extensions = " wav , flac "

        # Create dummy files with different extensions
        self._create_test_audio_files(source_dir)

        # Call find_audio_files
        result = find_audio_files(source_dir, extensions)

        # Check that the result contains the expected files
        self.assertEqual(len(result), 2, "Should find 2 files")
        self.assertIn(os.path.join(source_dir, "test.wav"), result, "Should find the wav file")
        self.assertIn(os.path.join(source_dir, "test.flac"), result, "Should find the flac file")

    def _create_test_audio_files(self, directory):
        """Helper method to create test audio files with different extensions."""
        # Create dummy files
        wav_file = os.path.join(directory, "test.wav")
        flac_file = os.path.join(directory, "test.flac")
        ogg_file = os.path.join(directory, "test.ogg")

        with open(wav_file, "w") as f:
            f.write("dummy wav data")
        with open(flac_file, "w") as f:
            f.write("dummy flac data")
        with open(ogg_file, "w") as f:
            f.write("dummy ogg data")


if __name__ == "__main__":
    unittest.main()
