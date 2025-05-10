#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name
# pylint: disable=too-many-arguments
# pylint: disable=unused-argument
# pylint: disable=R0801 # code duplication # code duplication
# pylint: disable=protected-access
"""
SPDX-License-Identifier: MIT
SPDX-PackageName: DrumGizmo kits generator
SPDX-PackageHomePage: https://github.com/e-picas/drumgizmo-kits-generator
SPDX-FileCopyrightText: 2025 Pierre Cassat (Picas)

Tests for the audio module of the DrumGizmo kit generator.
"""

import os
import shutil
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
    ) as mock_error, mock.patch(
        "drumgizmo_kits_generator.logger.section"
    ) as mock_section, mock.patch(
        "drumgizmo_kits_generator.logger.message"
    ) as mock_message, mock.patch(
        "drumgizmo_kits_generator.logger.set_verbose"
    ) as mock_set_verbose:
        yield {
            "info": mock_info,
            "debug": mock_debug,
            "warning": mock_warning,
            "error": mock_error,
            "section": mock_section,
            "message": mock_message,
            "set_verbose": mock_set_verbose,
        }


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
        "variations_method": "linear",
        "samplerate": "48000",
        "channels": ["Left", "Right"],
        "main_channels": ["Left", "Right"],
    }


class TestCalculateLinearVolume:
    """Tests for the _calculate_linear_volume function."""

    def test_calculate_linear_volume_first_level(self):
        """Test _calculate_linear_volume with first level (should be MAX volume)."""
        # First level should always be MAX volume
        volume = audio._calculate_linear_volume(1, 3)
        assert volume == constants.DEFAULT_VELOCITY_VOLUME_MAX

    def test_calculate_linear_volume_middle_level(self):
        """Test _calculate_linear_volume with middle level."""
        # Middle level should be between MAX and MIN
        volume = audio._calculate_linear_volume(2, 3)
        expected = constants.DEFAULT_VELOCITY_VOLUME_MAX - (1 / 2) * (
            constants.DEFAULT_VELOCITY_VOLUME_MAX - constants.DEFAULT_VELOCITY_VOLUME_MIN
        )
        assert volume == expected

    def test_calculate_linear_volume_last_level(self):
        """Test _calculate_linear_volume with last level (should be MIN volume)."""
        # Last level should be MIN volume
        volume = audio._calculate_linear_volume(3, 3)
        assert volume == constants.DEFAULT_VELOCITY_VOLUME_MIN

    def test_calculate_linear_volume_single_level(self):
        """Test _calculate_linear_volume with only one level."""
        # With only one level, it should be MAX volume
        volume = audio._calculate_linear_volume(1, 1)
        assert volume == constants.DEFAULT_VELOCITY_VOLUME_MAX


class TestCalculateLogarithmicVolume:
    """Tests for the _calculate_logarithmic_volume function."""

    def test_calculate_logarithmic_volume_first_level(self):
        """Test _calculate_logarithmic_volume with first level (should be MAX volume)."""
        # First level should always be MAX volume
        volume = audio._calculate_logarithmic_volume(1, 3)
        assert volume == constants.DEFAULT_VELOCITY_VOLUME_MAX

    def test_calculate_logarithmic_volume_middle_level(self):
        """Test _calculate_logarithmic_volume with middle level."""
        # Middle level should be between MAX and MIN, but not linearly
        volume = audio._calculate_logarithmic_volume(2, 3)
        # Should be higher than the linear equivalent
        linear_volume = audio._calculate_linear_volume(2, 3)
        assert volume > linear_volume  # Logarithmic should be louder in the middle
        assert volume < constants.DEFAULT_VELOCITY_VOLUME_MAX
        assert volume > constants.DEFAULT_VELOCITY_VOLUME_MIN

    def test_calculate_logarithmic_volume_last_level(self):
        """Test _calculate_logarithmic_volume with last level (should be MIN volume)."""
        # Last level should be MIN volume
        volume = audio._calculate_logarithmic_volume(3, 3)
        assert volume == constants.DEFAULT_VELOCITY_VOLUME_MIN

    def test_calculate_logarithmic_volume_single_level(self):
        """Test _calculate_logarithmic_volume with only one level."""
        # With only one level, it should be MAX volume
        volume = audio._calculate_logarithmic_volume(1, 1)
        assert volume == constants.DEFAULT_VELOCITY_VOLUME_MAX


class TestCreateVelocityVariation:
    """Tests for the create_velocity_variation function."""

    @mock.patch("subprocess.run")
    @mock.patch("os.path.exists")
    def test_create_velocity_variation_success(self, mock_exists, mock_run, sample_file, tmp_dir):
        """Test create_velocity_variation with successful SoX execution."""
        # Setup mocks
        mock_exists.return_value = True
        mock_run.return_value = subprocess.CompletedProcess(
            args=["sox", "input.wav", "output.wav", "gain", "0.00"],
            returncode=0,
            stdout="",
            stderr="",
        )

        # Call the function
        target_file = os.path.join(tmp_dir, "output.wav")
        audio.create_velocity_variation(sample_file, target_file, 1.0)

        # Verify SoX was called with correct arguments
        mock_run.assert_called_once()
        args, _ = mock_run.call_args
        assert "sox" in args[0][0]
        assert args[0][1] == sample_file
        assert args[0][2] == target_file
        assert "gain" in args[0]

    @mock.patch("subprocess.run")
    @mock.patch("os.path.exists")
    def test_create_velocity_variation_sox_error(self, mock_exists, mock_run, sample_file, tmp_dir):
        """Test create_velocity_variation with SoX error."""
        # Setup mocks
        mock_exists.return_value = True
        mock_run.side_effect = subprocess.CalledProcessError(1, "sox")

        # Call the function and expect an AudioProcessingError
        target_file = os.path.join(tmp_dir, "output.wav")
        with pytest.raises(audio.AudioProcessingError) as excinfo:
            audio.create_velocity_variation(sample_file, target_file, 1.0)

        # Verify the error message
        assert "Error creating velocity variation" in str(excinfo.value)

    @mock.patch("os.path.exists")
    def test_create_velocity_variation_source_not_found(self, mock_exists, tmp_dir):
        """Test create_velocity_variation with non-existent source file."""
        # Setup mock
        mock_exists.return_value = False

        # Call the function and expect an AudioProcessingError
        target_file = os.path.join(tmp_dir, "output.wav")
        with pytest.raises(audio.AudioProcessingError) as excinfo:
            audio.create_velocity_variation("nonexistent.wav", target_file, 1.0)

        # Verify the error message
        assert "Source file not found" in str(excinfo.value)


class TestCreateVelocityVariations:
    """Tests for the create_velocity_variations function."""

    @mock.patch("drumgizmo_kits_generator.audio.create_velocity_variation")
    @mock.patch("os.path.exists")
    def test_create_velocity_variations_with_linear_curve(
        self, mock_exists, mock_create_variation, tmp_dir, sample_file
    ):
        """Test create_velocity_variations with linear volume curve."""
        # Setup mocks
        mock_exists.return_value = True

        # Call the function with linear curve (default)
        result = audio.create_velocity_variations(
            sample_file, tmp_dir, 3, "test_instrument", variations_method="linear"
        )

        # Verify the function was called with the expected arguments
        assert len(result) == 3
        assert mock_create_variation.call_count == 3

        # Get all volume factors that were used
        volume_factors = [call[0][2] for call in mock_create_variation.call_args_list]

        # Verify the volume factors are in decreasing order
        assert all(
            volume_factors[i] >= volume_factors[i + 1] for i in range(len(volume_factors) - 1)
        )

        # First volume should be MAX, last should be MIN
        assert abs(volume_factors[0] - constants.DEFAULT_VELOCITY_VOLUME_MAX) < 0.0001
        assert abs(volume_factors[-1] - constants.DEFAULT_VELOCITY_VOLUME_MIN) < 0.0001

        # For linear, the steps between volumes should be equal
        step = (constants.DEFAULT_VELOCITY_VOLUME_MAX - constants.DEFAULT_VELOCITY_VOLUME_MIN) / 2
        assert abs(volume_factors[0] - volume_factors[1] - step) < 0.0001
        assert abs(volume_factors[1] - volume_factors[2] - step) < 0.0001

    @mock.patch("drumgizmo_kits_generator.audio.create_velocity_variation")
    @mock.patch("os.path.exists")
    def test_create_velocity_variations_with_logarithmic_curve(
        self, mock_exists, mock_create_variation, tmp_dir, sample_file
    ):
        """Test create_velocity_variations with logarithmic volume curve."""
        # Setup mocks
        mock_exists.return_value = True

        # Call the function with logarithmic curve
        result = audio.create_velocity_variations(
            sample_file, tmp_dir, 3, "test_instrument", variations_method="logarithmic"
        )

        # Verify the function was called with the expected arguments
        assert len(result) == 3
        assert mock_create_variation.call_count == 3

        # Get all volume factors that were used
        volume_factors = [call[0][2] for call in mock_create_variation.call_args_list]

        # Verify the volume factors are in decreasing order
        assert all(
            volume_factors[i] >= volume_factors[i + 1] for i in range(len(volume_factors) - 1)
        )

        # First volume should be MAX, last should be MIN
        assert abs(volume_factors[0] - constants.DEFAULT_VELOCITY_VOLUME_MAX) < 0.0001
        assert abs(volume_factors[-1] - constants.DEFAULT_VELOCITY_VOLUME_MIN) < 0.0001

    @mock.patch("drumgizmo_kits_generator.audio.create_velocity_variation")
    @mock.patch("os.path.exists")
    def test_create_velocity_variations_invalid_curve(
        self, mock_exists, mock_create_variation, tmp_dir, sample_file
    ):
        """Test create_velocity_variations with invalid volume curve."""
        # Setup mocks
        mock_exists.return_value = True

        # Call the function with an invalid curve type
        with pytest.raises(ValueError) as excinfo:
            audio.create_velocity_variations(
                sample_file, tmp_dir, 3, "test_instrument", variations_method="invalid"
            )

        # Verify the error message
        assert "Invalid variations method: invalid" in str(excinfo.value)
        mock_create_variation.assert_not_called()

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
        assert "creating velocity variation" in str(excinfo.value)
        assert "sox" in str(excinfo.value)


class TestConvertSampleRate:
    """Tests for the convert_sample_rate function."""

    @mock.patch("shutil.which")
    def test_convert_sample_rate_no_sox(self, mock_which, sample_file, mock_logger):
        """Test convert_sample_rate with SoX not available."""
        # Setup mocks
        mock_which.return_value = None  # SoX is not available

        # Call the function and expect a DependencyError
        with pytest.raises(audio.DependencyError) as excinfo:
            audio.convert_sample_rate(sample_file, "48000")

        # Verify the error message
        assert "SoX not found" in str(excinfo.value)

    @mock.patch("shutil.which")
    @mock.patch("subprocess.run")
    @mock.patch("tempfile.mkdtemp")
    @mock.patch("os.path.exists")
    @mock.patch("drumgizmo_kits_generator.audio.logger")
    def test_convert_sample_rate_with_sox(
        self, mock_logger, mock_exists, mock_mkdtemp, mock_run, mock_which, sample_file
    ):
        """Test convert_sample_rate with SoX available."""
        # Setup mocks
        mock_which.return_value = "/usr/bin/sox"  # SoX is available
        mock_run.return_value = mock.MagicMock(returncode=0)
        temp_dir = "/tmp/drumgizmo_temp"
        mock_mkdtemp.return_value = temp_dir
        mock_exists.return_value = False  # File doesn't exist before creation

        # Setup logger mock
        debug_mock = mock.MagicMock()
        mock_logger.debug = debug_mock

        # Call the function
        result = audio.convert_sample_rate(sample_file, "48000")

        # Assertions
        assert result != sample_file  # Should return a new file
        assert temp_dir in result  # Should be in the temp dir

        # Verify SoX command was called with correct arguments
        mock_run.assert_called_once()
        # pylint: disable-next=unused-variable
        args, kwargs = mock_run.call_args
        sox_path = shutil.which("sox")
        assert args[0][0] == sox_path
        assert args[0][1] == sample_file
        assert args[0][2] == "-r"
        assert args[0][3] == "48000"
        assert temp_dir in args[0][4]  # Output file is in temp dir

        # Verify debug logging was called
        debug_mock.assert_called()

        mock_mkdtemp.assert_called_once_with(
            prefix=constants.DEFAULT_TEMP_DIR_PREFIX
        )  # Should have created a temp dir

    @mock.patch("shutil.which")
    @mock.patch("subprocess.run")
    @mock.patch("tempfile.mkdtemp")
    @mock.patch("os.path.exists")
    @mock.patch("os.rmdir")
    @mock.patch("os.remove")
    def test_convert_sample_rate_with_error(
        self,
        mock_remove,
        mock_rmdir,
        mock_exists,
        mock_mkdtemp,
        mock_run,
        mock_which,
        sample_file,
        mock_logger,
    ):
        """Test convert_sample_rate with SoX error."""
        # Setup mocks
        mock_which.return_value = "/usr/bin/sox"  # SoX is available
        mock_run.side_effect = subprocess.CalledProcessError(1, "sox")
        mock_mkdtemp.return_value = "/tmp/drumgizmo_temp"
        mock_exists.return_value = True  # File exists before removal

        # Call the function - it should raise AudioProcessingError
        with pytest.raises(audio.AudioProcessingError) as excinfo:
            audio.convert_sample_rate(sample_file, "48000")

        # Verify the error message
        assert "converting sample rate" in str(excinfo.value)
        assert "sox" in str(excinfo.value)
        mock_mkdtemp.assert_called_once_with(
            prefix=constants.DEFAULT_TEMP_DIR_PREFIX
        )  # Should have created a temp dir
        mock_run.assert_called_once()
        mock_rmdir.assert_called_once_with(
            "/tmp/drumgizmo_temp"
        )  # Should have cleaned up the temp dir

    @mock.patch("shutil.which")
    @mock.patch("subprocess.run")
    @mock.patch("tempfile.mkdtemp")
    @mock.patch("os.path.exists")
    @mock.patch("os.rmdir")
    @mock.patch("os.remove")
    def test_convert_sample_rate_with_error_and_stderr(
        self,
        mock_remove,
        mock_rmdir,
        mock_exists,
        mock_mkdtemp,
        mock_run,
        mock_which,
        sample_file,
        mock_logger,
    ):
        """Test convert_sample_rate with SoX error that includes stderr output."""
        # Setup mocks
        mock_which.return_value = "/usr/bin/sox"  # SoX is available
        error = subprocess.CalledProcessError(1, "sox")
        error.stderr = "SoX error: invalid sample rate"
        mock_run.side_effect = error
        temp_dir = "/tmp/drumgizmo_temp"
        mock_mkdtemp.return_value = temp_dir
        mock_exists.return_value = True  # File exists before removal

        # Call the function - it should raise AudioProcessingError
        with pytest.raises(audio.AudioProcessingError) as excinfo:
            audio.convert_sample_rate(sample_file, "48000")

        # Verify the error message includes stderr
        assert "converting sample rate" in str(excinfo.value)
        assert "SoX error: invalid sample rate" in str(excinfo.value)

        # Verify that mkdtemp was called with the right prefix
        mock_mkdtemp.assert_called_once_with(prefix=constants.DEFAULT_TEMP_DIR_PREFIX)

        # Verify that the temp directory was cleaned up
        mock_rmdir.assert_called_once_with(temp_dir)

    @mock.patch("shutil.which")
    @mock.patch("subprocess.run")
    @mock.patch("tempfile.mkdtemp")
    @mock.patch("os.path.exists")
    @mock.patch("os.rmdir")
    @mock.patch("os.remove")
    def test_convert_sample_rate_with_generic_exception(
        self,
        mock_remove,
        mock_rmdir,
        mock_exists,
        mock_mkdtemp,
        mock_run,
        mock_which,
        sample_file,
        mock_logger,
    ):
        """Test convert_sample_rate with a generic exception."""
        # Setup mocks
        mock_which.return_value = "/usr/bin/sox"  # SoX is available
        mock_run.side_effect = Exception("Unexpected error")
        temp_dir = "/tmp/drumgizmo_temp"
        mock_mkdtemp.return_value = temp_dir
        mock_exists.return_value = True  # File exists before removal

        # Call the function - it should raise AudioProcessingError
        with pytest.raises(audio.AudioProcessingError) as excinfo:
            audio.convert_sample_rate(sample_file, "48000")

        # Verify the error message
        assert "Unexpected error while converting sample rate" in str(excinfo.value)
        # Verify that mkdtemp was called with the right prefix
        mock_mkdtemp.assert_called_once_with(prefix=constants.DEFAULT_TEMP_DIR_PREFIX)
        # Verify that the temp directory was cleaned up
        mock_rmdir.assert_called_once_with(temp_dir)


class TestGetAudioInfo:
    """Tests for the get_audio_info function."""

    @mock.patch("shutil.which")
    def test_get_audio_info_no_soxi(self, mock_which, sample_file, mock_logger):
        """Test get_audio_info with soxi not available."""
        # Setup mocks
        mock_which.return_value = None  # soxi is not available

        # Call the function and expect a DependencyError
        with pytest.raises(audio.DependencyError) as excinfo:
            audio.get_audio_info(sample_file)

        # Verify the error message
        assert "soxi (part of SoX) not found" in str(excinfo.value)

    @mock.patch("shutil.which")
    @mock.patch("subprocess.run")
    @mock.patch("drumgizmo_kits_generator.audio.logger")
    def test_get_audio_info_with_soxi(self, mock_logger, mock_run, mock_which, sample_file):
        """Test get_audio_info with soxi available."""
        # Setup mocks
        mock_which.return_value = "/usr/bin/soxi"  # soxi is available

        # Setup logger mock
        debug_mock = mock.MagicMock()
        mock_logger.debug = debug_mock

        # Create mock responses for each subprocess call
        def mock_subprocess_run(cmd, **kwargs):
            result = mock.MagicMock()
            result.returncode = 0
            result.stdout = ""

            if "-c" in cmd:  # Channels
                result.stdout = "2\n"
            elif "-r" in cmd:  # Sample rate
                result.stdout = "44100\n"
            elif "-b" in cmd:  # Bit depth
                result.stdout = "24\n"
            elif "-D" in cmd:  # Duration
                result.stdout = "2.5\n"

            return result

        mock_run.side_effect = mock_subprocess_run

        # Call the function
        result = audio.get_audio_info(sample_file)

        # Verify the results
        assert result["channels"] == 2
        assert result["samplerate"] == 44100
        assert result["bits"] == 24
        assert result["duration"] == 2.5

        # Verify debug logging was called
        debug_mock.assert_called()

    @mock.patch("subprocess.run")
    @mock.patch("shutil.which")
    def test_get_audio_info_with_error(self, mock_which, mock_run, sample_file, mock_logger):
        """Test get_audio_info with soxi error."""
        # Setup mocks
        mock_which.return_value = "/usr/bin/soxi"  # soxi is available
        mock_run.side_effect = subprocess.CalledProcessError(1, "soxi")

        # Call the function - it should raise AudioProcessingError
        with pytest.raises(audio.AudioProcessingError) as excinfo:
            audio.get_audio_info(sample_file)

        # Verify the error message
        assert "getting audio information" in str(excinfo.value)
        assert "soxi" in str(excinfo.value)

    @mock.patch("subprocess.run")
    @mock.patch("shutil.which")
    def test_get_audio_info_with_error_and_stderr(
        self, mock_which, mock_run, sample_file, mock_logger
    ):
        """Test get_audio_info with soxi error that includes stderr output."""
        # Setup mocks
        mock_which.return_value = "/usr/bin/soxi"  # soxi is available
        error = subprocess.CalledProcessError(1, "soxi")
        error.stderr = "soxi ERROR: Failed to open input file"
        mock_run.side_effect = error

        # Call the function - it should raise AudioProcessingError
        with pytest.raises(audio.AudioProcessingError) as excinfo:
            audio.get_audio_info(sample_file)

        # Verify the error message includes stderr content
        assert "getting audio information" in str(excinfo.value)
        assert "soxi ERROR: Failed to open input file" in str(excinfo.value)

    @mock.patch("subprocess.run")
    @mock.patch("shutil.which")
    def test_get_audio_info_with_value_error(self, mock_which, mock_run, sample_file, mock_logger):
        """Test get_audio_info with a ValueError during parsing."""
        # Setup mocks
        mock_which.return_value = "/usr/bin/soxi"  # soxi is available

        # Return non-numeric value for channels to trigger ValueError
        def mock_subprocess_run(cmd, **kwargs):
            result = mock.MagicMock()
            result.returncode = 0

            if "-c" in cmd:  # Channels - return non-numeric value
                result.stdout = "stereo\n"  # This should cause a ValueError
            elif "-r" in cmd:  # Sample rate
                result.stdout = "44100\n"
            elif "-b" in cmd:  # Bit depth
                result.stdout = "24\n"
            elif "-D" in cmd:  # Duration
                result.stdout = "2.5\n"

            return result

        mock_run.side_effect = mock_subprocess_run

        # Call the function - it should raise AudioProcessingError
        with pytest.raises(audio.AudioProcessingError) as excinfo:
            audio.get_audio_info(sample_file)

        # Verify the error message
        assert "Failed to parse audio information" in str(excinfo.value)


class TestProcessSample:
    """Tests for the process_sample function."""

    @mock.patch("drumgizmo_kits_generator.utils.get_instrument_name")
    @mock.patch("drumgizmo_kits_generator.audio.get_audio_info")
    @mock.patch("drumgizmo_kits_generator.audio.convert_sample_rate")
    @mock.patch("drumgizmo_kits_generator.audio.create_velocity_variations")
    @mock.patch("os.makedirs")
    def test_process_sample_without_conversion_if_samplerate_matches(
        self,
        mock_makedirs,
        mock_create_velocity,
        mock_convert_sample_rate,
        mock_get_audio_info,
        mock_get_name,
        tmp_dir,
        sample_file,
    ):
        """Test process_sample n'appelle pas la conversion si le sample rate est déjà correct."""
        mock_get_name.return_value = "test_instrument"
        mock_create_velocity.return_value = ["file1.wav", "file2.wav", "file3.wav"]
        metadata = {
            "name": "Test Kit",
            "version": "1.0",
            "description": "Test description",
            "velocity_levels": 3,
            "variations_method": "linear",
            "samplerate": 44100,
        }
        mock_get_audio_info.return_value = {"samplerate": 44100}

        # Cas classique (audio_info non fourni, get_audio_info appelé)
        result = audio.process_sample(sample_file, tmp_dir, metadata)
        assert result == ["file1.wav", "file2.wav", "file3.wav"]
        mock_create_velocity.assert_called_once_with(
            sample_file,
            os.path.join(tmp_dir, "test_instrument", "samples"),
            metadata["velocity_levels"],
            "test_instrument",
            variations_method="linear",
        )
        mock_convert_sample_rate.assert_not_called()
        assert mock_get_audio_info.call_count == 1

        # Cas où audio_info est fourni (get_audio_info NE DOIT PAS être appelé)
        mock_get_audio_info.reset_mock()
        mock_create_velocity.reset_mock()
        mock_convert_sample_rate.reset_mock()
        result2 = audio.process_sample(
            sample_file, tmp_dir, metadata, audio_info={"samplerate": 44100}
        )
        assert result2 == ["file1.wav", "file2.wav", "file3.wav"]
        mock_create_velocity.assert_called_once()
        mock_convert_sample_rate.assert_not_called()
        mock_get_audio_info.assert_not_called()

    @mock.patch("drumgizmo_kits_generator.utils.get_instrument_name")
    @mock.patch("drumgizmo_kits_generator.audio.convert_sample_rate")
    @mock.patch("drumgizmo_kits_generator.audio.create_velocity_variations")
    @mock.patch("os.makedirs")
    @mock.patch("os.path.exists")
    @mock.patch("shutil.rmtree")
    def test_process_sample_with_sample_rate_conversion(
        self,
        mock_rmtree,
        mock_exists,
        mock_makedirs,
        mock_create_velocity,
        mock_convert_sample_rate,
        mock_get_name,
        tmp_dir,
        sample_file,
        metadata,
    ):
        """Test process_sample with sample rate conversion."""
        # Setup mocks
        mock_get_name.return_value = "test_instrument"
        temp_dir = "/tmp/drumgizmo_temp"
        converted_file = os.path.join(temp_dir, "converted.wav")
        mock_convert_sample_rate.return_value = converted_file
        mock_create_velocity.return_value = ["file1.wav", "file2.wav", "file3.wav"]
        mock_exists.return_value = True

        # Mock the temp directory creation
        with mock.patch("tempfile.mkdtemp") as mock_mkdtemp:
            mock_mkdtemp.return_value = temp_dir

            # Call the function
            result = audio.process_sample(sample_file, tmp_dir, metadata)

        # Assertions
        assert result == ["file1.wav", "file2.wav", "file3.wav"]
        mock_get_name.assert_called_once()
        mock_convert_sample_rate.assert_called_once_with(
            sample_file, metadata["samplerate"], target_dir=temp_dir
        )
        mock_create_velocity.assert_called_once_with(
            converted_file,
            os.path.join(tmp_dir, "test_instrument", "samples"),
            metadata["velocity_levels"],
            "test_instrument",
            variations_method="linear",
        )
        mock_rmtree.assert_called_once_with(temp_dir)

    @mock.patch("drumgizmo_kits_generator.utils.get_instrument_name")
    @mock.patch("drumgizmo_kits_generator.audio.convert_sample_rate")
    @mock.patch("drumgizmo_kits_generator.audio.create_velocity_variations")
    @mock.patch("os.makedirs")
    def test_process_sample_without_sample_rate_conversion(
        self,
        mock_makedirs,
        mock_create_velocity,
        mock_convert_sample_rate,
        mock_get_name,
        tmp_dir,
        sample_file,
    ):
        """Test process_sample without sample rate conversion."""
        # Setup mocks
        mock_get_name.return_value = "test_instrument"
        mock_create_velocity.return_value = ["file1.wav", "file2.wav", "file3.wav"]

        # Create metadata with samplerate
        metadata_with_samplerate = {
            "name": "Test Kit",
            "version": "1.0",
            "description": "Test description",
            "velocity_levels": 3,
            "variations_method": "linear",
            "samplerate": 44100,
        }

        # Patch get_audio_info pour simuler le même sample rate
        with mock.patch("drumgizmo_kits_generator.audio.get_audio_info") as mock_get_audio_info:
            mock_get_audio_info.return_value = {"samplerate": 44100}
            result = audio.process_sample(sample_file, tmp_dir, metadata_with_samplerate)

        # Assertions
        assert result == ["file1.wav", "file2.wav", "file3.wav"]
        mock_get_name.assert_called_once()
        mock_makedirs.assert_called_once_with(
            os.path.join(tmp_dir, "test_instrument", "samples"), exist_ok=True
        )
        mock_convert_sample_rate.assert_not_called()
        mock_create_velocity.assert_called_once_with(
            sample_file,
            os.path.join(tmp_dir, "test_instrument", "samples"),
            metadata_with_samplerate["velocity_levels"],
            "test_instrument",
            variations_method="linear",
        )

    @mock.patch("drumgizmo_kits_generator.utils.get_instrument_name")
    @mock.patch("drumgizmo_kits_generator.audio.convert_sample_rate")
    @mock.patch("drumgizmo_kits_generator.audio.create_velocity_variations")
    @mock.patch("os.makedirs")
    @mock.patch("os.path.exists")
    @mock.patch("shutil.rmtree")
    def test_process_sample_cleanup_temp_dirs(
        self,
        mock_rmtree,
        mock_exists,
        mock_makedirs,
        mock_create_velocity,
        mock_convert_sample_rate,
        mock_get_name,
        tmp_dir,
        sample_file,
        metadata,
    ):
        """Test process_sample cleans up temporary directories."""
        # Setup mocks
        mock_get_name.return_value = "test_instrument"
        temp_dir = "/tmp/drumgizmo_temp"
        converted_file = os.path.join(temp_dir, "converted.wav")
        mock_convert_sample_rate.return_value = converted_file
        mock_create_velocity.return_value = ["file1.wav", "file2.wav", "file3.wav"]
        mock_exists.return_value = True

        # Mock the temp directory creation
        with mock.patch("tempfile.mkdtemp") as mock_mkdtemp:
            mock_mkdtemp.return_value = temp_dir

            # Call the function
            result = audio.process_sample(sample_file, tmp_dir, metadata)

        # Assertions
        assert result == ["file1.wav", "file2.wav", "file3.wav"]
        mock_makedirs.assert_called_once_with(
            os.path.join(tmp_dir, "test_instrument", "samples"), exist_ok=True
        )
        mock_rmtree.assert_called_once_with(temp_dir)  # Should have cleaned up the temp dir

    @mock.patch("drumgizmo_kits_generator.utils.get_instrument_name")
    @mock.patch("drumgizmo_kits_generator.audio.create_velocity_variations")
    @mock.patch("os.makedirs")
    def test_process_sample_with_default_velocity_levels(
        self,
        mock_makedirs,
        mock_create_velocity,
        mock_get_name,
        tmp_dir,
        sample_file,
    ):
        """Test process_sample with default velocity levels."""
        # Setup mocks
        mock_get_name.return_value = "test_instrument"
        mock_create_velocity.return_value = ["file1.wav", "file2.wav", "file3.wav"]

        # Create metadata with samplerate and without velocity_levels
        metadata_with_samplerate = {
            "name": "Test Kit",
            "version": "1.0",
            "description": "Test description",
            "velocity_levels": constants.DEFAULT_VELOCITY_LEVELS,
            "samplerate": 44100,
            "variations_method": "linear",
        }

        # Patch get_audio_info pour simuler le même sample rate
        with mock.patch("drumgizmo_kits_generator.audio.get_audio_info") as mock_get_audio_info:
            mock_get_audio_info.return_value = {"samplerate": 44100}
            result = audio.process_sample(sample_file, tmp_dir, metadata_with_samplerate)

        # Assertions
        assert result == ["file1.wav", "file2.wav", "file3.wav"]
        mock_makedirs.assert_called_once_with(
            os.path.join(tmp_dir, "test_instrument", "samples"), exist_ok=True
        )
        mock_create_velocity.assert_called_once_with(
            sample_file,
            os.path.join(tmp_dir, "test_instrument", "samples"),
            constants.DEFAULT_VELOCITY_LEVELS,
            "test_instrument",
            variations_method="linear",
        )
