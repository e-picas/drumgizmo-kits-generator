#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name
# pylint: disable=unspecified-encoding
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-arguments
# pylint: disable=too-many-locals
"""
Tests for the main module of the DrumGizmo kit generator.
"""

import argparse
import os
import shutil
import tempfile
from unittest import mock

import pytest

from drumgizmo_kits_generator import constants, main


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


class TestParseArguments:
    """Tests for the parse_arguments function."""

    @mock.patch(
        "sys.argv", ["drumgizmo_kits_generator", "-s", "/path/to/source", "-t", "/path/to/target"]
    )
    def test_parse_arguments_minimal(self):
        """Test parse_arguments with minimal required arguments."""
        args = main.parse_arguments()
        assert args.source == "/path/to/source"
        assert args.target == "/path/to/target"
        assert args.config == constants.DEFAULT_CONFIG_FILE
        assert not args.verbose
        assert not args.dry_run

    @mock.patch(
        "sys.argv",
        [
            "drumgizmo_kits_generator",
            "-s",
            "/path/to/source",
            "-t",
            "/path/to/target",
            "-c",
            "/path/to/config.ini",
            "-v",
            "-x",
            "--name",
            "Custom Kit",
            "--version",
            "2.0",
            "--description",
            "Custom description",
            "--notes",
            "Custom notes",
            "--author",
            "Custom Author",
            "--license",
            "MIT",
            "--website",
            "https://custom.com",
            "--logo",
            "custom-logo.png",
            "--samplerate",
            "96000",
            "--extra-files",
            "file1.txt,file2.pdf",
            "--velocity-levels",
            "5",
            "--midi-note-min",
            "10",
            "--midi-note-max",
            "100",
            "--midi-note-median",
            "55",
            "--extensions",
            "wav,aiff",
            "--channels",
            "Ch1,Ch2",
            "--main-channels",
            "Ch1",
        ],
    )
    def test_parse_arguments_full(self):
        """Test parse_arguments with all possible arguments."""
        args = main.parse_arguments()
        assert args.source == "/path/to/source"
        assert args.target == "/path/to/target"
        assert args.config == "/path/to/config.ini"
        assert args.verbose
        assert args.dry_run
        assert args.name == "Custom Kit"
        assert args.version == "2.0"
        assert args.description == "Custom description"
        assert args.notes == "Custom notes"
        assert args.author == "Custom Author"
        assert args.license == "MIT"
        assert args.website == "https://custom.com"
        assert args.logo == "custom-logo.png"
        assert args.samplerate == "96000"
        assert args.extra_files == "file1.txt,file2.pdf"
        assert args.velocity_levels == "5"
        assert args.midi_note_min == "10"
        assert args.midi_note_max == "100"
        assert args.midi_note_median == "55"
        assert args.extensions == "wav,aiff"
        assert args.channels == "Ch1,Ch2"
        assert args.main_channels == "Ch1"


class TestLoadConfiguration:
    """Tests for the load_configuration function."""

    def test_load_configuration_defaults(self):
        """Test loading configuration with default values."""
        args = argparse.Namespace(
            source="/source",
            target="/target",
            verbose=False,
            dry_run=False,
            config=constants.DEFAULT_CONFIG_FILE,
            name=None,
            version=None,
            description=None,
            notes=None,
            author=None,
            license=None,
            website=None,
            logo=None,
            samplerate=None,
            extra_files=None,
            velocity_levels=None,
            midi_note_min=None,
            midi_note_max=None,
            midi_note_median=None,
            extensions=None,
            channels=None,
            main_channels=None,
        )

        with mock.patch("os.path.isfile", return_value=False):
            config_data = main.load_configuration(args)

        assert config_data["name"] == constants.DEFAULT_NAME
        assert config_data["version"] == constants.DEFAULT_VERSION
        assert config_data["license"] == constants.DEFAULT_LICENSE
        assert config_data["samplerate"] == constants.DEFAULT_SAMPLERATE
        assert config_data["extensions"] == constants.DEFAULT_EXTENSIONS
        assert config_data["channels"] == constants.DEFAULT_CHANNELS
        assert config_data["main_channels"] == constants.DEFAULT_MAIN_CHANNELS
        assert config_data["velocity_levels"] == constants.DEFAULT_VELOCITY_LEVELS
        assert config_data["midi_note_min"] == constants.DEFAULT_MIDI_NOTE_MIN
        assert config_data["midi_note_max"] == constants.DEFAULT_MIDI_NOTE_MAX
        assert config_data["midi_note_median"] == constants.DEFAULT_MIDI_NOTE_MEDIAN

    def test_load_configuration_from_file(self, temp_config_file):
        """Test loading configuration from a file."""
        args = argparse.Namespace(
            source="/source",
            target="/target",
            verbose=False,
            dry_run=False,
            config=temp_config_file,
            name=None,
            version=None,
            description=None,
            notes=None,
            author=None,
            license=None,
            website=None,
            logo=None,
            samplerate=None,
            extra_files=None,
            velocity_levels=None,
            midi_note_min=None,
            midi_note_max=None,
            midi_note_median=None,
            extensions=None,
            channels=None,
            main_channels=None,
        )

        config_data = main.load_configuration(args)

        assert config_data["name"] == "Test Kit"
        assert config_data["version"] == "1.0.0"
        assert config_data["description"] == "Test description"
        assert config_data["notes"] == "Test notes"
        assert config_data["author"] == "Test Author"
        assert config_data["license"] == "Test License"
        assert config_data["website"] == "https://example.com"
        assert config_data["logo"] == "logo.png"
        assert config_data["samplerate"] == "44100"
        assert config_data["extra_files"] == "file1.txt,file2.txt"
        assert config_data["velocity_levels"] == "5"
        assert config_data["midi_note_min"] == "30"
        assert config_data["midi_note_max"] == "90"
        assert config_data["midi_note_median"] == "60"
        assert config_data["extensions"] == "wav,flac"
        assert config_data["channels"] == "Left,Right"
        assert config_data["main_channels"] == "Left,Right"

    def test_load_configuration_from_source_dir(self, temp_config_file):
        """Test loading configuration from source directory."""
        # Create a temporary directory structure
        with tempfile.TemporaryDirectory() as temp_dir:
            # Copy the config file to the source directory
            source_config = os.path.join(temp_dir, constants.DEFAULT_CONFIG_FILE)
            shutil.copy(temp_config_file, source_config)

            args = argparse.Namespace(
                source=temp_dir,
                target="/target",
                verbose=False,
                dry_run=False,
                config=constants.DEFAULT_CONFIG_FILE,
                name=None,
                version=None,
                description=None,
                notes=None,
                author=None,
                license=None,
                website=None,
                logo=None,
                samplerate=None,
                extra_files=None,
                velocity_levels=None,
                midi_note_min=None,
                midi_note_max=None,
                midi_note_median=None,
                extensions=None,
                channels=None,
                main_channels=None,
            )

            config_data = main.load_configuration(args)

            assert config_data["name"] == "Test Kit"
            assert config_data["version"] == "1.0.0"
            assert config_data["description"] == "Test description"

    def test_load_configuration_nonexistent_file(self):
        """Test loading configuration with a nonexistent file."""
        args = argparse.Namespace(
            source="/source",
            target="/target",
            verbose=False,
            dry_run=False,
            config="nonexistent.ini",  # Non-default config file that doesn't exist
            name=None,
            version=None,
            description=None,
            notes=None,
            author=None,
            license=None,
            website=None,
            logo=None,
            samplerate=None,
            extra_files=None,
            velocity_levels=None,
            midi_note_min=None,
            midi_note_max=None,
            midi_note_median=None,
            extensions=None,
            channels=None,
            main_channels=None,
        )

        with mock.patch("os.path.isfile", return_value=False), mock.patch(
            "drumgizmo_kits_generator.logger.warning"
        ) as mock_warning:
            config_data = main.load_configuration(args)

            # Verify that a warning was logged
            mock_warning.assert_called_once_with("Configuration file not found: nonexistent.ini")

        # Should still have default values
        assert config_data["name"] == constants.DEFAULT_NAME
        assert config_data["version"] == constants.DEFAULT_VERSION


class TestTransformConfiguration:
    """Tests for the transform_configuration function."""

    @mock.patch("drumgizmo_kits_generator.transformers.transform_velocity_levels")
    @mock.patch("drumgizmo_kits_generator.transformers.transform_midi_note_min")
    @mock.patch("drumgizmo_kits_generator.transformers.transform_midi_note_max")
    @mock.patch("drumgizmo_kits_generator.transformers.transform_midi_note_median")
    @mock.patch("drumgizmo_kits_generator.transformers.transform_samplerate")
    @mock.patch("drumgizmo_kits_generator.transformers.transform_extensions")
    @mock.patch("drumgizmo_kits_generator.transformers.transform_channels")
    @mock.patch("drumgizmo_kits_generator.transformers.transform_main_channels")
    @mock.patch("drumgizmo_kits_generator.transformers.transform_extra_files")
    def test_transform_configuration(
        self,
        mock_extra_files,
        mock_main_channels,
        mock_channels,
        mock_extensions,
        mock_samplerate,
        mock_median,
        mock_max,
        mock_min,
        mock_velocity,
    ):
        """Test transform_configuration calls all transformer functions."""
        # Setup mocks to return transformed values
        mock_velocity.return_value = 4
        mock_min.return_value = 0
        mock_max.return_value = 127
        mock_median.return_value = 60
        mock_samplerate.return_value = "48000"
        mock_extensions.return_value = ["wav", "flac"]
        mock_channels.return_value = ["Left", "Right"]
        mock_main_channels.return_value = ["Left"]
        mock_extra_files.return_value = ["file1.txt"]

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
            "samplerate": "44100",
            "extra_files": "file1.txt",
            "velocity_levels": "4",
            "midi_note_min": "0",
            "midi_note_max": "127",
            "midi_note_median": "60",
            "extensions": "wav,flac",
            "channels": "Left,Right",
            "main_channels": "Left",
        }

        # Call the function
        result = main.transform_configuration(config_data)

        # Check that all transformer functions were called
        mock_velocity.assert_called_once_with(config_data["velocity_levels"])
        mock_min.assert_called_once_with(config_data["midi_note_min"])
        mock_max.assert_called_once_with(config_data["midi_note_max"])
        mock_median.assert_called_once_with(config_data["midi_note_median"])
        mock_samplerate.assert_called_once_with(config_data["samplerate"])
        mock_extensions.assert_called_once_with(config_data["extensions"])
        mock_channels.assert_called_once_with(config_data["channels"])
        mock_main_channels.assert_called_once_with(config_data["main_channels"])
        mock_extra_files.assert_called_once_with(config_data["extra_files"])

        # Check that transformed values are in the result
        assert result["velocity_levels"] == 4
        assert result["midi_note_min"] == 0
        assert result["midi_note_max"] == 127
        assert result["midi_note_median"] == 60
        assert result["samplerate"] == "48000"
        assert result["extensions"] == ["wav", "flac"]
        assert result["channels"] == ["Left", "Right"]
        assert result["main_channels"] == ["Left"]
        assert result["extra_files"] == ["file1.txt"]


class TestValidateConfiguration:
    """Tests for the validate_configuration function."""

    @mock.patch("drumgizmo_kits_generator.validators.validate_midi_note_min")
    @mock.patch("drumgizmo_kits_generator.validators.validate_midi_note_max")
    @mock.patch("drumgizmo_kits_generator.validators.validate_midi_note_median")
    @mock.patch("drumgizmo_kits_generator.validators.validate_channels")
    @mock.patch("drumgizmo_kits_generator.validators.validate_main_channels")
    def test_validate_configuration(
        self,
        mock_validate_main_channels,
        mock_validate_channels,
        mock_validate_median,
        mock_validate_max,
        mock_validate_min,
    ):
        """Test validate_configuration calls validator functions."""
        # Create config data
        config_data = {
            "midi_note_min": 0,
            "midi_note_max": 127,
            "midi_note_median": 60,
            "channels": ["Left", "Right"],
            "main_channels": ["Left"],
        }

        # Call the function
        main.validate_configuration(config_data)

        # Check that validator functions were called
        mock_validate_min.assert_called_once()
        mock_validate_max.assert_called_once()
        mock_validate_median.assert_called_once()
        mock_validate_channels.assert_called_once()
        mock_validate_main_channels.assert_called_once()


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

        # Call the function
        metadata = main.prepare_metadata(config_data)

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

        metadata = main.prepare_metadata(config_data)

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

        metadata = main.prepare_metadata(config_data)

        assert metadata["name"] == "Test Kit"
        assert metadata["velocity_levels"] == 5
        assert metadata["midi_note_min"] == 30
        assert metadata["midi_note_max"] == 90
        assert metadata["midi_note_median"] == 60
        assert metadata["samplerate"] == 44100


class TestPrintFunctions:
    """Tests for the print_* functions."""

    def test_print_metadata(self, mock_logger):
        """Test print_metadata function."""
        metadata = {
            "name": "Test Kit",
            "version": "1.0.0",
            "description": "Test description",
            "notes": "Test notes",
            "author": "Test Author",
            "license": "Test License",
            "website": "https://example.com",
            "logo": "logo.png",
            "samplerate": "44100",
            "extra_files": ["file1.txt", "file2.txt"],
            "velocity_levels": 5,
            "midi_note_min": 30,
            "midi_note_max": 90,
            "midi_note_median": 60,
            "extensions": ["wav", "flac"],
            "channels": ["Left", "Right"],
            "main_channels": ["Left", "Right"],
        }

        main.print_metadata(metadata)

        # Verify that section and info were called with appropriate arguments
        mock_logger["section"].assert_called_with("Metadata")
        assert mock_logger["info"].call_count >= 10  # Should call info for each metadata item

    def test_print_samples_info(self, mock_logger):
        """Test print_samples_info function."""
        audio_files = [
            "/path/to/kick.wav",
            "/path/to/snare.wav",
            "/path/to/hihat.wav",
        ]

        metadata = {
            "midi_note_min": 30,
            "midi_note_max": 90,
            "midi_note_median": 60,
        }

        main.print_samples_info(audio_files, metadata)

        # Verify that section and info were called with appropriate arguments
        mock_logger["section"].assert_called_with("Source Audio Samples")
        assert mock_logger["info"].call_count >= 4  # Should call info for count and each sample


class TestMain:
    """Tests for the main module."""

    # Configuration de données partagée par tous les tests
    config_data = {
        "name": "Test Kit",
        "version": "1.0",
        "description": "Test description",
        "notes": "Test notes",
        "author": "Test Author",
        "license": "CC-BY-SA",
        "website": "https://example.com",
        "samplerate": "48000",
        "velocity_levels": 3,
        "midi_note_min": 0,
        "midi_note_max": 127,
        "midi_note_median": 60,
        "extensions": ["wav", "flac", "ogg"],
        "channels": ["Left", "Right", "Overhead"],
        "main_channels": ["Left", "Right"],
    }

    @mock.patch("drumgizmo_kits_generator.main.parse_arguments")
    @mock.patch("drumgizmo_kits_generator.utils.validate_directories")
    @mock.patch("drumgizmo_kits_generator.main.load_configuration")
    @mock.patch("drumgizmo_kits_generator.main.transform_configuration")
    @mock.patch("drumgizmo_kits_generator.main.validate_configuration")
    @mock.patch("drumgizmo_kits_generator.main.prepare_metadata")
    @mock.patch("drumgizmo_kits_generator.main.print_metadata")
    @mock.patch("drumgizmo_kits_generator.utils.scan_source_files")
    @mock.patch("drumgizmo_kits_generator.main.print_samples_info")
    @mock.patch("drumgizmo_kits_generator.utils.prepare_target_directory")
    @mock.patch("drumgizmo_kits_generator.main.process_audio_files")
    @mock.patch("drumgizmo_kits_generator.main.generate_xml_files")
    @mock.patch("drumgizmo_kits_generator.main.copy_additional_files")
    def test_main_normal_flow(
        self,
        mock_copy,
        mock_generate_xml,
        mock_process_audio,
        mock_prepare_target,
        mock_print_samples,
        mock_scan_source,
        mock_print_metadata,
        mock_prepare_metadata,
        mock_validate_config,
        mock_transform_config,
        mock_load_config,
        mock_validate_dirs,
        mock_parse_args,
        mock_logger,
    ):
        """Test main function normal execution flow."""
        # Setup mocks
        args = argparse.Namespace()
        args.source = "/path/to/source"
        args.target = "/path/to/target"
        args.config = constants.DEFAULT_CONFIG_FILE
        args.verbose = True
        args.dry_run = False
        mock_parse_args.return_value = args

        config_data = self.config_data
        mock_load_config.return_value = config_data

        transformed_config = {"name": "Test Kit", "extensions": ["wav"]}
        mock_transform_config.return_value = transformed_config

        metadata = {"name": "Test Kit", "extensions": ["wav"], "instruments": []}
        mock_prepare_metadata.return_value = metadata

        audio_files = ["/path/to/source/kick.wav", "/path/to/source/snare.wav"]
        mock_scan_source.return_value = audio_files

        processed_files = [
            "/path/to/target/Kick/samples/1-Kick.wav",
            "/path/to/target/Snare/samples/1-Snare.wav",
        ]
        mock_process_audio.return_value = processed_files

        # Call the function
        main.main()

        # Check that all expected functions were called in order
        mock_parse_args.assert_called_once()
        mock_logger["set_verbose"].assert_called_once_with(True)
        mock_validate_dirs.assert_called_once_with(args.source, args.target, args.config)
        mock_load_config.assert_called_once_with(args)
        mock_transform_config.assert_called_once_with(config_data)
        mock_validate_config.assert_called_once_with(transformed_config)
        mock_prepare_metadata.assert_called_once_with(transformed_config)
        mock_print_metadata.assert_called_once_with(metadata)
        mock_scan_source.assert_called_once_with(args.source, metadata["extensions"])
        mock_print_samples.assert_called_once_with(audio_files, metadata)
        mock_prepare_target.assert_called_once_with(args.target)
        mock_process_audio.assert_called_once_with(audio_files, args.target, metadata)
        mock_generate_xml.assert_called_once_with(processed_files, args.target, metadata)
        mock_copy.assert_called_once_with(args.source, args.target, metadata)

    @mock.patch("drumgizmo_kits_generator.main.parse_arguments")
    @mock.patch("drumgizmo_kits_generator.utils.validate_directories")
    @mock.patch("drumgizmo_kits_generator.main.load_configuration")
    @mock.patch("drumgizmo_kits_generator.main.transform_configuration")
    @mock.patch("drumgizmo_kits_generator.main.validate_configuration")
    @mock.patch("drumgizmo_kits_generator.main.prepare_metadata")
    @mock.patch("drumgizmo_kits_generator.main.print_metadata")
    @mock.patch("drumgizmo_kits_generator.utils.scan_source_files")
    @mock.patch("drumgizmo_kits_generator.main.print_samples_info")
    def test_main_dry_run(
        self,
        mock_print_samples,
        mock_scan_source,
        mock_print_metadata,
        mock_prepare_metadata,
        mock_validate_config,
        mock_transform_config,
        mock_load_config,
        mock_validate_dirs,
        mock_parse_args,
        mock_logger,
    ):
        """Test main function in dry run mode."""
        # Setup mocks
        args = argparse.Namespace()
        args.source = "/path/to/source"
        args.target = "/path/to/target"
        args.config = constants.DEFAULT_CONFIG_FILE
        args.verbose = False
        args.dry_run = True
        mock_parse_args.return_value = args

        config_data = self.config_data
        mock_load_config.return_value = config_data

        transformed_config = {"name": "Test Kit", "extensions": ["wav"]}
        mock_transform_config.return_value = transformed_config

        metadata = {"name": "Test Kit", "extensions": ["wav"], "instruments": []}
        mock_prepare_metadata.return_value = metadata

        audio_files = ["/path/to/source/kick.wav", "/path/to/source/snare.wav"]
        mock_scan_source.return_value = audio_files

        # Call the function
        main.main()

        # Check that dry run message was displayed
        mock_logger["message"].assert_called_with("Dry run mode enabled, stopping here")

        # Check that file processing functions were not called
        assert not hasattr(mock_logger, "prepare_target_directory")
        assert not hasattr(mock_logger, "process_audio_files")
        assert not hasattr(mock_logger, "generate_xml_files")
        assert not hasattr(mock_logger, "copy_additional_files")

        # Verify that all mocks were used
        mock_parse_args.assert_called_once()
        mock_logger["set_verbose"].assert_called_once_with(False)
        mock_validate_dirs.assert_called_once()
        mock_load_config.assert_called_once()
        mock_transform_config.assert_called_once()
        mock_validate_config.assert_called_once()
        mock_prepare_metadata.assert_called_once()
        mock_print_metadata.assert_called_once()
        mock_scan_source.assert_called_once()
        mock_print_samples.assert_called_once()

    @mock.patch("drumgizmo_kits_generator.utils.scan_source_files")
    @mock.patch("drumgizmo_kits_generator.main.process_audio_files")
    @mock.patch("drumgizmo_kits_generator.main.generate_xml_files")
    @mock.patch("drumgizmo_kits_generator.main.copy_additional_files")
    @mock.patch("drumgizmo_kits_generator.utils.validate_directories")
    @mock.patch("drumgizmo_kits_generator.main.validate_configuration")
    @mock.patch("drumgizmo_kits_generator.main.parse_arguments")
    @mock.patch("drumgizmo_kits_generator.main.load_configuration")
    @mock.patch("drumgizmo_kits_generator.main.transform_configuration")
    @mock.patch("drumgizmo_kits_generator.main.prepare_metadata")
    @mock.patch("drumgizmo_kits_generator.main.print_metadata")
    @mock.patch("drumgizmo_kits_generator.main.print_samples_info")
    @mock.patch("drumgizmo_kits_generator.utils.prepare_target_directory")
    def test_main_with_valid_args(
        self,
        mock_prepare_target,
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

        config_data = self.config_data
        mock_load_config.return_value = config_data

        transformed_config = dict(config_data)
        transformed_config["extensions"] = [".wav", ".flac"]
        mock_transform_config.return_value = transformed_config

        mock_validate_config.return_value = transformed_config

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
        mock_validate_dirs.assert_called_once()
        mock_load_config.assert_called_once()
        mock_transform_config.assert_called_once()
        mock_validate_config.assert_called_once()
        mock_prepare_metadata.assert_called_once()
        mock_print_metadata.assert_called_once()
        mock_print_samples.assert_called_once()
        mock_scan_source.assert_called_once()
        mock_prepare_target.assert_called_once()
        mock_process.assert_called_once()
        mock_generate.assert_called_once()
        mock_copy.assert_called_once()


if __name__ == "__main__":
    pytest.main(["-v", __file__])
