#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name
# pylint: disable=too-many-arguments
# pylint: disable=unused-argument
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
    def test_convert_sample_rate_with_sox(
        self, mock_mkdtemp, mock_run, mock_which, sample_file, mock_logger
    ):
        """Test convert_sample_rate with SoX available."""
        # Setup mocks
        mock_which.return_value = "/usr/bin/sox"  # SoX is available
        mock_run.return_value = mock.MagicMock(returncode=0)
        temp_dir = "/tmp/drumgizmo_temp"
        mock_mkdtemp.return_value = temp_dir

        # Call the function
        result = audio.convert_sample_rate(sample_file, "48000")

        # Assertions
        assert result != sample_file  # Should return a new file
        assert temp_dir in result  # Should be in the temp directory
        assert mock_logger["debug"].call_count >= 1  # Log about conversion
        mock_run.assert_called_once()  # SoX command should be called
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
        assert "SoX (soxi) not found" in str(excinfo.value)

    @mock.patch("shutil.which")
    @mock.patch("subprocess.run")
    def test_get_audio_info_with_soxi(self, mock_run, mock_which, sample_file, mock_logger):
        """Test get_audio_info with soxi available."""
        # Setup mocks
        mock_which.return_value = "/usr/bin/soxi"  # soxi is available

        # Mock subprocess.run to return different values for different commands
        def mock_subprocess_run(cmd, **kwargs):
            result = mock.MagicMock()
            result.returncode = 0

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

        # Assertions
        assert result["channels"] == 2
        assert result["samplerate"] == 44100
        assert result["bits"] == 24
        assert result["duration"] == 2.5
        assert mock_logger["debug"].call_count >= 1  # Debug log about audio info

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

    @mock.patch("drumgizmo_kits_generator.utils.clean_instrument_name")
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
        mock_clean_name,
        tmp_dir,
        sample_file,
        metadata,
    ):
        """Test process_sample with sample rate conversion."""
        # Setup mocks
        mock_clean_name.return_value = "test_instrument"
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
        mock_clean_name.assert_called_once()
        mock_convert_sample_rate.assert_called_once_with(
            sample_file, metadata["samplerate"], target_dir=temp_dir
        )
        mock_create_velocity.assert_called_once_with(
            converted_file,
            os.path.join(tmp_dir, "test_instrument", "samples"),
            metadata["velocity_levels"],
            "test_instrument",
        )
        mock_rmtree.assert_called_once_with(temp_dir)

    @mock.patch("drumgizmo_kits_generator.utils.clean_instrument_name")
    @mock.patch("drumgizmo_kits_generator.audio.convert_sample_rate")
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
        mock_clean_name,
        tmp_dir,
        sample_file,
        metadata,
    ):
        """Test process_sample cleans up temporary directories."""
        # Setup mocks
        mock_clean_name.return_value = "test_instrument"
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
        mock_rmtree.assert_called_once_with(temp_dir)  # Should have cleaned up the temp dir

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
            "velocity_levels": constants.DEFAULT_VELOCITY_LEVELS,
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
