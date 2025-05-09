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
# pylint: disable=R0801 # code duplication
# pylint: disable=unused-variable
"""
SPDX-License-Identifier: MIT
SPDX-PackageName: DrumGizmo kits generator
SPDX-PackageHomePage: https://github.com/e-picas/drumgizmo-kits-generator
SPDX-FileCopyrightText: 2025 Pierre Cassat (Picas)

Tests for the main module of the DrumGizmo kit generator.
"""

import argparse
import io
import os
import shutil
import tempfile
from unittest import mock

import pytest

from drumgizmo_kits_generator import cli, constants, main
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
    ) as mock_set_verbose, mock.patch(
        "drumgizmo_kits_generator.logger.set_raw_output"
    ) as mock_set_raw_output, mock.patch(
        "drumgizmo_kits_generator.logger.print_action_start"
    ) as mock_print_action_start, mock.patch(
        "drumgizmo_kits_generator.logger.print_action_end"
    ) as mock_print_action_end:
        yield {
            "info": mock_info,
            "debug": mock_debug,
            "warning": mock_warning,
            "error": mock_error,
            "section": mock_section,
            "message": mock_message,
            "set_verbose": mock_set_verbose,
            "set_raw_output": mock_set_raw_output,
            "print_action_start": mock_print_action_start,
            "print_action_end": mock_print_action_end,
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
    args.raw_output = False
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

    @mock.patch("drumgizmo_kits_generator.kit_generator.print_metadata")
    @mock.patch("drumgizmo_kits_generator.kit_generator.print_midi_mapping")
    @mock.patch("drumgizmo_kits_generator.cli.parse_arguments")
    @mock.patch("drumgizmo_kits_generator.kit_generator.validate_directories")
    @mock.patch("drumgizmo_kits_generator.config.load_configuration")
    @mock.patch("drumgizmo_kits_generator.kit_generator.scan_source_files")
    @mock.patch("drumgizmo_kits_generator.logger.message")
    @mock.patch("drumgizmo_kits_generator.kit_generator.print_summary")
    def test_main_dry_run(
        self,
        mock_print_summary,
        mock_message,
        mock_scan_source_files,
        mock_load_configuration,
        mock_validate_directories,
        mock_parse_arguments,
        mock_print_midi_mapping,
        mock_print_metadata,
    ):
        """Test main function in dry run mode."""
        # Setup mocks
        args = argparse.Namespace()
        args.source = "/path/to/source"
        args.target = "/path/to/target"
        args.config = constants.DEFAULT_CONFIG_FILE
        args.verbose = False
        args.dry_run = True
        args.raw_output = False
        mock_parse_arguments.return_value = args

        # La configuration est déjà transformée et validée par load_configuration
        config_data = dict(self.config_data)
        config_data.update(
            {
                "source": "/path/to/source",
                "target": "/path/to/target",
                "config": constants.DEFAULT_CONFIG_FILE,
                "verbose": False,
                "raw_output": False,
                "dry_run": True,
                "extensions": ["wav", "flac"],
                "midi_note_min": 0,
                "midi_note_max": 127,
                "midi_note_median": 60,
            }
        )
        mock_load_configuration.return_value = config_data

        audio_files = [
            "/path/to/source/Kick.wav",
            "/path/to/source/Snare.wav",
        ]
        mock_scan_source_files.return_value = audio_files

        # Call the function
        main.main()

        # Check that dry run message was displayed
        # Nouvelle signature : prkit_generator.evaluate_midi_mapping({'audio_files': audio_files, 'config': config_data})
        expected_run_data = {
            "config": config_data,
            "audio_files": audio_files,
            "midi_mapping": mock.ANY,
        }
        mock_print_midi_mapping.assert_called_once_with(expected_run_data)
        mock_message.assert_called_with("\nDry run mode enabled, stopping here")

        # Verify that all mocks were used
        mock_parse_arguments.assert_called_once()
        mock_validate_directories.assert_called_once_with("/path/to/source", "/path/to/target")
        mock_load_configuration.assert_called_once_with(args)

        mock_print_metadata.assert_called_once_with(config_data)
        args, kwargs = mock_scan_source_files.call_args
        assert args[0] == "/path/to/source"
        assert "config" in args[1]
        assert args[1]["config"] == config_data


@mock.patch("drumgizmo_kits_generator.logger.is_verbose")
@mock.patch("traceback.format_exc")
@mock.patch("drumgizmo_kits_generator.cli.parse_arguments")
@mock.patch("drumgizmo_kits_generator.kit_generator.validate_directories")
@mock.patch("drumgizmo_kits_generator.logger.error")
def test_main_unexpected_exception(
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
    mock_error.assert_called_with("Unexpected error: Unexpected test error", mock.ANY)

    # Reset mocks
    mock_error.reset_mock()

    # Test with verbose mode on
    mock_is_verbose.return_value = True

    # Call the main function again
    main.main()

    # Verify that an error message was printed with traceback in verbose mode
    mock_error.assert_any_call("Unexpected error: Unexpected test error", mock.ANY)
    # Le traceback n'est plus loggé séparément, donc on ne vérifie plus mock_format_exc


class TestMainWithDependencies:
    """Tests for the main function with dependency checks."""

    def setup_method(self):
        """Initialize test data."""
        self.config_data = {
            "config": {
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
        }

    # pylint: disable=too-many-arguments
    @mock.patch("drumgizmo_kits_generator.utils.check_dependency")
    @mock.patch("drumgizmo_kits_generator.cli.parse_arguments")
    @mock.patch("drumgizmo_kits_generator.kit_generator.validate_directories")
    @mock.patch("drumgizmo_kits_generator.config.load_configuration")
    @mock.patch("drumgizmo_kits_generator.config.transform_configuration")
    @mock.patch("drumgizmo_kits_generator.config.validate_configuration")
    @mock.patch("drumgizmo_kits_generator.kit_generator.print_metadata")
    @mock.patch("drumgizmo_kits_generator.kit_generator.scan_source_files")
    @mock.patch("drumgizmo_kits_generator.kit_generator.print_midi_mapping")
    @mock.patch("sys.stderr", new_callable=io.StringIO)
    def test_main_sox_dependency_check(
        self,
        mock_stderr,
        mock_print_midi_mapping,
        mock_scan_source_files,
        mock_print_metadata,
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
            "sox",
            "The required 'SoX' software has not been found in the system, can not generate kit!",
        )

        # Verify that an error message was printed
        stderr_output = mock_stderr.getvalue()
        assert "DependencyError: " in stderr_output
        assert "SoX not found" in stderr_output

    @mock.patch("sys.exit")
    @mock.patch("builtins.print")
    @mock.patch("argparse.ArgumentParser.parse_known_args")
    def test_main_app_version(self, mock_parse_known_args, mock_print, mock_exit):
        """Test that --app-version option displays version and exits."""
        # Mock parse_known_args to return a namespace with app_version=True
        args = argparse.Namespace()
        args.app_version = True
        args.raw_output = False
        mock_parse_known_args.return_value = (args, [])

        # Call the parse_arguments function directly
        cli.parse_arguments()

        # Verify that version was printed and sys.exit was called
        mock_print.assert_called_with(f"{constants.APP_NAME} v{constants.APP_VERSION}")
        mock_exit.assert_called_with(0)

    # pylint: disable=too-many-arguments
    @mock.patch("drumgizmo_kits_generator.kit_generator.scan_source_files")
    @mock.patch("drumgizmo_kits_generator.kit_generator.process_audio_files")
    @mock.patch("drumgizmo_kits_generator.kit_generator.generate_xml_files")
    @mock.patch("drumgizmo_kits_generator.kit_generator.copy_additional_files")
    @mock.patch("drumgizmo_kits_generator.kit_generator.validate_directories")
    @mock.patch("drumgizmo_kits_generator.config.validate_configuration")
    @mock.patch("drumgizmo_kits_generator.kit_generator.print_metadata")
    @mock.patch("drumgizmo_kits_generator.kit_generator.print_midi_mapping")
    @mock.patch("drumgizmo_kits_generator.kit_generator.prepare_target_directory")
    @mock.patch("drumgizmo_kits_generator.cli.parse_arguments")
    @mock.patch("drumgizmo_kits_generator.config.load_configuration")
    @mock.patch("drumgizmo_kits_generator.config.transform_configuration")
    def test_main_with_valid_args(
        self,
        mock_transform_config,
        mock_load_config,
        mock_parse_args,
        mock_prepare_target,
        mock_print_midi_mapping,
        mock_print_metadata,
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
            raw_output=False,
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
        mock_validate_dirs.assert_called_once_with("/path/to/source", "/path/to/target")

        # Vérifier que load_configuration a été appelé avec les bons arguments
        mock_load_config.assert_called_once_with(args)

        # Vérifier que les fonctions de transformation et validation ont été appelées
        # Note: Ces appels sont effectués à l'intérieur de load_configuration
        # donc nous ne devrions pas les vérifier ici car nous avons mocké load_configuration

        # Vérifier les autres appels
        mock_print_metadata.assert_called_once_with(transformed_config)
        args, kwargs = mock_scan_source.call_args
        assert args[0] == "/path/to/source"
        assert "config" in args[1]
        assert args[1]["config"] == transformed_config
        # En mode non-dry_run, prepare_target_directory doit être appelé
        mock_prepare_target.assert_called_once_with("/path/to/target")
        mock_process.assert_called_once_with("/path/to/target", mock.ANY)
        mock_generate.assert_called_once_with("/path/to/target", mock.ANY)
        mock_copy.assert_called_once_with("/path/to/source", "/path/to/target", transformed_config)


if __name__ == "__main__":
    pytest.main(["-v", __file__])
