#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-arguments
# pylint: disable=unused-argument
"""
Tests for the utils module of the DrumGizmo kit generator.
"""

import os
import subprocess
import tempfile
from unittest import mock

import pytest

from drumgizmo_kits_generator import constants, exceptions, utils


@pytest.fixture
def mock_logger_fixture():
    """Mock logger functions."""
    with mock.patch("drumgizmo_kits_generator.logger.info") as mock_info, mock.patch(
        "drumgizmo_kits_generator.logger.debug"
    ) as mock_debug, mock.patch(
        "drumgizmo_kits_generator.logger.warning"
    ) as mock_warning, mock.patch(
        "drumgizmo_kits_generator.logger.error"
    ) as mock_error, mock.patch(
        "drumgizmo_kits_generator.logger.section"
    ) as mock_section:
        yield {
            "info": mock_info,
            "debug": mock_debug,
            "warning": mock_warning,
            "error": mock_error,
            "section": mock_section,
        }


@pytest.fixture
def sample_file_fixture():
    """Create a temporary audio file for testing."""
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
        temp_file_path = temp_file.name
    yield temp_file_path
    if os.path.exists(temp_file_path):
        os.unlink(temp_file_path)


class TestConvertSampleRate:
    """Tests for the convert_sample_rate function."""

    @mock.patch("shutil.which")
    def test_convert_sample_rate_no_sox(self, mock_which, sample_file_fixture, mock_logger_fixture):
        """Test convert_sample_rate with SoX not available."""
        # Setup mocks
        mock_which.return_value = None  # SoX is not available

        # Call the function and expect a DependencyError
        with pytest.raises(exceptions.DependencyError) as excinfo:
            utils.convert_sample_rate(sample_file_fixture, "48000")

        # Verify the error message
        assert "SoX not found" in str(excinfo.value)

        # No need to verify logger.error call as it's now handled in main.py
        # mock_logger_fixture["error"].assert_called_once()

    @mock.patch("shutil.which")
    @mock.patch("subprocess.run")
    @mock.patch("tempfile.mkdtemp")
    def test_convert_sample_rate_with_sox(
        self, mock_mkdtemp, mock_run, mock_which, sample_file_fixture, mock_logger_fixture
    ):
        """Test convert_sample_rate with SoX available."""
        # Setup mocks
        mock_which.return_value = "/usr/bin/sox"  # SoX is available
        mock_run.return_value = mock.MagicMock(returncode=0)
        temp_dir = "/tmp/drumgizmo_temp"
        mock_mkdtemp.return_value = temp_dir

        # Call the function
        result = utils.convert_sample_rate(sample_file_fixture, "48000")

        # Assertions
        assert result != sample_file_fixture  # Should return a new file
        assert temp_dir in result  # Should be in the temp directory
        assert mock_logger_fixture["debug"].call_count >= 1  # Log about conversion
        mock_run.assert_called_once()  # SoX command should be called

    @mock.patch("shutil.rmtree")
    @mock.patch("tempfile.mkdtemp")
    @mock.patch("subprocess.run")
    @mock.patch("shutil.which")
    def test_convert_sample_rate_with_error(
        self,
        mock_which,
        mock_run,
        mock_mkdtemp,
        mock_rmtree,
        sample_file_fixture,
        mock_logger_fixture,
    ):
        """Test convert_sample_rate with SoX error."""
        # Setup mocks
        mock_which.return_value = "/usr/bin/sox"  # SoX is available
        mock_run.side_effect = subprocess.CalledProcessError(1, "sox")
        temp_dir = "/tmp/drumgizmo_temp"
        mock_mkdtemp.return_value = temp_dir

        # Call the function - it should raise AudioProcessingError
        with pytest.raises(utils.AudioProcessingError) as excinfo:
            utils.convert_sample_rate(sample_file_fixture, "48000")

        # Verify the error message
        assert "Failed to convert sample rate" in str(excinfo.value)

        # Verify that temp dir is cleaned up
        mock_rmtree.assert_called_once_with(temp_dir, ignore_errors=True)

    @mock.patch("shutil.rmtree")
    @mock.patch("tempfile.mkdtemp")
    @mock.patch("subprocess.run")
    @mock.patch("shutil.which")
    def test_convert_sample_rate_with_error_and_stderr(
        self,
        mock_which,
        mock_run,
        mock_mkdtemp,
        mock_rmtree,
        sample_file_fixture,
        mock_logger_fixture,
    ):
        """Test convert_sample_rate with SoX error that includes stderr output."""
        # Setup mocks
        mock_which.return_value = "/usr/bin/sox"  # SoX is available
        error = subprocess.CalledProcessError(1, "sox")
        error.stderr = "SoX ERROR: Failed to open input file"
        mock_run.side_effect = error
        temp_dir = "/tmp/drumgizmo_temp"
        mock_mkdtemp.return_value = temp_dir

        # Call the function - it should raise AudioProcessingError
        with pytest.raises(utils.AudioProcessingError) as excinfo:
            utils.convert_sample_rate(sample_file_fixture, "48000")

        # Verify the error message includes stderr content
        assert "Failed to convert sample rate" in str(excinfo.value)
        assert "SoX ERROR: Failed to open input file" in str(excinfo.value)

        # Verify that the temporary directory is cleaned up
        mock_rmtree.assert_called_once_with(temp_dir, ignore_errors=True)

    @mock.patch("shutil.rmtree")
    @mock.patch("tempfile.mkdtemp")
    @mock.patch("subprocess.run")
    @mock.patch("shutil.which")
    def test_convert_sample_rate_with_generic_exception(
        self,
        mock_which,
        mock_run,
        mock_mkdtemp,
        mock_rmtree,
        sample_file_fixture,
        mock_logger_fixture,
    ):
        """Test convert_sample_rate with a generic exception."""
        # Setup mocks
        mock_which.return_value = "/usr/bin/sox"  # SoX is available
        mock_run.side_effect = Exception("Unexpected error")
        temp_dir = "/tmp/drumgizmo_temp"
        mock_mkdtemp.return_value = temp_dir

        # Call the function - it should raise AudioProcessingError
        with pytest.raises(utils.AudioProcessingError) as excinfo:
            utils.convert_sample_rate(sample_file_fixture, "48000")

        # Verify the error message
        assert "Unexpected error during sample rate conversion" in str(excinfo.value)

        # Verify that the temporary directory is cleaned up
        mock_rmtree.assert_called_once_with(temp_dir, ignore_errors=True)


class TestGetAudioInfo:
    """Tests for the get_audio_info function."""

    @mock.patch("shutil.which")
    def test_get_audio_info_no_soxi(self, mock_which, sample_file_fixture, mock_logger_fixture):
        """Test get_audio_info with soxi not available."""
        # Setup mocks
        mock_which.return_value = None  # soxi is not available

        # Call the function and expect a DependencyError
        with pytest.raises(exceptions.DependencyError) as excinfo:
            utils.get_audio_info(sample_file_fixture)

        # Verify the error message
        assert "SoX (soxi) not found" in str(excinfo.value)

        # No need to verify logger.error call as it's now handled in main.py
        # mock_logger_fixture["error"].assert_called_once()

    @mock.patch("shutil.which")
    @mock.patch("subprocess.run")
    def test_get_audio_info_with_soxi(
        self, mock_run, mock_which, sample_file_fixture, mock_logger_fixture
    ):
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
        result = utils.get_audio_info(sample_file_fixture)

        # Assertions
        assert result["channels"] == 2
        assert result["samplerate"] == 44100
        assert result["bits"] == 24
        assert result["duration"] == 2.5
        assert mock_logger_fixture["debug"].call_count >= 1  # Debug log about audio info

    @mock.patch("subprocess.run")
    @mock.patch("shutil.which")
    def test_get_audio_info_with_error(
        self, mock_which, mock_run, sample_file_fixture, mock_logger_fixture
    ):
        """Test get_audio_info with soxi error."""
        # Setup mocks
        mock_which.return_value = "/usr/bin/soxi"  # soxi is available
        mock_run.side_effect = subprocess.CalledProcessError(1, "soxi")

        # Call the function - it should raise AudioProcessingError
        with pytest.raises(utils.AudioProcessingError) as excinfo:
            utils.get_audio_info(sample_file_fixture)

        # Verify the error message
        assert "Failed to get audio information" in str(excinfo.value)

    @mock.patch("subprocess.run")
    @mock.patch("shutil.which")
    def test_get_audio_info_with_error_and_stderr(
        self, mock_which, mock_run, sample_file_fixture, mock_logger_fixture
    ):
        """Test get_audio_info with soxi error that includes stderr output."""
        # Setup mocks
        mock_which.return_value = "/usr/bin/soxi"  # soxi is available
        error = subprocess.CalledProcessError(1, "soxi")
        error.stderr = "soxi ERROR: Failed to open input file"
        mock_run.side_effect = error

        # Call the function - it should raise AudioProcessingError
        with pytest.raises(utils.AudioProcessingError) as excinfo:
            utils.get_audio_info(sample_file_fixture)

        # Verify the error message includes stderr content
        assert "Failed to get audio information" in str(excinfo.value)
        assert "soxi ERROR: Failed to open input file" in str(excinfo.value)

    @mock.patch("subprocess.run")
    @mock.patch("shutil.which")
    def test_get_audio_info_with_value_error(
        self, mock_which, mock_run, sample_file_fixture, mock_logger_fixture
    ):
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
        with pytest.raises(utils.AudioProcessingError) as excinfo:
            utils.get_audio_info(sample_file_fixture)

        # Verify the error message
        assert "Failed to parse audio information" in str(excinfo.value)

    @mock.patch("os.path.isfile")
    @mock.patch("shutil.which")
    def test_get_audio_info_file_not_found(
        self, mock_which, mock_isfile, sample_file_fixture, mock_logger_fixture
    ):
        """Test get_audio_info with a file that doesn't exist."""
        # Setup mocks
        mock_which.return_value = "/usr/bin/soxi"  # soxi is available
        mock_isfile.return_value = False  # File doesn't exist

        # Call the function - it should raise AudioProcessingError
        with pytest.raises(utils.AudioProcessingError) as excinfo:
            utils.get_audio_info(sample_file_fixture)

        # Verify the error message
        assert "Audio file not found" in str(excinfo.value)


class TestCleanInstrumentName:
    """Tests for the clean_instrument_name function."""

    def test_clean_instrument_name_basic(self):
        """Test clean_instrument_name with basic input."""
        # Test with a simple filename (without extension)
        assert utils.clean_instrument_name("Kick") == "Kick"
        assert utils.clean_instrument_name("Snare") == "Snare"
        assert utils.clean_instrument_name("HiHat") == "HiHat"

    def test_clean_instrument_name_with_path(self):
        """Test clean_instrument_name with path."""
        # Test with paths (without extension)
        assert utils.clean_instrument_name("Kick") == "Kick"
        assert utils.clean_instrument_name("Snare") == "Snare"

    def test_clean_instrument_name_with_special_chars(self):
        """Test clean_instrument_name with special characters."""
        # Test with special characters (without extension)
        assert utils.clean_instrument_name("Kick-Drum") == "Kick-Drum"
        assert utils.clean_instrument_name("Snare-Left") == "Snare-Left"
        assert utils.clean_instrument_name("Hi-Hat") == "Hi-Hat"

    def test_clean_instrument_name_with_numbers(self):
        """Test clean_instrument_name with numbers."""
        # Test with numbers (without extension)
        assert utils.clean_instrument_name("Kick01") == "Kick01"
        assert utils.clean_instrument_name("Snare_02") == "Snare_02"

    def test_clean_instrument_name_with_velocity_prefix(self):
        """Test clean_instrument_name with velocity prefix."""
        # Test with velocity prefix
        assert utils.clean_instrument_name("1-Kick") == "Kick"
        assert utils.clean_instrument_name("2-Snare") == "Snare"
        assert utils.clean_instrument_name("3-HiHat") == "HiHat"

    def test_clean_instrument_name_with_converted_suffix(self):
        """Test clean_instrument_name with _converted suffix."""
        # Test with _converted suffix
        assert utils.clean_instrument_name("Kick_converted") == "Kick"
        assert utils.clean_instrument_name("Snare_converted") == "Snare"
        assert utils.clean_instrument_name("1-HiHat_converted") == "HiHat"


class TestScanSourceFiles:
    """Tests for the scan_source_files function."""

    def test_scan_source_files(self):
        """Test scan_source_files with various extensions."""
        # Create a temporary directory with test files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create some test files
            wav_file = os.path.join(temp_dir, "test1.wav")
            flac_file = os.path.join(temp_dir, "test2.flac")
            mp3_file = os.path.join(temp_dir, "test3.mp3")
            txt_file = os.path.join(temp_dir, "test4.txt")

            # Create subdirectory with more files
            subdir = os.path.join(temp_dir, "subdir")
            os.makedirs(subdir)
            subdir_wav = os.path.join(subdir, "subtest1.wav")
            subdir_flac = os.path.join(subdir, "subtest2.flac")

            # Create all the files
            for file_path in [wav_file, flac_file, mp3_file, txt_file, subdir_wav, subdir_flac]:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write("dummy content")

            # Test with various extension filters

            # Test with wav only
            result = utils.scan_source_files(temp_dir, ["wav"])
            assert len(result) == 2
            assert wav_file in result
            assert subdir_wav in result
            assert flac_file not in result
            assert mp3_file not in result
            assert txt_file not in result

            # Test with wav and flac
            result = utils.scan_source_files(temp_dir, ["wav", "flac"])
            assert len(result) == 4
            assert wav_file in result
            assert flac_file in result
            assert subdir_wav in result
            assert subdir_flac in result
            assert mp3_file not in result
            assert txt_file not in result

            # Test with all audio formats
            result = utils.scan_source_files(temp_dir, ["wav", "flac", "mp3"])
            assert len(result) == 5
            assert wav_file in result
            assert flac_file in result
            assert mp3_file in result
            assert subdir_wav in result
            assert subdir_flac in result
            assert txt_file not in result

            # Test with case insensitivity
            result = utils.scan_source_files(temp_dir, ["WAV", "FLAC"])
            assert len(result) == 4
            assert wav_file in result
            assert flac_file in result
            assert subdir_wav in result
            assert subdir_flac in result

            # Test with empty extensions list
            result = utils.scan_source_files(temp_dir, [])
            assert len(result) == 0


class TestValidateDirectories:
    """Tests for the validate_directories function."""

    @mock.patch("os.path.isdir")
    @mock.patch("os.path.isfile")
    def test_validate_directories_all_valid(self, mock_isfile, mock_isdir, mock_logger_fixture):
        """Test validate_directories with all valid paths."""
        # Setup mocks
        mock_isdir.return_value = True
        mock_isfile.return_value = True

        # Call the function
        utils.validate_directories("/path/to/source", "/path/to/target")

        # Test with config file
        utils.validate_directories(
            "/path/to/source", "/path/to/target", constants.DEFAULT_CONFIG_FILE
        )

        # Assertions
        mock_isdir.assert_called()

    @mock.patch("os.path.isdir")
    def test_validate_directories_invalid_source(self, mock_isdir, mock_logger_fixture):
        """Test validate_directories with invalid source directory."""
        # Setup mocks
        mock_isdir.side_effect = lambda path: path != "/invalid/source"

        # Call the function and expect a DirectoryError
        with pytest.raises(utils.DirectoryError) as excinfo:
            utils.validate_directories("/invalid/source", "/valid/target")

        # Verify the error message
        assert "Source directory does not exist" in str(excinfo.value)

        # No need to verify logger.error call as it's now handled in main.py
        # mock_logger_fixture["error"].assert_called_once()

    @mock.patch("os.path.isdir")
    @mock.patch("os.path.exists")
    @mock.patch("os.path.dirname")
    @mock.patch("os.path.abspath")
    def test_validate_directories_invalid_target_parent(
        self, mock_abspath, mock_dirname, mock_exists, mock_isdir, mock_logger_fixture
    ):
        """Test validate_directories with invalid target parent directory."""
        # Setup mocks
        mock_isdir.return_value = True  # Source directory exists
        mock_exists.return_value = False  # Target doesn't exist
        mock_abspath.return_value = "/invalid/target"
        mock_dirname.return_value = "/invalid"
        mock_isdir.side_effect = lambda path: path != "/invalid"  # Parent directory doesn't exist

        # Call the function and expect a DirectoryError
        with pytest.raises(utils.DirectoryError) as excinfo:
            utils.validate_directories("/valid/source", "/invalid/target")

        # Verify the error message
        assert "Parent directory of target does not exist" in str(excinfo.value)

        # No need to verify logger.error call as it's now handled in main.py
        # mock_logger_fixture["error"].assert_called_once()

    @mock.patch("os.path.isdir")
    @mock.patch("os.path.isfile")
    @mock.patch("os.path.exists")
    def test_validate_directories_invalid_config(
        self, mock_exists, mock_isfile, mock_isdir, mock_logger_fixture
    ):
        """Test validate_directories with invalid config file."""
        # Setup mocks
        mock_isdir.return_value = True  # Source and target directories exist
        mock_exists.return_value = True  # Target exists
        mock_isfile.return_value = False  # Config file doesn't exist

        # Call the function and expect a DirectoryError
        with pytest.raises(utils.DirectoryError) as excinfo:
            utils.validate_directories("/valid/source", "/valid/target", "/invalid/config.ini")

        # Verify the error message
        assert "Configuration file does not exist" in str(excinfo.value)

        # No need to verify logger.error call as it's now handled in main.py
        # mock_logger_fixture["error"].assert_called_once()

    @mock.patch("os.path.isdir")
    @mock.patch("os.path.isfile")
    @mock.patch("os.path.dirname")
    @mock.patch("os.path.abspath")
    def test_validate_directories_default_config(
        self, mock_abspath, mock_dirname, mock_isfile, mock_isdir
    ):
        """Test validate_directories with default config file."""
        # Setup mocks
        mock_isdir.return_value = True
        mock_isfile.return_value = False
        mock_dirname.return_value = "/path/to/parent"
        mock_abspath.return_value = "/path/to/target"

        # Call the function with the default config file
        utils.validate_directories(
            "/path/to/source", "/path/to/target", constants.DEFAULT_CONFIG_FILE
        )

        # Assertions
        mock_isfile.assert_not_called()  # Should not check if default config exists


class TestPrepareTargetDirectory:
    """Tests for the prepare_target_directory function."""

    @mock.patch("os.path.exists")
    @mock.patch("os.makedirs")
    def test_prepare_target_directory_new(self, mock_makedirs, mock_exists, mock_logger_fixture):
        """Test prepare_target_directory with a new directory."""
        # Setup mocks
        mock_exists.return_value = False

        # Call the function
        utils.prepare_target_directory("/path/to/target")

        # Assertions
        mock_makedirs.assert_called_once_with("/path/to/target")
        assert mock_logger_fixture["section"].call_count >= 1
        assert mock_logger_fixture["info"].call_count >= 1

    @mock.patch("os.path.exists")
    @mock.patch("os.path.isdir")
    @mock.patch("os.listdir")
    @mock.patch("os.path.join")
    @mock.patch("shutil.rmtree")
    @mock.patch("os.remove")
    def test_prepare_target_directory_existing(
        self,
        mock_remove,
        mock_rmtree,
        mock_join,
        mock_listdir,
        mock_isdir,
        mock_exists,
        mock_logger_fixture,
    ):
        """Test prepare_target_directory with an existing directory."""
        # Setup mocks
        mock_exists.return_value = True
        mock_listdir.return_value = ["file1.txt", "file2.txt", "dir1"]

        # Mock os.path.join to return predictable paths
        def mock_join_paths(dir_path, item):
            return f"{dir_path}/{item}"

        mock_join.side_effect = mock_join_paths

        # Mock os.path.isdir to identify directories
        def mock_is_dir(path):
            return "dir" in path

        mock_isdir.side_effect = mock_is_dir

        # Call the function
        utils.prepare_target_directory("/path/to/target")

        # Assertions
        assert mock_logger_fixture["section"].call_count >= 1
        assert mock_logger_fixture["info"].call_count >= 1
        assert mock_listdir.call_count == 1

        # Check that directories are removed with rmtree
        mock_rmtree.assert_called_once_with("/path/to/target/dir1")

        # Check that files are removed with os.remove
        assert mock_remove.call_count == 2
        mock_remove.assert_any_call("/path/to/target/file1.txt")
        mock_remove.assert_any_call("/path/to/target/file2.txt")


class TestCheckDependency:
    """Tests for the check_dependency function."""

    @mock.patch("shutil.which")
    def test_check_dependency_found(self, mock_which, mock_logger_fixture):
        """Test check_dependency with a command that is found."""
        # Setup mocks
        mock_which.return_value = "/usr/bin/test_command"

        # Call the function - should not raise an exception
        utils.check_dependency("test_command")

        # Verify that logger.error was not called
        mock_logger_fixture["error"].assert_not_called()

    @mock.patch("shutil.which")
    def test_check_dependency_not_found(self, mock_which, mock_logger_fixture):
        """Test check_dependency with dependency not found."""
        # Setup mocks
        mock_which.return_value = None

        # Call the function and expect a DependencyError
        with pytest.raises(exceptions.DependencyError) as excinfo:
            utils.check_dependency("test_command")

        # Verify the error message contains the command name
        assert "test_command" in str(excinfo.value)
        assert "not found" in str(excinfo.value)

        # No need to verify logger.error call as it's now handled in main.py
        # mock_logger_fixture["error"].assert_called_once()

    @mock.patch("shutil.which")
    def test_check_dependency_custom_message(self, mock_which, mock_logger_fixture):
        """Test check_dependency with a custom error message."""
        # Setup mocks
        mock_which.return_value = None
        custom_message = "Custom error message for test_command"

        # Call the function and expect a DependencyError
        with pytest.raises(exceptions.DependencyError) as excinfo:
            utils.check_dependency("test_command", custom_message)

        # Verify the error message
        assert custom_message == str(excinfo.value)

        # No need to verify logger.error call as it's now handled in main.py
        # mock_logger_fixture["error"].assert_called_once()
