#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name
# pylint: disable=too-many-arguments
"""
Tests for the audio module of the DrumGizmo kit generator.
"""

import os
import subprocess
import tempfile
from unittest import mock

import pytest

from drumgizmo_kits_generator import audio, constants


@pytest.fixture
def mock_logger():
    """Mock logger functions."""
    with mock.patch("drumgizmo_kits_generator.logger.info") as mock_info, mock.patch(
        "drumgizmo_kits_generator.logger.debug"
    ) as mock_debug, mock.patch(
        "drumgizmo_kits_generator.logger.warning"
    ) as mock_warning, mock.patch(
        "drumgizmo_kits_generator.logger.error"
    ) as mock_error:
        yield {"info": mock_info, "debug": mock_debug, "warning": mock_warning, "error": mock_error}


@pytest.fixture
def tmp_dir():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield tmp_dir


@pytest.fixture
def sample_file():
    """Create a temporary audio file for testing."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
        temp_file_path = temp_file.name
    yield temp_file_path
    if os.path.exists(temp_file_path):
        os.unlink(temp_file_path)


@pytest.fixture
def metadata():
    """Create metadata for testing."""
    return {
        "name": "Test Kit",
        "version": "1.0",
        "description": "Test description",
        "velocity_levels": 3,
        "samplerate": "48000",
        "channels": ["Left", "Right"],
        "main_channels": ["Left", "Right"],
    }


class TestCreateVelocityVariations:
    """Tests for the create_velocity_variations function."""

    @mock.patch("shutil.which")
    @mock.patch("subprocess.run")
    @mock.patch("os.path.exists")
    @mock.patch("shutil.copy2")
    def test_create_velocity_variations_with_sox(
        self, mock_copy2, mock_exists, mock_run, mock_which, tmp_dir, sample_file
    ):
        """Test create_velocity_variations with SoX available."""
        # Setup mocks
        mock_which.return_value = "/usr/bin/sox"  # SoX is available
        mock_exists.return_value = True
        mock_run.return_value = mock.MagicMock(returncode=0)

        # Call the function
        result = audio.create_velocity_variations(sample_file, tmp_dir, 3, "test_instrument")

        # Assertions
        assert len(result) == 3
        assert all(
            os.path.basename(f).startswith(f"{i}-test_instrument") for i, f in enumerate(result, 1)
        )
        assert mock_run.call_count == 3
        assert mock_copy2.call_count == 0

    @mock.patch("shutil.which")
    @mock.patch("os.path.exists")
    def test_create_velocity_variations_without_sox(
        self, mock_exists, mock_which, tmp_dir, sample_file
    ):
        """Test create_velocity_variations without SoX available."""
        # Setup mocks
        mock_which.return_value = None  # SoX is not available
        mock_exists.return_value = True

        # Call the function and expect a DependencyError
        with pytest.raises(audio.DependencyError) as excinfo:
            audio.create_velocity_variations(sample_file, tmp_dir, 3, "test_instrument")

        # Verify the error message
        assert "SoX not found" in str(excinfo.value)

    @mock.patch("os.path.exists")
    def test_create_velocity_variations_file_not_found(self, mock_exists, tmp_dir, sample_file):
        """Test create_velocity_variations with file not found."""
        # Setup mocks
        mock_exists.return_value = False

        # Call the function and expect an AudioProcessingError
        with pytest.raises(audio.AudioProcessingError) as excinfo:
            audio.create_velocity_variations(sample_file, tmp_dir, 3, "test_instrument")

        # Verify the error message
        assert "Source file not found" in str(excinfo.value)

    @mock.patch("subprocess.run")
    @mock.patch("os.path.exists")
    def test_create_velocity_variations_sox_error(
        self, mock_exists, mock_run, tmp_dir, sample_file
    ):
        """Test create_velocity_variations with SoX error."""
        # Setup mocks
        mock_exists.return_value = True
        mock_run.side_effect = subprocess.CalledProcessError(1, "sox")

        # Call the function and expect an AudioProcessingError
        with pytest.raises(audio.AudioProcessingError) as excinfo:
            audio.create_velocity_variations(sample_file, tmp_dir, 3, "test_instrument")

        # Verify the error message
        assert "Failed to create velocity variation" in str(excinfo.value)


class TestProcessSample:
    """Tests for the process_sample function."""

    @mock.patch("drumgizmo_kits_generator.utils.clean_instrument_name")
    @mock.patch("drumgizmo_kits_generator.utils.convert_sample_rate")
    @mock.patch("drumgizmo_kits_generator.audio.create_velocity_variations")
    def test_process_sample_with_sample_rate_conversion(
        self,
        mock_create_velocity,
        mock_convert_sample_rate,
        mock_clean_name,
        tmp_dir,
        sample_file,
        metadata,
    ):
        """Test process_sample with sample rate conversion."""
        # Setup mocks
        mock_clean_name.return_value = "test_instrument"
        converted_file = "/path/to/converted_file.wav"
        mock_convert_sample_rate.return_value = converted_file
        mock_create_velocity.return_value = ["file1.wav", "file2.wav", "file3.wav"]

        # Call the function
        result = audio.process_sample(sample_file, tmp_dir, metadata)

        # Assertions
        assert result == ["file1.wav", "file2.wav", "file3.wav"]
        mock_clean_name.assert_called_once()
        mock_convert_sample_rate.assert_called_once_with(sample_file, metadata["samplerate"])
        mock_create_velocity.assert_called_once_with(
            converted_file,
            os.path.join(tmp_dir, "test_instrument", "samples"),
            metadata["velocity_levels"],
            "test_instrument",
        )

    @mock.patch("drumgizmo_kits_generator.utils.clean_instrument_name")
    @mock.patch("drumgizmo_kits_generator.utils.convert_sample_rate")
    @mock.patch("drumgizmo_kits_generator.audio.create_velocity_variations")
    def test_process_sample_without_sample_rate_conversion(
        self, mock_create_velocity, mock_convert_sample_rate, mock_clean_name, tmp_dir, sample_file
    ):
        """Test process_sample without sample rate conversion."""
        # Setup mocks
        mock_clean_name.return_value = "test_instrument"
        mock_create_velocity.return_value = ["file1.wav", "file2.wav", "file3.wav"]

        # Create metadata without samplerate
        metadata_without_samplerate = {
            "name": "Test Kit",
            "version": "1.0",
            "description": "Test description",
            "velocity_levels": 3,
        }

        # Call the function
        result = audio.process_sample(sample_file, tmp_dir, metadata_without_samplerate)

        # Assertions
        assert result == ["file1.wav", "file2.wav", "file3.wav"]
        mock_clean_name.assert_called_once()
        mock_convert_sample_rate.assert_not_called()
        mock_create_velocity.assert_called_once_with(
            sample_file,
            os.path.join(tmp_dir, "test_instrument", "samples"),
            metadata_without_samplerate["velocity_levels"],
            "test_instrument",
        )

    @mock.patch("drumgizmo_kits_generator.utils.clean_instrument_name")
    @mock.patch("drumgizmo_kits_generator.utils.convert_sample_rate")
    @mock.patch("drumgizmo_kits_generator.audio.create_velocity_variations")
    @mock.patch("shutil.rmtree")
    def test_process_sample_cleanup_temp_dirs(
        self,
        mock_rmtree,
        mock_create_velocity,
        mock_convert_sample_rate,
        mock_clean_name,
        tmp_dir,
        sample_file,
        metadata,
    ):
        """Test process_sample cleans up temporary directories."""
        # Setup mocks
        mock_clean_name.return_value = "test_instrument"
        converted_file = "/path/to/converted_file.wav"
        mock_convert_sample_rate.return_value = converted_file
        mock_create_velocity.return_value = ["file1.wav", "file2.wav", "file3.wav"]

        # Call the function
        result = audio.process_sample(sample_file, tmp_dir, metadata)

        # Assertions
        assert result == ["file1.wav", "file2.wav", "file3.wav"]
        assert mock_rmtree.call_count == 0  # No temp dirs to clean up in this test

    @mock.patch("drumgizmo_kits_generator.utils.clean_instrument_name")
    @mock.patch("drumgizmo_kits_generator.audio.create_velocity_variations")
    def test_process_sample_with_default_velocity_levels(
        self, mock_create_velocity, mock_clean_name, tmp_dir, sample_file
    ):
        """Test process_sample with default velocity levels."""
        # Setup mocks
        mock_clean_name.return_value = "test_instrument"
        mock_create_velocity.return_value = ["file1.wav", "file2.wav", "file3.wav"]

        # Create metadata without velocity_levels
        metadata_without_velocity = {
            "name": "Test Kit",
            "version": "1.0",
            "description": "Test description",
        }

        # Call the function
        result = audio.process_sample(sample_file, tmp_dir, metadata_without_velocity)

        # Assertions
        assert result == ["file1.wav", "file2.wav", "file3.wav"]
        mock_create_velocity.assert_called_once_with(
            mock.ANY,
            os.path.join(tmp_dir, "test_instrument", "samples"),
            constants.DEFAULT_VELOCITY_LEVELS,
            "test_instrument",
        )
