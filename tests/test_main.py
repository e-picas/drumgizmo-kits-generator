#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for the main script of the DrumGizmo kit generator.

These tests verify the functionality of the main script that orchestrates
the creation of DrumGizmo kits, including metadata preparation, file handling,
and integration with other modules.
"""

import os
import shutil
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

# Add the parent directory to the path to be able to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import the modules to test
# pylint: disable-next=wrong-import-position
import main

# pylint: disable-next=wrong-import-position
from utils import extract_instrument_name, get_file_extension


class TestDrumGizmoKitGenerator(unittest.TestCase):
    """Tests for the DrumGizmo kit generator."""

    def setUp(self):
        """Initialize before each test by creating test directories and files."""
        self.source_dir = os.path.join(os.path.dirname(__file__), "sources")
        self.target_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.source_dir, "drumgizmo-kit.ini")

    def tearDown(self):
        """Cleanup after each test by removing temporary directories."""
        if os.path.exists(self.target_dir):
            shutil.rmtree(self.target_dir)

    # pylint: disable-next=too-many-statements
    def test_prepare_metadata(self):
        """Test preparing metadata from the configuration file with various input combinations."""
        # Create a temporary configuration file
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp:
            temp.write('kit_name = "Test Kit"\n')
            temp.write('kit_version = "1.0"\n')
            temp.write('kit_description = "This is a description"\n')
            temp.write('kit_notes = "DrumGizmo kit generated for testing purpose"\n')
            temp.write('kit_author = "Test Author"\n')
            temp.write('kit_license = "Test License"\n')
            temp.write('kit_website = "http://example.com"\n')
            temp.write('kit_logo = "test_logo.png"\n')
            temp.write('kit_samplerate = "48000"\n')
            temp.write('kit_instrument_prefix = "Test"\n')
            temp_name = temp.name

        # Create mock arguments
        args = MagicMock()
        args.config = temp_name
        args.source = self.source_dir
        args.name = None
        args.version = None
        args.description = "This is a description"  # Explicitly specify the description
        args.notes = None
        args.author = None
        args.license = None
        args.website = None
        args.logo = None
        args.samplerate = None
        args.instrument_prefix = None
        args.extra_files = None

        # Call the function to test
        metadata = main.prepare_metadata(args)

        # Verify the metadata
        self.assertEqual(metadata["name"], "Test Kit", "Kit name should be read from config")
        self.assertEqual(metadata["version"], "1.0", "Version should be read from config")
        self.assertEqual(
            metadata["description"],
            "This is a description",
            "Description should match command line arg",
        )
        self.assertIn(
            "DrumGizmo kit generated for testing purpose",
            metadata["notes"],
            "Notes should be read from config",
        )
        self.assertEqual(metadata["author"], "Test Author", "Author should be read from config")
        self.assertEqual(metadata["license"], "Test License", "License should be read from config")
        self.assertEqual(
            metadata["website"], "http://example.com", "Website should be read from config"
        )
        self.assertEqual(metadata["logo"], "test_logo.png", "Logo should be read from config")
        self.assertEqual(metadata["samplerate"], "48000", "Sample rate should be read from config")
        self.assertEqual(
            metadata["instrument_prefix"], "Test", "Instrument prefix should be read from config"
        )

        # Test command line arguments overriding config values
        args.name = "Override Kit"
        args.version = "2.0"
        args.author = "Override Author"

        # Call the function again
        metadata = main.prepare_metadata(args)

        # Verify the overridden values
        self.assertEqual(
            metadata["name"], "Override Kit", "Kit name should be overridden by command line"
        )
        self.assertEqual(metadata["version"], "2.0", "Version should be overridden by command line")
        self.assertEqual(
            metadata["author"], "Override Author", "Author should be overridden by command line"
        )

        # Delete the temporary file
        os.unlink(temp_name)

        # Test with missing config file but command line arguments
        args.config = None
        args.name = "Command Line Kit"
        args.version = "3.0"
        args.description = "Command line description"
        args.notes = "Command line notes"
        args.author = "Command Line Author"
        args.license = "Command Line License"
        args.samplerate = "96000"
        args.instrument_prefix = "CL"

        # Call the function again
        metadata = main.prepare_metadata(args)

        # Verify values from command line only
        self.assertEqual(
            metadata["name"], "Command Line Kit", "Kit name should be from command line"
        )
        self.assertEqual(metadata["version"], "3.0", "Version should be from command line")
        self.assertEqual(
            metadata["description"],
            "Command line description",
            "Description should be from command line",
        )
        self.assertIn("Command line notes", metadata["notes"], "Notes should be from command line")
        self.assertEqual(
            metadata["author"], "Command Line Author", "Author should be from command line"
        )
        self.assertEqual(
            metadata["license"], "Command Line License", "License should be from command line"
        )
        self.assertEqual(metadata["samplerate"], "96000", "Sample rate should be from command line")
        self.assertEqual(
            metadata["instrument_prefix"], "CL", "Instrument prefix should be from command line"
        )

    def test_copy_extra_files(self):
        """Test copying additional files with various file paths and configurations."""
        # Create test files in the current directory
        extra_files = ["test_file1.txt", "test_file2.txt"]
        current_dir = os.getcwd()
        subdir = None

        try:
            # Create files in the current directory
            for file in extra_files:
                file_path = os.path.join(current_dir, file)
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("Test content")

            # Create a string of additional files
            extra_files_str = ",".join(extra_files)

            # Call the function - note that copy_extra_files prend 3 arguments: source_dir, target_dir, extra_files_str
            copied_files = main.copy_extra_files(current_dir, self.target_dir, extra_files_str)

            # Verify that the files have been copied
            self.assertEqual(
                len(copied_files), len(extra_files), f"Should have copied {len(extra_files)} files"
            )
            for file in extra_files:
                target_path = os.path.join(self.target_dir, file)
                self.assertTrue(
                    os.path.exists(target_path), f"File {file} should exist in target directory"
                )
                self.assertTrue(
                    file in copied_files, f"File {file} should be in the list of copied files"
                )

            # Test with a non-existent file
            non_existent = "non_existent_file.txt"
            copied_files = main.copy_extra_files(current_dir, self.target_dir, non_existent)
            self.assertEqual(
                len(copied_files), 0, "Should not copy any files when file doesn't exist"
            )

            # Test with a file in a subdirectory
            subdir = os.path.join(current_dir, "subdir")
            os.makedirs(subdir, exist_ok=True)
            subdir_file = os.path.join(subdir, "subdir_file.txt")
            with open(subdir_file, "w", encoding="utf-8") as f:
                f.write("Subdir test content")

            # Call the function with a file in a subdirectory
            copied_files = main.copy_extra_files(
                current_dir, self.target_dir, "subdir/subdir_file.txt"
            )

            # Verify the file was copied with its directory structure
            target_subdir = os.path.join(self.target_dir, "subdir")
            self.assertTrue(os.path.exists(target_subdir), "Target subdirectory should be created")
            self.assertTrue(
                os.path.exists(os.path.join(target_subdir, "subdir_file.txt")),
                "File in subdirectory should be copied",
            )
            self.assertEqual(len(copied_files), 1, "Should have copied 1 file from subdirectory")

        finally:
            # Clean up created files
            for file in extra_files:
                file_path = os.path.join(current_dir, file)
                if os.path.exists(file_path):
                    os.remove(file_path)
            if subdir and os.path.exists(subdir):
                shutil.rmtree(subdir)

    def test_extract_instrument_name(self):
        """Test extracting the instrument name from various file paths."""
        # Test different file paths
        test_cases = [
            ("/path/to/Bass-Drum-1.wav", "Bass-Drum-1"),
            ("/path/to/E-Mu-Proteus-FX-Wacky-Snare.wav", "E-Mu-Proteus-FX-Wacky-Snare"),
            ("/path/with spaces/Tom Tom.wav", "Tom Tom"),
            ("Cymbal-Crash.flac", "Cymbal-Crash"),
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

    @patch("main.create_xml_file")
    @patch("main.create_midimap_xml")
    @patch("main.create_drumkit_xml")
    @patch("main.create_volume_variations")
    @patch("main.copy_sample_file")  # Utiliser copy_sample_file au lieu de copy_audio_file
    @patch("main.find_audio_files")

    # pylint: disable-next=too-many-arguments
    def test_main_integration(
        self,
        mock_find_audio_files,
        mock_copy_sample_file,
        mock_create_volume_variations,
        mock_create_drumkit_xml,
        mock_create_midimap_xml,
        mock_create_xml_file,
    ):
        """Integration test of the main script with all components mocked."""
        # Configure the mocks
        mock_find_audio_files.return_value = ["/path/to/sample1.wav", "/path/to/sample2.wav"]
        mock_copy_sample_file.return_value = True
        mock_create_volume_variations.return_value = None  # La fonction ne retourne rien
        mock_create_xml_file.return_value = True
        mock_create_drumkit_xml.return_value = True
        mock_create_midimap_xml.return_value = True

        # Create arguments for main()
        # pylint: disable-next=R0801
        sys.argv = [
            "create_drumgizmo_kit.py",
            "-s",
            self.source_dir,
            "-t",
            self.target_dir,
            "-c",
            self.config_file,
            "--name",
            "Test Kit",
        ]

        # Call the main() function
        with patch("sys.exit") as mock_exit:
            main.main()

            # Verify that the function did not terminate with an error
            mock_exit.assert_not_called()

        # Verify that the functions were called
        # pylint: disable-next=expression-not-assigned
        mock_find_audio_files.assert_called_once(), "find_audio_files should be called once"
        self.assertEqual(
            mock_copy_sample_file.call_count, 2, "copy_sample_file should be called for each sample"
        )
        self.assertEqual(
            mock_create_volume_variations.call_count,
            2,
            "create_volume_variations should be called for each sample",
        )
        self.assertEqual(
            mock_create_xml_file.call_count, 2, "create_xml_file should be called for each sample"
        )
        # pylint: disable-next=expression-not-assigned
        mock_create_drumkit_xml.assert_called_once(), "create_drumkit_xml should be called once"
        # pylint: disable-next=expression-not-assigned
        mock_create_midimap_xml.assert_called_once(), "create_midimap_xml should be called once"

    @patch("main.find_audio_files")
    def test_main_no_audio_files(self, mock_find_audio_files):
        """Test main function behavior when no audio files are found."""
        # Configure the mock to return an empty list
        mock_find_audio_files.return_value = []

        # Create arguments for main()
        sys.argv = [
            "create_drumgizmo_kit.py",
            "-s",
            self.source_dir,
            "-t",
            self.target_dir,
            "-c",
            self.config_file,
            "--name",
            "Test Kit",
        ]

        # Call the main() function and expect a system exit
        with patch("sys.exit") as mock_exit:
            main.main()

            # Verify that the function terminated with an error
            mock_exit.assert_called_once()

        # Verify that find_audio_files was called
        mock_find_audio_files.assert_called_once()


if __name__ == "__main__":
    unittest.main()
