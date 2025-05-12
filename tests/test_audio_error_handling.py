#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=unspecified-encoding
# pylint: disable=unused-argument
"""
SPDX-License-Identifier: MIT
SPDX-PackageName: DrumGizmo kits generator
SPDX-FileCopyrightText: 2023 E-Picas <drumgizmo@e-picas.fr>
SPDX-FileType: SOURCE

Tests for error handling in the audio.py module
"""

import os
import subprocess
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from drumgizmo_kits_generator.audio import (
    convert_sample_rate,
    create_velocity_variations,
    get_audio_info,
    process_sample,
)
from drumgizmo_kits_generator.exceptions import AudioProcessingError


def test_process_sample_with_missing_file():
    """Test process_sample with a missing file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Test with a non-existent file
        source_file = os.path.join(temp_dir, "nonexistent.wav")

        # Create minimal valid metadata
        metadata = {"samplerate": "44100", "velocity_levels": 3, "variations_method": "linear"}

        # Mock audio.get_audio_info to avoid errors before reaching the actual test
        mock_audio_info = {"channels": 2, "samplerate": "44100", "duration": 1.0, "bitdepth": 16}

        with patch("drumgizmo_kits_generator.audio.get_audio_info", return_value=mock_audio_info):
            # Should raise an AudioProcessingError
            with pytest.raises(AudioProcessingError) as excinfo:
                process_sample(source_file, temp_dir, metadata)

            # The error could be from different parts of the process
            assert (
                "file not found" in str(excinfo.value).lower()
                or "failed" in str(excinfo.value).lower()
            )


def test_create_velocity_variations_with_invalid_method():
    """Test create_velocity_variations with an invalid method."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a test file
        source_file = os.path.join(temp_dir, "test.wav")
        with open(source_file, "w") as f:
            f.write("test audio content")

        # Test with invalid method
        with pytest.raises(ValueError) as excinfo:
            create_velocity_variations(
                source_file, temp_dir, 3, "test", variations_method="invalid_method"
            )

        assert "Invalid variations method" in str(excinfo.value)


def test_convert_sample_rate_with_sox_error():
    """Test convert_sample_rate when sox command fails."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a test file
        source_file = os.path.join(temp_dir, "test.wav")
        with open(source_file, "w") as f:
            f.write("test audio content")

        # Mock subprocess.run to raise a CalledProcessError
        error = subprocess.CalledProcessError(1, ["sox", source_file, "-r", "44100", "output.wav"])
        error.stderr = "SoX error: invalid audio file"

        with patch("subprocess.run", side_effect=error):
            with patch(
                "drumgizmo_kits_generator.utils.check_dependency", return_value="/usr/bin/sox"
            ):
                with pytest.raises(AudioProcessingError) as excinfo:
                    convert_sample_rate(source_file, "44100")

        assert "Failed to convert sample rate with SoX" in str(excinfo.value)


def test_get_audio_info_with_invalid_file():
    """Test get_audio_info with an invalid audio file."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create an invalid audio file (text file)
        invalid_file = os.path.join(temp_dir, "invalid.wav")
        with open(invalid_file, "w") as f:
            f.write("This is not a valid audio file")

        # Mock subprocess.run to raise a CalledProcessError
        error = subprocess.CalledProcessError(1, ["soxi", "-r", invalid_file])
        error.stderr = "soxi: Can't open input file `invalid.wav': WAVE: RIFF header not found"

        with patch("subprocess.run", side_effect=error):
            with patch(
                "drumgizmo_kits_generator.utils.check_dependency", return_value="/usr/bin/soxi"
            ):
                with pytest.raises(AudioProcessingError) as excinfo:
                    get_audio_info(invalid_file)

        assert "Failed to get audio information with SoX" in str(excinfo.value)


def test_get_audio_info_with_value_error():
    """Test get_audio_info when parsing values fails."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a test file
        test_file = os.path.join(temp_dir, "test.wav")
        with open(test_file, "w") as f:
            f.write("test audio content")

        # Mock subprocess.run to return valid process but with invalid stdout
        def mock_run(*args, **kwargs):
            mock_process = MagicMock()
            mock_process.returncode = 0

            # Return non-numeric value for sample rate to trigger ValueError
            if "-r" in args[0]:
                mock_process.stdout = "invalid"
            elif "-c" in args[0]:
                mock_process.stdout = "2"
            elif "-D" in args[0]:
                mock_process.stdout = "1.0"
            elif "-b" in args[0]:
                mock_process.stdout = "16"

            return mock_process

        with patch("subprocess.run", side_effect=mock_run):
            with patch(
                "drumgizmo_kits_generator.utils.check_dependency", return_value="/usr/bin/soxi"
            ):
                with pytest.raises(AudioProcessingError) as excinfo:
                    get_audio_info(test_file)

        assert "Unable to parse audio information" in str(excinfo.value)
