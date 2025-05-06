#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name
# pylint: disable=unspecified-encoding
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-arguments
# pylint: disable=too-many-locals
# pylint: disable=too-many-lines
# pylint: disable=attribute-defined-outside-init
# pylint: disable=unused-argument
"""
Tests for the main module of the DrumGizmo kit generator.
"""

import argparse
import io
import os
import shutil
import tempfile
from unittest import mock

import pytest

from drumgizmo_kits_generator import cli, config, constants, main, utils
from drumgizmo_kits_generator.exceptions import DependencyError


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
def temp_dir():
    """Create a temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Clean up
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_config_file(temp_dir):
    """Create a sample configuration file for testing."""
    config_content = """[drumgizmo_kit_generator]
name = "Test Kit"
version = "1.0"
description = "Test description"
notes = "Test notes"
author = "Test Author"
license = "CC-BY-SA"
website = "https://example.com"
samplerate = "48000"
velocity_levels = 3
midi_note_min = 0
midi_note_max = 127
midi_note_median = 60
extensions = "wav,flac,ogg"
channels = "Left,Right,Overhead"
main_channels = "Left,Right"
"""
    config_path = os.path.join(temp_dir, "test-config.ini")
    with open(config_path, "w") as f:
        f.write(config_content)
    yield config_path


@pytest.fixture
def sample_args():
    """Create sample command line arguments for testing."""
    args = argparse.Namespace()
    args.source = "/path/to/source"
    args.target = "/path/to/target"
    args.config = constants.DEFAULT_CONFIG_FILE
    args.verbose = False
    args.dry_run = False
    args.name = None
    args.version = None
    args.description = None
    args.notes = None
    args.author = None
    args.license = None
    args.website = None
    args.logo = None
    args.samplerate = None
    args.extra_files = None
    args.velocity_levels = None
    args.midi_note_min = None
    args.midi_note_max = None
    args.midi_note_median = None
    args.extensions = None
    args.channels = None
    args.main_channels = None
    return args


@pytest.fixture
def temp_config_file():
    """Create a temporary configuration file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ini", delete=False) as temp_file:
        temp_file.write(
            """[drumgizmo_kit_generator]
name = Test Kit
version = 1.0.0
description = Test description
notes = Test notes
author = Test Author
license = Test License
website = https://example.com
logo = logo.png
samplerate = 44100
extra_files = file1.txt,file2.txt
velocity_levels = 5
midi_note_min = 30
midi_note_max = 90
midi_note_median = 60
extensions = wav,flac
channels = Left,Right
main_channels = Left,Right
"""
        )
        temp_file_path = temp_file.name

    yield temp_file_path

    # Clean up
    if os.path.exists(temp_file_path):
        os.unlink(temp_file_path)


class TestPrepareMetadata:
    """Tests for the prepare_metadata function."""

    def test_prepare_metadata(self):
        """Test prepare_metadata correctly processes configuration data."""
        # Create config data
        config_data = {
            "name": "Test Kit",
            "version": "1.0",
            "description": "Test description",
            "notes": "Test notes",
            "author": "Test Author",
            "license": "CC-BY-SA",
            "website": "https://example.com",
            "logo": "logo.png",
            "samplerate": "48000",
            "extra_files": ["file1.txt"],
            "velocity_levels": 4,
            "midi_note_min": 0,
            "midi_note_max": 127,
            "midi_note_median": 60,
            "extensions": ["wav", "flac", "ogg"],
            "channels": ["Left", "Right", "Overhead"],
            "main_channels": ["Left", "Right"],
        }

        # Call the function from config module
        metadata = config.prepare_metadata(config_data)

        # Check that metadata contains all expected keys
        assert metadata["name"] == "Test Kit"
        assert metadata["version"] == "1.0"
        assert metadata["description"] == "Test description"
        assert metadata["notes"] == "Test notes"
        assert metadata["author"] == "Test Author"
        assert metadata["license"] == "CC-BY-SA"
        assert metadata["website"] == "https://example.com"
        assert metadata["logo"] == "logo.png"
        assert metadata["samplerate"] == 48000
        assert metadata["extra_files"] == ["file1.txt"]
        assert metadata["velocity_levels"] == 4
        assert metadata["midi_note_min"] == 0
        assert metadata["midi_note_max"] == 127
        assert metadata["midi_note_median"] == 60
        assert metadata["extensions"] == ["wav", "flac", "ogg"]
        assert metadata["channels"] == ["Left", "Right", "Overhead"]
        assert metadata["main_channels"] == ["Left", "Right"]

        # In the actual implementation, the instruments list might be added elsewhere
        # So we'll just check that the metadata contains the original config data
        for key, value in config_data.items():
            if key == "samplerate":
                assert metadata[key] == int(value)
            else:
                assert metadata[key] == value

    def test_prepare_metadata_with_string_values(self):
        """Test prepare_metadata with string values."""
        config_data = {
            "name": "Test Kit",
            "version": "1.0.0",
            "description": "Test description",
            "notes": "Test notes",
            "author": "Test Author",
            "license": "Test License",
            "website": "https://example.com",
            "logo": "logo.png",
            "samplerate": "44100",
            "extra_files": "file1.txt,file2.txt",
            "velocity_levels": "5",
            "midi_note_min": "30",
            "midi_note_max": "90",
            "midi_note_median": "60",
            "extensions": "wav,flac",
            "channels": "Left,Right",
            "main_channels": "Left,Right",
        }

        # Call the function from config module
        metadata = config.prepare_metadata(config_data)

        assert metadata["name"] == "Test Kit"
        assert metadata["velocity_levels"] == 5
        assert metadata["midi_note_min"] == 30
        assert metadata["midi_note_max"] == 90
        assert metadata["midi_note_median"] == 60
        assert metadata["samplerate"] == 44100

    def test_prepare_metadata_with_integer_values(self):
        """Test prepare_metadata with integer values."""
        config_data = {
            "name": "Test Kit",
            "version": "1.0.0",
            "description": "Test description",
            "notes": "Test notes",
            "author": "Test Author",
            "license": "Test License",
            "website": "https://example.com",
            "logo": "logo.png",
            "samplerate": "44100",
            "extra_files": "file1.txt,file2.txt",
            "velocity_levels": 5,  # Already an integer
            "midi_note_min": 30,  # Already an integer
            "midi_note_max": 90,  # Already an integer
            "midi_note_median": 60,  # Already an integer
            "extensions": "wav,flac",
            "channels": "Left,Right",
            "main_channels": "Left,Right",
        }

        # Call the function from config module
        metadata = config.prepare_metadata(config_data)

        assert metadata["name"] == "Test Kit"
        assert metadata["velocity_levels"] == 5
        assert metadata["midi_note_min"] == 30
        assert metadata["midi_note_max"] == 90
        assert metadata["midi_note_median"] == 60
        assert metadata["samplerate"] == 44100


class TestEvaluateMidiMapping:
    """Tests for the evaluate_midi_mapping function."""

    def test_evaluate_midi_mapping_with_valid_input(self, mock_logger):
        """Test evaluate_midi_mapping with valid input."""
        # Setup
        audio_files = [
            "/path/to/source/Kick.wav",
            "/path/to/source/Snare.wav",
            "/path/to/source/HiHat.wav",
        ]

        metadata = {"midi_note_min": 30, "midi_note_max": 90, "midi_note_median": 60}

        # Mock utils functions
        with mock.patch(
            "drumgizmo_kits_generator.utils.extract_instrument_names"
        ) as mock_extract, mock.patch(
            "drumgizmo_kits_generator.utils.calculate_midi_mapping"
        ) as mock_calculate:
            # Configure mocks
            mock_extract.return_value = ["Kick", "Snare", "HiHat"]
            mock_calculate.return_value = {"Kick": 30, "Snare": 60, "HiHat": 90}

            # Call the function
            result = utils.evaluate_midi_mapping(audio_files, metadata)

            # Assertions
            mock_extract.assert_called_once_with(audio_files)
            mock_calculate.assert_called_once_with(
                ["Kick", "Snare", "HiHat"], {"min": 30, "max": 90, "median": 60}
            )
            assert result == {"Kick": 30, "Snare": 60, "HiHat": 90}

    def test_evaluate_midi_mapping_with_empty_files(self, mock_logger):
        """Test evaluate_midi_mapping with empty input list."""
        # Setup
        audio_files = []
        metadata = {"midi_note_min": 30, "midi_note_max": 90, "midi_note_median": 60}

        # Call the function
        result = utils.evaluate_midi_mapping(audio_files, metadata)

        # Assertions
        assert not result

    def test_evaluate_midi_mapping_with_missing_metadata(self, mock_logger):
        """Test evaluate_midi_mapping with missing metadata keys."""
        # Setup
        audio_files = ["/path/to/source/Kick.wav"]
        metadata = {}  # Missing required metadata keys

        # Mock utils functions
        with mock.patch(
            "drumgizmo_kits_generator.utils.extract_instrument_names"
        ) as mock_extract, mock.patch(
            "drumgizmo_kits_generator.utils.calculate_midi_mapping"
        ) as mock_calculate:
            # Configure mocks
            mock_extract.return_value = ["Kick"]
            mock_calculate.return_value = {"Kick": 60}  # Default value when min/max not specified

            # Call the function
            result = utils.evaluate_midi_mapping(audio_files, metadata)

            # Assertions
            mock_extract.assert_called_once_with(audio_files)
            mock_calculate.assert_called_once_with(
                ["Kick"], {"min": None, "max": None, "median": None}
            )
            assert result == {"Kick": 60}


class TestMain:
    """Tests for the main function."""

    def setup_method(self):
        """Initialize test data."""
        self.config_data = {
            "name": "Test Kit",
            "version": "1.0.0",
            "description": "Test description",
            "notes": "Test notes",
            "author": "Test Author",
            "license": "Test License",
            "website": "https://example.com",
            "logo": "logo.png",
            "samplerate": "44100",
            "extra_files": "file1.txt,file2.txt",
            "velocity_levels": "5",
            "midi_note_min": "30",
            "midi_note_max": "90",
            "midi_note_median": "60",
            "extensions": "wav,flac",
            "channels": "Left,Right",
            "main_channels": "Left,Right",
        }

    # pylint: disable=too-many-arguments
    @mock.patch("drumgizmo_kits_generator.cli.parse_arguments")
    @mock.patch("drumgizmo_kits_generator.validators.validate_directories")
    @mock.patch(
        "drumgizmo_kits_generator.main.load_configuration"
    )  # Modifié pour cibler l'import dans main
    @mock.patch("drumgizmo_kits_generator.config.prepare_metadata")
    @mock.patch("drumgizmo_kits_generator.cli.print_metadata")
    @mock.patch("drumgizmo_kits_generator.utils.scan_source_files")
    @mock.patch("drumgizmo_kits_generator.cli.print_samples_info")
    @mock.patch("drumgizmo_kits_generator.cli.print_midi_mapping")
    @mock.patch("drumgizmo_kits_generator.logger.message")
    def test_main_dry_run(
        self,
        mock_message,
        mock_print_midi_mapping,
        mock_print_samples_info,
        mock_scan_source_files,
        mock_print_metadata,
        mock_prepare_metadata,
        mock_load_configuration,
        mock_validate_directories,
        mock_parse_arguments,
    ):
        """Test main function in dry run mode."""
        # Setup mocks
        args = argparse.Namespace()
        args.source = "/path/to/source"
        args.target = "/path/to/target"
        args.config = constants.DEFAULT_CONFIG_FILE
        args.verbose = False
        args.dry_run = True
        mock_parse_arguments.return_value = args

        # La configuration est déjà transformée et validée par load_configuration
        config_data = dict(self.config_data)
        config_data.update(
            {
                "source": "/path/to/source",
                "target": "/path/to/target",
                "config": constants.DEFAULT_CONFIG_FILE,
                "verbose": False,
                "dry_run": True,
            }
        )
        mock_load_configuration.return_value = config_data

        metadata = dict(config_data)
        metadata["instruments"] = []
        mock_prepare_metadata.return_value = metadata

        audio_files = [
            "/path/to/source/Kick.wav",
            "/path/to/source/Snare.wav",
        ]
        mock_scan_source_files.return_value = audio_files

        # Call the function
        main.main()

        # Check that dry run message was displayed
        mock_print_samples_info.assert_called_once_with(audio_files, metadata)
        mock_print_midi_mapping.assert_called_once_with(audio_files, metadata)
        mock_message.assert_called_with("\nDry run mode enabled, stopping here")

        # Verify that all mocks were used
        mock_parse_arguments.assert_called_once()
        mock_validate_directories.assert_called_once()
        mock_load_configuration.assert_called_once_with(args)
        mock_prepare_metadata.assert_called_once_with(config_data)
        mock_print_metadata.assert_called_once_with(metadata)
        mock_scan_source_files.assert_called_once_with("/path/to/source", ["wav", "flac"])
        mock_print_samples_info.assert_called_once_with(audio_files, metadata)

    @mock.patch("drumgizmo_kits_generator.logger.is_verbose")
    @mock.patch("traceback.format_exc")
    @mock.patch("drumgizmo_kits_generator.cli.parse_arguments")
    @mock.patch("drumgizmo_kits_generator.validators.validate_directories")
    @mock.patch("drumgizmo_kits_generator.logger.error")
    def test_main_unexpected_exception(
        self,
        mock_error,
        mock_validate_directories,
        mock_parse_arguments,
        mock_format_exc,
        mock_is_verbose,
    ):
        """Test that unexpected exceptions are handled correctly in the main function."""
        # Setup mocks
        mock_args = mock.MagicMock()
        mock_parse_arguments.return_value = mock_args

        # Make validate_directories raise an unexpected exception
        mock_validate_directories.side_effect = Exception("Unexpected test error")

        # Mock traceback.format_exc to return a known string
        mock_format_exc.return_value = (
            "Traceback (most recent call last):\n  ...\nException: Unexpected test error"
        )

        # Test with verbose mode off
        mock_is_verbose.return_value = False

        # Call the main function
        main.main()

        # Verify that an error message was printed
        mock_error.assert_called_with("Unexpected error: Unexpected test error")

        # Reset mocks
        mock_error.reset_mock()

        # Test with verbose mode on
        mock_is_verbose.return_value = True

        # Call the main function again
        main.main()

        # Verify that an error message was printed with traceback in verbose mode
        mock_error.assert_any_call("Unexpected error: Unexpected test error")
        mock_error.assert_any_call(mock_format_exc.return_value)


class TestMainWithDependencies:
    """Tests for the main function with dependency checks."""

    def setup_method(self):
        """Initialize test data."""
        self.config_data = {
            "name": "Test Kit",
            "version": "1.0.0",
            "description": "Test description",
            "notes": "Test notes",
            "author": "Test Author",
            "license": "Test License",
            "website": "https://example.com",
            "logo": "logo.png",
            "samplerate": "44100",
            "extra_files": "file1.txt,file2.txt",
            "velocity_levels": "5",
            "midi_note_min": "30",
            "midi_note_max": "90",
            "midi_note_median": "60",
            "extensions": "wav,flac",
            "channels": "Left,Right",
            "main_channels": "Left,Right",
        }

    # pylint: disable=too-many-arguments
    @mock.patch("drumgizmo_kits_generator.utils.check_dependency")
    @mock.patch("drumgizmo_kits_generator.cli.parse_arguments")
    @mock.patch("drumgizmo_kits_generator.validators.validate_directories")
    @mock.patch("drumgizmo_kits_generator.config.load_configuration")
    @mock.patch("drumgizmo_kits_generator.config.transform_configuration")
    @mock.patch("drumgizmo_kits_generator.config.validate_configuration")
    @mock.patch("drumgizmo_kits_generator.config.prepare_metadata")
    @mock.patch("drumgizmo_kits_generator.cli.print_metadata")
    @mock.patch("drumgizmo_kits_generator.utils.scan_source_files")
    @mock.patch("drumgizmo_kits_generator.cli.print_samples_info")
    @mock.patch("drumgizmo_kits_generator.cli.print_midi_mapping")
    @mock.patch("sys.stderr", new_callable=io.StringIO)
    def test_main_sox_dependency_check(
        self,
        mock_stderr,
        mock_print_midi_mapping,  # pylint: disable=unused-argument
        mock_print_samples_info,  # pylint: disable=unused-argument
        mock_scan_source_files,  # pylint: disable=unused-argument
        mock_print_metadata,  # pylint: disable=unused-argument
        mock_prepare_metadata,  # pylint: disable=unused-argument
        mock_validate_config,
        mock_transform_config,
        mock_load_config,
        mock_validate_dirs,
        mock_parse_args,
        mock_check_dependency,
    ):
        """Test that SoX dependency is checked in the main function."""
        # Setup mocks
        mock_args = mock.MagicMock()
        mock_args.dry_run = False
        mock_parse_args.return_value = mock_args

        # Make check_dependency raise a DependencyError
        mock_check_dependency.side_effect = DependencyError("SoX not found")

        # Call the main function
        main.main()

        # Verify that check_dependency was called with "sox"
        mock_check_dependency.assert_called_with(
            "sox", "SoX not found in the system, can not generate samples"
        )

        # Verify that an error message was printed
        stderr_output = mock_stderr.getvalue()
        assert "ERROR: " in stderr_output
        assert "SoX not found" in stderr_output

    @mock.patch("sys.exit")
    @mock.patch("builtins.print")
    @mock.patch("argparse.ArgumentParser.parse_known_args")
    def test_main_app_version(self, mock_parse_known_args, mock_print, mock_exit):
        """Test that --app-version option displays version and exits."""
        # Mock parse_known_args to return a namespace with app_version=True
        args = argparse.Namespace()
        args.app_version = True
        mock_parse_known_args.return_value = (args, [])

        # Call the parse_arguments function directly
        cli.parse_arguments()

        # Verify that version was printed and sys.exit was called
        mock_print.assert_called_with(f"{constants.APP_NAME} v{constants.APP_VERSION}")
        mock_exit.assert_called_with(0)

    # pylint: disable=too-many-arguments
    @mock.patch("drumgizmo_kits_generator.utils.scan_source_files")
    @mock.patch("drumgizmo_kits_generator.main.process_audio_files")
    @mock.patch("drumgizmo_kits_generator.main.generate_xml_files")
    @mock.patch("drumgizmo_kits_generator.main.copy_additional_files")
    @mock.patch("drumgizmo_kits_generator.validators.validate_directories")
    @mock.patch("drumgizmo_kits_generator.config.validate_configuration")
    @mock.patch("drumgizmo_kits_generator.cli.parse_arguments")
    @mock.patch(
        "drumgizmo_kits_generator.main.load_configuration"
    )  # Modifié pour cibler l'import dans main
    @mock.patch("drumgizmo_kits_generator.config.transform_configuration")
    @mock.patch("drumgizmo_kits_generator.config.prepare_metadata")
    @mock.patch("drumgizmo_kits_generator.cli.print_metadata")
    @mock.patch("drumgizmo_kits_generator.cli.print_samples_info")
    @mock.patch("drumgizmo_kits_generator.cli.print_midi_mapping")
    @mock.patch("drumgizmo_kits_generator.utils.prepare_target_directory")
    def test_main_with_valid_args(
        self,
        mock_prepare_target,
        mock_print_midi_mapping,  # pylint: disable=unused-argument
        mock_print_samples,
        mock_print_metadata,
        mock_prepare_metadata,
        mock_transform_config,
        mock_load_config,
        mock_parse_args,
        mock_validate_config,
        mock_validate_dirs,
        mock_copy,
        mock_generate,
        mock_process,
        mock_scan_source,
    ):
        """Test main function with valid arguments."""
        # Setup mocks
        args = argparse.Namespace(
            source="/path/to/source",
            target="/path/to/target",
            config=None,
            verbose=False,
            dry_run=False,
        )
        mock_parse_args.return_value = args

        # Configurer les retours des mocks dans l'ordre d'appel
        config_data = dict(self.config_data)

        # Simuler la transformation de la configuration
        transformed_config = dict(config_data)
        transformed_config["extensions"] = [".wav", ".flac"]

        # Configurer les retours des mocks pour simuler le flux normal
        mock_transform_config.return_value = transformed_config
        mock_validate_config.return_value = transformed_config
        mock_load_config.return_value = (
            transformed_config  # load_configuration retourne la config transformée
        )

        metadata = dict(transformed_config)
        metadata["instruments"] = []
        mock_prepare_metadata.return_value = metadata

        audio_files = ["kick.wav", "snare.wav"]
        mock_scan_source.return_value = audio_files

        mock_process.return_value = {
            "Kick": ["kick1.wav", "kick2.wav"],
            "Snare": ["snare1.wav", "snare2.wav"],
        }

        # Call the function
        main.main()

        # Assertions
        mock_parse_args.assert_called_once()
        mock_validate_dirs.assert_called_once_with("/path/to/source", "/path/to/target", False)

        # Vérifier que load_configuration a été appelé avec les bons arguments
        mock_load_config.assert_called_once_with(args)

        # Vérifier que les fonctions de transformation et validation ont été appelées
        # Note: Ces appels sont effectués à l'intérieur de load_configuration
        # donc nous ne devrions pas les vérifier ici car nous avons mocké load_configuration

        # Vérifier que prepare_metadata a été appelé avec la configuration transformée
        mock_prepare_metadata.assert_called_once_with(transformed_config)

        # Vérifier les autres appels
        mock_print_metadata.assert_called_once_with(metadata)
        mock_print_samples.assert_called_once_with(audio_files, metadata)
        mock_scan_source.assert_called_once_with("/path/to/source", [".wav", ".flac"])
        mock_prepare_target.assert_called_once_with("/path/to/target")
        mock_process.assert_called_once_with(audio_files, "/path/to/target", metadata)
        mock_generate.assert_called_once_with(audio_files, "/path/to/target", metadata)
        mock_copy.assert_called_once_with("/path/to/source", "/path/to/target", metadata)


if __name__ == "__main__":
    pytest.main(["-v", __file__])
