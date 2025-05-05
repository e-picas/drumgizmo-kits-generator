#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name
# pylint: disable=unspecified-encoding
# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
# pylint: disable=too-few-public-methods
"""
Integration tests for error scenarios in the DrumGizmo kit generator.
This test suite verifies that the application handles error conditions correctly.
"""

import io
import os
import shutil
import tempfile
from unittest import mock

import pytest

from drumgizmo_kits_generator import exceptions, main


@pytest.fixture
def temp_output_dir():
    """Create a temporary directory for the test output."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Clean up
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def temp_source_dir():
    """Create a temporary directory for the test source files."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Clean up
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def temp_config_file():
    """Create a temporary configuration file."""
    with tempfile.NamedTemporaryFile(suffix=".ini", delete=False) as temp_file:
        temp_file_path = temp_file.name
    yield temp_file_path
    # Clean up
    if os.path.exists(temp_file_path):
        os.unlink(temp_file_path)


class TestIntegrationErrors:
    """Integration tests for error scenarios in the DrumGizmo kit generator."""

    def test_nonexistent_source_directory(self, temp_output_dir):
        """Test with a non-existent source directory."""
        # Create a path to a directory that doesn't exist
        nonexistent_dir = os.path.join(
            tempfile.gettempdir(), "nonexistent_dir_" + os.urandom(8).hex()
        )

        # Run the generator with the non-existent source directory
        with mock.patch(
            "sys.argv", ["drumgizmo_kits_generator", "-s", nonexistent_dir, "-t", temp_output_dir]
        ), mock.patch("sys.stderr", new_callable=io.StringIO) as mock_stderr:
            # The application should raise a DirectoryError which is caught in main.py
            main.main()

            # Verify that an error message was printed
            stderr_output = mock_stderr.getvalue()
            # Check that the error message contains the expected text, ignoring ANSI color codes
            assert "ERROR:" in stderr_output
            assert f"Source directory '{nonexistent_dir}' does not exist" in stderr_output.replace(
                "\x1b[91m", ""
            ).replace("\x1b[0m", "")

    def test_nonexistent_config_file(self, temp_output_dir, temp_source_dir):
        """Test with a non-existent configuration file."""
        # Create a path to a file that doesn't exist
        nonexistent_config = os.path.join(
            tempfile.gettempdir(), "nonexistent_config_" + os.urandom(8).hex() + ".ini"
        )

        # Run the generator with the non-existent config file
        with mock.patch(
            "sys.argv",
            [
                "drumgizmo_kits_generator",
                "-s",
                temp_source_dir,
                "-t",
                temp_output_dir,
                "-c",
                nonexistent_config,
            ],
        ), mock.patch("sys.stderr", new_callable=io.StringIO) as mock_stderr:
            # The application should raise a ConfigurationError which is caught in main.py
            main.main()

            # Verify that an error message was printed
            stderr_output = mock_stderr.getvalue()
            # Check for a warning about the configuration file not being found
            assert "WARNING:" in stderr_output.replace("\x1b[91m", "").replace("\x1b[0m", "")
            assert f"Configuration file not found: {nonexistent_config}" in stderr_output.replace(
                "\x1b[91m", ""
            ).replace("\x1b[0m", "")

    def test_invalid_config_file(self, temp_output_dir, temp_source_dir, temp_config_file):
        """Test with an invalid configuration file (not a valid INI file)."""
        # Create an invalid INI file
        with open(temp_config_file, "w") as f:
            f.write("This is not a valid INI file")

        # Run the generator with the invalid config file
        with mock.patch(
            "sys.argv",
            [
                "drumgizmo_kits_generator",
                "-s",
                temp_source_dir,
                "-t",
                temp_output_dir,
                "-c",
                temp_config_file,
            ],
        ), mock.patch("sys.stderr", new_callable=io.StringIO) as mock_stderr:
            # The application should raise a ConfigurationError which is caught in main.py
            main.main()

            # Verify that an error message was printed
            stderr_output = mock_stderr.getvalue()
            assert "ERROR: " in stderr_output
            assert "Error parsing configuration file" in stderr_output

    def test_missing_required_config_values(
        self, temp_output_dir, temp_source_dir, temp_config_file
    ):
        """Test with a configuration file missing required values."""
        # Create a config file missing required values
        with open(temp_config_file, "w") as f:
            f.write("[drumgizmo_kit_generator]\n")
            f.write("# Missing required name field\n")
            f.write("version = 1.0.0\n")

        # Run the generator with the incomplete config file
        with mock.patch(
            "sys.argv",
            [
                "drumgizmo_kits_generator",
                "-s",
                temp_source_dir,
                "-t",
                temp_output_dir,
                "-c",
                temp_config_file,
            ],
        ):
            # The application uses default values for missing configuration entries
            # so it doesn't exit with an error
            main.main()

            # Verify that the output directory was created and contains the expected files
            assert os.path.exists(temp_output_dir)
            assert os.path.exists(os.path.join(temp_output_dir, "drumkit.xml"))

            # When there are no instruments, midimap.xml might not be created
            # Verify that the default name "DrumGizmo Kit" was used
            with open(os.path.join(temp_output_dir, "drumkit.xml"), "r") as f:
                content = f.read()
                assert 'name="DrumGizmo Kit"' in content

    def test_no_audio_files_in_source_directory(
        self, temp_output_dir, temp_source_dir, temp_config_file
    ):
        """Test with a source directory containing no audio files."""
        # Create a valid config file
        with open(temp_config_file, "w") as f:
            f.write("[drumgizmo_kit_generator]\n")
            f.write("name = Test Kit\n")
            f.write("version = 1.0.0\n")
            f.write("description = Test kit for integration tests\n")
            f.write("author = Test Author\n")
            f.write("extensions = wav,ogg,flac\n")

        # Create an empty source directory (no audio files)
        # The directory is already empty from the fixture

        # Run the generator with the empty source directory
        with mock.patch(
            "sys.argv",
            [
                "drumgizmo_kits_generator",
                "-s",
                temp_source_dir,
                "-t",
                temp_output_dir,
                "-c",
                temp_config_file,
            ],
        ):
            # The application doesn't exit with an error if no audio files are found
            # It just creates an empty kit
            main.main()

            # Verify that the output directory was created and contains the expected files
            assert os.path.exists(temp_output_dir)
            assert os.path.exists(os.path.join(temp_output_dir, "drumkit.xml"))

            # When there are no instruments, we should check the warning message
            # Verify that no instrument directories were created
            dirs = [
                d
                for d in os.listdir(temp_output_dir)
                if os.path.isdir(os.path.join(temp_output_dir, d))
            ]
            assert len(dirs) == 0

            # Verify that the kit name is correctly set in the drumkit.xml file
            with open(os.path.join(temp_output_dir, "drumkit.xml"), "r") as f:
                content = f.read()
                assert 'name="Test Kit"' in content

    def test_sox_not_available(self, temp_output_dir, temp_source_dir, temp_config_file):
        """Test behavior when SoX is not available."""
        # Create a valid config file
        with open(temp_config_file, "w") as f:
            f.write("[drumgizmo_kit_generator]\n")
            f.write("name = Test Kit\n")
            f.write("version = 1.0.0\n")
            f.write("description = Test kit for integration tests\n")
            f.write("author = Test Author\n")
            f.write("extensions = wav,ogg,flac\n")

        # Create a sample audio file
        sample_file = os.path.join(temp_source_dir, "test_sample.wav")
        with open(sample_file, "wb") as f:
            f.write(b"RIFF" + b"\x00" * 100)  # Fake WAV file header

        # Mock shutil.which to simulate SoX not being available
        with mock.patch(
            "sys.argv",
            [
                "drumgizmo_kits_generator",
                "-s",
                temp_source_dir,
                "-t",
                temp_output_dir,
                "-c",
                temp_config_file,
            ],
        ), mock.patch("shutil.which", return_value=None), mock.patch(
            "sys.stderr", new_callable=io.StringIO
        ) as mock_stderr:
            # The application should raise a DependencyError which is caught in main.py
            main.main()

            # Verify that an error message was printed
            stderr_output = mock_stderr.getvalue()
            assert "ERROR: " in stderr_output
            assert "SoX not found" in stderr_output

    def test_dry_run_mode(self, temp_output_dir, temp_source_dir, temp_config_file):
        """Test dry run mode (no actual files should be generated)."""
        # Create a valid config file
        with open(temp_config_file, "w") as f:
            f.write("[drumgizmo_kit_generator]\n")
            f.write("name = Test Kit\n")
            f.write("version = 1.0.0\n")
            f.write("description = Test kit for integration tests\n")
            f.write("author = Test Author\n")
            f.write("extensions = wav,ogg,flac\n")

        # Create a sample audio file
        sample_file = os.path.join(temp_source_dir, "test_sample.wav")
        with open(sample_file, "wb") as f:
            f.write(b"RIFF" + b"\x00" * 100)  # Fake WAV file header

        # Run the generator in dry run mode
        with mock.patch(
            "sys.argv",
            [
                "drumgizmo_kits_generator",
                "-s",
                temp_source_dir,
                "-t",
                temp_output_dir,
                "-c",
                temp_config_file,
                "--dry-run",
            ],
        ), mock.patch("drumgizmo_kits_generator.utils.check_dependency", return_value=None):
            main.main()

            # Verify that no files were generated in the output directory
            assert len(os.listdir(temp_output_dir)) == 0

    def test_invalid_audio_file(self, temp_output_dir, temp_source_dir, temp_config_file):
        """Test with an invalid audio file that cannot be processed."""
        # Create a valid config file
        with open(temp_config_file, "w") as f:
            f.write("[drumgizmo_kit_generator]\n")
            f.write("name = Test Kit\n")
            f.write("version = 1.0.0\n")
            f.write("description = Test kit for integration tests\n")
            f.write("author = Test Author\n")
            f.write("extensions = wav,ogg,flac\n")

        # Create an invalid audio file
        invalid_file = os.path.join(temp_source_dir, "invalid_sample.wav")
        with open(invalid_file, "w") as f:
            f.write("This is not a valid WAV file")

        # Mock subprocess.run to simulate SoX failing to process the file
        with mock.patch(
            "sys.argv",
            [
                "drumgizmo_kits_generator",
                "-s",
                temp_source_dir,
                "-t",
                temp_output_dir,
                "-c",
                temp_config_file,
            ],
        ), mock.patch("shutil.which", return_value="/usr/bin/sox"), mock.patch(
            "subprocess.run",
            side_effect=exceptions.AudioProcessingError("Failed to process audio file"),
        ), mock.patch(
            "sys.stderr", new_callable=io.StringIO
        ) as mock_stderr:
            # The application should raise an AudioProcessingError which is caught in main.py
            main.main()

            # Verify that an error message was printed
            stderr_output = mock_stderr.getvalue()
            assert "ERROR: " in stderr_output
            assert "Failed to process audio file" in stderr_output


if __name__ == "__main__":
    pytest.main(["-v", __file__])
