#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=unspecified-encoding
# pylint: disable=R0801 # code duplication
"""
SPDX-License-Identifier: MIT
SPDX-PackageName: DrumGizmo kits generator
SPDX-FileCopyrightText: 2022-2023 The DrumGizmo Team
SPDX-FileContributor: E-Picas <web-tech@e-picas.fr>

Tests for the error handling in the kit_generator module.
"""

import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from drumgizmo_kits_generator.exceptions import (
    AudioProcessingError,
    DependencyError,
    DirectoryError,
    XMLGenerationError,
)
from drumgizmo_kits_generator.kit_generator import (
    copy_additional_files,
    generate_xml_files,
    process_audio_files,
)
from drumgizmo_kits_generator.state import RunData


def test_process_audio_files_with_dependency_error():
    """Test process_audio_files function with a dependency error."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test file
        source_dir = os.path.join(temp_dir, "source")
        target_dir = os.path.join(temp_dir, "target")
        os.makedirs(source_dir)
        os.makedirs(target_dir)

        test_file = os.path.join(source_dir, "test.wav")
        with open(test_file, "w") as f:
            f.write("test audio content")

        # Create run data with necessary configuration
        run_data = RunData(source_dir=source_dir, target_dir=target_dir)
        run_data.config = {
            "name": "Test Kit",
            "version": "1.0",
            "samplerate": "44100",
            "velocity_levels": 3,
            "variations_method": "linear",
        }
        run_data.audio_sources = {
            "test": {
                "file_path": test_file,
                "instrument_name": "test",
                "midi_note": 60,
                "source_path": test_file,
            }
        }

        # Mock audio.process_sample to raise a DependencyError
        with patch(
            "drumgizmo_kits_generator.audio.process_sample",
            side_effect=DependencyError("SoX is not installed"),
        ):
            # Should raise a DependencyError with enriched context
            with pytest.raises(DependencyError) as excinfo:
                process_audio_files(run_data)

            # Check that the error message is enriched
            assert "Missing dependency during audio processing" in str(excinfo.value)
            assert "SoX is not installed" in str(excinfo.value)


def test_process_audio_files_with_os_error():
    """Test process_audio_files function with an OS error."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test file
        source_dir = os.path.join(temp_dir, "source")
        target_dir = os.path.join(temp_dir, "target")
        os.makedirs(source_dir)
        os.makedirs(target_dir)

        test_file = os.path.join(source_dir, "test.wav")
        with open(test_file, "w") as f:
            f.write("test audio content")

        # Create run data with necessary configuration
        run_data = RunData(source_dir=source_dir, target_dir=target_dir)
        run_data.config = {
            "name": "Test Kit",
            "version": "1.0",
            "samplerate": "44100",
            "velocity_levels": 3,
            "variations_method": "linear",
        }
        run_data.audio_sources = {
            "test": {
                "file_path": test_file,
                "instrument_name": "test",
                "midi_note": 60,
                "source_path": test_file,
            }
        }

        # Create an OSError with errno and filename
        os_error = OSError(13, "Permission denied", test_file)

        # Mock audio.process_sample to raise an OSError
        with patch(
            "drumgizmo_kits_generator.audio.process_sample",
            side_effect=os_error,
        ):
            # Should raise an AudioProcessingError with enriched context
            with pytest.raises(AudioProcessingError) as excinfo:
                process_audio_files(run_data)

            # Check that the error message is enriched
            assert "System error during audio processing" in str(excinfo.value)
            assert "Permission denied" in str(excinfo.value)


def test_process_audio_files_with_unexpected_error():
    """Test process_audio_files function with an unexpected error."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test file
        source_dir = os.path.join(temp_dir, "source")
        target_dir = os.path.join(temp_dir, "target")
        os.makedirs(source_dir)
        os.makedirs(target_dir)

        test_file = os.path.join(source_dir, "test.wav")
        with open(test_file, "w") as f:
            f.write("test audio content")

        # Create run data with necessary configuration
        run_data = RunData(source_dir=source_dir, target_dir=target_dir)
        run_data.config = {
            "name": "Test Kit",
            "version": "1.0",
            "samplerate": "44100",
            "velocity_levels": 3,
            "variations_method": "linear",
        }
        run_data.audio_sources = {
            "test": {
                "file_path": test_file,
                "instrument_name": "test",
                "midi_note": 60,
                "source_path": test_file,
            }
        }

        # Mock audio.process_sample to raise a KeyError
        with patch(
            "drumgizmo_kits_generator.audio.process_sample",
            side_effect=KeyError("Missing key"),
        ):
            # Should raise an AudioProcessingError with enriched context
            with pytest.raises(AudioProcessingError) as excinfo:
                process_audio_files(run_data)

            # Check that the error message is enriched
            assert "Unexpected error during audio processing" in str(excinfo.value)
            assert "KeyError" in str(excinfo.value)


def test_generate_xml_files_with_xml_generation_error():
    """Test generate_xml_files function with an XMLGenerationError."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test directories
        source_dir = os.path.join(temp_dir, "source")
        target_dir = os.path.join(temp_dir, "target")
        os.makedirs(source_dir)
        os.makedirs(target_dir)

        # Create run data with necessary configuration
        run_data = RunData(source_dir=source_dir, target_dir=target_dir)
        run_data.config = {
            "name": "Test Kit",
            "version": "1.0",
            "samplerate": "44100",
            "velocity_levels": 3,
        }
        run_data.audio_processed = {
            "test": ["test_file1.wav", "test_file2.wav"],
        }
        run_data.audio_sources = {
            "test": {
                "file_path": "test.wav",
                "instrument_name": "test",
                "midi_note": 60,
            }
        }
        run_data.midi_mapping = {
            "test": 60,
        }

        # Mock xml_generator.generate_drumkit_xml to raise an XMLGenerationError
        with patch(
            "drumgizmo_kits_generator.xml_generator.generate_drumkit_xml",
            side_effect=XMLGenerationError("Invalid XML structure"),
        ):
            # Should raise an XMLGenerationError with enriched context
            with pytest.raises(XMLGenerationError) as excinfo:
                generate_xml_files(run_data)

            # Check that the error message is enriched
            assert "Failed to generate XML files" in str(excinfo.value)
            assert "Invalid XML structure" in str(excinfo.value)


def test_generate_xml_files_with_os_error():
    """Test generate_xml_files function with an OSError."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test directories
        source_dir = os.path.join(temp_dir, "source")
        target_dir = os.path.join(temp_dir, "target")
        os.makedirs(source_dir)
        os.makedirs(target_dir)

        # Create run data with necessary configuration
        run_data = RunData(source_dir=source_dir, target_dir=target_dir)
        run_data.config = {
            "name": "Test Kit",
            "version": "1.0",
            "samplerate": "44100",
            "velocity_levels": 3,
        }
        run_data.audio_processed = {
            "test": ["test_file1.wav", "test_file2.wav"],
        }
        run_data.audio_sources = {
            "test": {
                "file_path": "test.wav",
                "instrument_name": "test",
                "midi_note": 60,
            }
        }
        run_data.midi_mapping = {
            "test": 60,
        }

        # Create an OSError with errno and filename
        os_error = OSError(13, "Permission denied", os.path.join(target_dir, "drumkit.xml"))

        # Mock xml_generator.generate_drumkit_xml to raise an OSError
        with patch(
            "drumgizmo_kits_generator.xml_generator.generate_drumkit_xml",
            side_effect=os_error,
        ):
            # Should raise an XMLGenerationError with enriched context
            with pytest.raises(XMLGenerationError) as excinfo:
                generate_xml_files(run_data)

            # Check that the error message is enriched
            assert "I/O error during XML file generation" in str(excinfo.value)
            assert "Permission denied" in str(excinfo.value)


def test_generate_xml_files_with_value_error():
    """Test generate_xml_files function with a ValueError."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test directories
        source_dir = os.path.join(temp_dir, "source")
        target_dir = os.path.join(temp_dir, "target")
        os.makedirs(source_dir)
        os.makedirs(target_dir)

        # Create run data with necessary configuration
        run_data = RunData(source_dir=source_dir, target_dir=target_dir)
        run_data.config = {
            "name": "Test Kit",
            "version": "1.0",
            "samplerate": "44100",
            "velocity_levels": 3,
        }
        run_data.audio_processed = {
            "test": ["test_file1.wav", "test_file2.wav"],
        }
        run_data.audio_sources = {
            "test": {
                "file_path": "test.wav",
                "instrument_name": "test",
                "midi_note": 60,
            }
        }
        run_data.midi_mapping = {
            "test": 60,
        }

        # Mock xml_generator.generate_drumkit_xml to raise a ValueError
        with patch(
            "drumgizmo_kits_generator.xml_generator.generate_drumkit_xml",
            side_effect=ValueError("Invalid value"),
        ):
            # Should raise an XMLGenerationError with enriched context
            with pytest.raises(XMLGenerationError) as excinfo:
                generate_xml_files(run_data)

            # Check that the error message is enriched
            assert "Invalid values during XML file generation" in str(excinfo.value)
            assert "Invalid value" in str(excinfo.value)


def test_copy_additional_files_with_file_not_found_error():
    """Test copy_additional_files function with a FileNotFoundError."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test directories
        source_dir = os.path.join(temp_dir, "source")
        target_dir = os.path.join(temp_dir, "target")
        os.makedirs(source_dir)
        os.makedirs(target_dir)

        # Create run data with necessary configuration
        run_data = RunData(source_dir=source_dir, target_dir=target_dir)
        run_data.config = {
            "logo": "logo.png",
            "extra_files": ["extra.txt"],
        }

        # Create a mock logger to verify warnings
        mock_logger = MagicMock()

        # Call the function with the mock logger
        with patch("drumgizmo_kits_generator.kit_generator.logger", mock_logger):
            copy_additional_files(run_data)

        # Verify that warnings were logged for missing files
        mock_logger.warning.assert_any_call(
            f"Logo file not found: {os.path.join(source_dir, 'logo.png')}"
        )
        mock_logger.warning.assert_any_call(
            f"Extra file not found: {os.path.join(source_dir, 'extra.txt')}"
        )


def test_copy_additional_files_with_permission_error():
    """Test copy_additional_files function with a PermissionError."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create test directories
        source_dir = os.path.join(temp_dir, "source")
        target_dir = os.path.join(temp_dir, "target")
        os.makedirs(source_dir)
        os.makedirs(target_dir)

        # Create test logo and extra files
        logo_file = os.path.join(source_dir, "logo.png")
        extra_file = os.path.join(source_dir, "extra.txt")
        with open(logo_file, "w") as f:
            f.write("test logo content")
        with open(extra_file, "w") as f:
            f.write("test extra content")

        # Create run data with necessary configuration
        run_data = RunData(source_dir=source_dir, target_dir=target_dir)
        run_data.config = {
            "logo": "logo.png",
            "extra_files": ["extra.txt"],
        }

        # Create a PermissionError with errno and filename
        perm_error = PermissionError(13, "Permission denied", os.path.join(target_dir, "extra.txt"))

        # Mock shutil.copy2 to raise a PermissionError
        with patch(
            "shutil.copy2",
            side_effect=perm_error,
        ):
            # Should raise a DirectoryError with enriched context
            with pytest.raises(DirectoryError) as excinfo:
                copy_additional_files(run_data)

            # Check that the error message is enriched
            assert "Permission error when copying additional files" in str(excinfo.value)
            assert "Permission denied" in str(excinfo.value)
