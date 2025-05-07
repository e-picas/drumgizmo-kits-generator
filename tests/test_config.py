#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name
# pylint: disable=protected-access
# pylint: disable=use-implicit-booleaness-not-comparison
# pylint: disable=too-many-arguments
# pylint: disable=too-few-public-methods
# pylint: disable=wrong-import-position
"""
SPDX-License-Identifier: MIT
SPDX-PackageName: DrumGizmo kits generator
SPDX-PackageHomePage: https://github.com/e-picas/drumgizmo-kits-generator
SPDX-FileCopyrightText: 2025 Pierre Cassat (Picas)

Tests for the config module.
"""

import argparse
import os
import shutil
import sys
import tempfile
from unittest import mock

import pytest

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from drumgizmo_kits_generator import config, constants
from drumgizmo_kits_generator.config import transform_configuration, validate_configuration

# Importer les constantes depuis le module constants
DEFAULT_EXTENSIONS = constants.DEFAULT_EXTENSIONS
DEFAULT_VELOCITY_LEVELS = constants.DEFAULT_VELOCITY_LEVELS
DEFAULT_MIDI_NOTE_MIN = constants.DEFAULT_MIDI_NOTE_MIN
DEFAULT_MIDI_NOTE_MAX = constants.DEFAULT_MIDI_NOTE_MAX
DEFAULT_MIDI_NOTE_MEDIAN = constants.DEFAULT_MIDI_NOTE_MEDIAN
DEFAULT_NAME = constants.DEFAULT_NAME
DEFAULT_VERSION = constants.DEFAULT_VERSION
DEFAULT_LICENSE = constants.DEFAULT_LICENSE
DEFAULT_SAMPLERATE = constants.DEFAULT_SAMPLERATE
DEFAULT_CHANNELS = constants.DEFAULT_CHANNELS
DEFAULT_MAIN_CHANNELS = constants.DEFAULT_MAIN_CHANNELS
from drumgizmo_kits_generator.exceptions import ConfigurationError


@pytest.fixture
def sample_config_file():
    """Create a sample configuration file for testing."""
    with tempfile.NamedTemporaryFile(suffix=".ini", delete=False) as f:
        f.write(
            b"""[drumgizmo_kit_generator]
name = Test Kit
version = 1.0
samplerate = 44100
velocity_levels = 3
channels = Kick,Snare,HiHat
main_channels = Kick,Snare
"""
        )
        return f.name


@pytest.fixture
def empty_config_file():
    """Create an empty configuration file for testing."""
    with tempfile.NamedTemporaryFile(suffix=".ini", delete=False) as f:
        f.write(
            b"""[drumgizmo_kit_generator]
"""
        )
        return f.name


@pytest.fixture
def invalid_config_file():
    """Create an invalid configuration file for testing."""
    with tempfile.NamedTemporaryFile(suffix=".ini", delete=False) as f:
        f.write(
            b"""[drumgizmo_kit_generator]
invalid content
"""
        )
        return f.name


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


def test_load_config_file(sample_config_file):
    """Test loading a valid configuration file."""
    config_data = config.load_config_file(sample_config_file)

    # Check that all values were loaded correctly
    assert config_data["name"] == "Test Kit"
    assert config_data["version"] == "1.0"
    assert config_data["samplerate"] == "44100"
    assert config_data["velocity_levels"] == "3"
    assert config_data["channels"] == "Kick,Snare,HiHat"
    assert config_data["main_channels"] == "Kick,Snare"


def test_load_empty_config_file(empty_config_file):
    """Test loading an empty configuration file."""
    config_data = config.load_config_file(empty_config_file)

    # Check that default values are returned for an empty config file
    assert "name" in config_data
    assert "version" in config_data
    assert "channels" in config_data
    assert "main_channels" in config_data


def test_load_nonexistent_config_file():
    """Test loading a nonexistent configuration file."""
    # Should raise ConfigurationError
    with pytest.raises(ConfigurationError) as excinfo:
        config.load_config_file("nonexistent_file.ini")

    # Check the error message
    assert "Configuration file not found" in str(excinfo.value)


def test_load_invalid_config_file(invalid_config_file):
    """Test loading an invalid configuration file."""
    # Should raise ConfigurationError
    with pytest.raises(ConfigurationError) as excinfo:
        config.load_config_file(invalid_config_file)

    # Check the error message
    assert "Error parsing configuration file" in str(excinfo.value)


# def test_process_channel_list_with_custom_value():
#     """Test processing a channel list with a custom value."""
#     custom_channels = "Channel1,Channel2,Channel3"
#     result = config._process_channel_list(custom_channels, constants.DEFAULT_CHANNELS, "channels")

#     # Check that the custom value is returned
#     assert result == custom_channels


# def test_process_channel_list_with_empty_value():
#     """Test processing a channel list with an empty value."""
#     result = config._process_channel_list(None, constants.DEFAULT_CHANNELS, "channels")

#     # Check that the default value is returned
#     assert result == constants.DEFAULT_CHANNELS


# def test_process_channels():
#     """Test processing channels and main channels."""
#     # Test with custom values
#     config_data = {"channels": "Channel1,Channel2,Channel3", "main_channels": "Channel1,Channel2"}
#     result = config.process_channels(config_data)

#     # Check that the values are unchanged
#     assert result["channels"] == "Channel1,Channel2,Channel3"
#     assert result["main_channels"] == "Channel1,Channel2"

#     # Test with empty values
#     config_data = {}
#     result = config.process_channels(config_data)

#     # Check that the default values are used
#     assert result["channels"] == constants.DEFAULT_CHANNELS
#     assert result["main_channels"] == constants.DEFAULT_MAIN_CHANNELS


class TestLoadConfiguration:
    """Tests for the load_configuration function."""

    @mock.patch("drumgizmo_kits_generator.config.transform_configuration")
    @mock.patch("drumgizmo_kits_generator.config.validate_configuration")
    def test_load_configuration_defaults(
        self, mock_validate_configuration, mock_transform_configuration
    ):
        """Test loading configuration with default values."""
        args = argparse.Namespace(
            source="/source",
            target="/target",
            verbose=False,
            raw_output=False,
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

        # Configuration attendue après transformation
        expected_config = {
            "source": "/source",
            "target": "/target",
            "verbose": False,
            "raw_output": False,
            "dry_run": False,
            "config": constants.DEFAULT_CONFIG_FILE,
            "name": constants.DEFAULT_NAME,
            "version": constants.DEFAULT_VERSION,
            "license": constants.DEFAULT_LICENSE,
            "samplerate": constants.DEFAULT_SAMPLERATE,
            "extensions": constants.DEFAULT_EXTENSIONS,
            "channels": constants.DEFAULT_CHANNELS,
            "main_channels": constants.DEFAULT_MAIN_CHANNELS,
            "velocity_levels": constants.DEFAULT_VELOCITY_LEVELS,
            "midi_note_min": constants.DEFAULT_MIDI_NOTE_MIN,
            "midi_note_max": constants.DEFAULT_MIDI_NOTE_MAX,
            "midi_note_median": constants.DEFAULT_MIDI_NOTE_MEDIAN,
            "description": "",
            "notes": "",
            "author": "",
            "website": "",
            "logo": "",
            "extra_files": [],
        }

        # Configurer les mocks
        mock_transform_configuration.return_value = expected_config
        mock_validate_configuration.return_value = expected_config

        with mock.patch("os.path.isfile", return_value=False):
            config_data = config.load_configuration(args)

        # Vérifier que les fonctions ont été appelées
        mock_transform_configuration.assert_called_once()
        mock_validate_configuration.assert_called_once_with(expected_config)

        # Vérifier les valeurs de configuration
        for key, expected_value in expected_config.items():
            assert config_data[key] == expected_value, f"Mismatch for {key}"

    @mock.patch("drumgizmo_kits_generator.config.transform_configuration")
    @mock.patch("drumgizmo_kits_generator.config.validate_configuration")
    def test_load_configuration_from_file(
        self, mock_validate_configuration, mock_transform_configuration, temp_config_file
    ):
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

        # Configuration attendue après transformation
        expected_config = {
            "source": "/source",
            "target": "/target",
            "verbose": False,
            "dry_run": False,
            "config": temp_config_file,
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

        # Configurer les mocks
        mock_transform_configuration.return_value = expected_config
        mock_validate_configuration.return_value = expected_config

        config_data = config.load_configuration(args)
        # Vérifier que les fonctions ont été appelées
        mock_transform_configuration.assert_called_once()
        mock_validate_configuration.assert_called_once_with(expected_config)

        # Vérifier les valeurs de configuration
        for key, expected_value in expected_config.items():
            assert config_data[key] == expected_value, f"Mismatch for {key}"

    @mock.patch("drumgizmo_kits_generator.config.transform_configuration")
    @mock.patch("drumgizmo_kits_generator.config.validate_configuration")
    def test_load_configuration_from_source_dir(
        self, mock_validate_configuration, mock_transform_configuration, temp_config_file
    ):
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

            # Configuration attendue après transformation
            expected_config = {
                "source": temp_dir,
                "target": "/target",
                "verbose": False,
                "dry_run": False,
                "config": constants.DEFAULT_CONFIG_FILE,
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

            # Configurer les mocks
            mock_transform_configuration.return_value = expected_config
            mock_validate_configuration.return_value = expected_config

            config_data = config.load_configuration(args)

            # Vérifier que les fonctions ont été appelées
            mock_transform_configuration.assert_called_once()
            mock_validate_configuration.assert_called_once_with(expected_config)

            # Vérifier les valeurs de configuration
            assert config_data["name"] == "Test Kit"
            assert config_data["version"] == "1.0.0"
            assert config_data["description"] == "Test description"

    @mock.patch("drumgizmo_kits_generator.config.transform_configuration")
    @mock.patch("drumgizmo_kits_generator.config.validate_configuration")
    def test_load_configuration_nonexistent_file(
        self, mock_validate_configuration, mock_transform_configuration
    ):
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

        # Configuration attendue après transformation
        expected_config = {
            "source": "/source",
            "target": "/target",
            "verbose": False,
            "dry_run": False,
            "config": "nonexistent.ini",
            "name": constants.DEFAULT_NAME,
            "version": constants.DEFAULT_VERSION,
            "license": constants.DEFAULT_LICENSE,
            "samplerate": constants.DEFAULT_SAMPLERATE,
            "extensions": constants.DEFAULT_EXTENSIONS,
            "channels": constants.DEFAULT_CHANNELS,
            "main_channels": constants.DEFAULT_MAIN_CHANNELS,
            "velocity_levels": constants.DEFAULT_VELOCITY_LEVELS,
            "midi_note_min": constants.DEFAULT_MIDI_NOTE_MIN,
            "midi_note_max": constants.DEFAULT_MIDI_NOTE_MAX,
            "midi_note_median": constants.DEFAULT_MIDI_NOTE_MEDIAN,
            "description": "",
            "notes": "",
            "author": "",
            "website": "",
            "logo": "",
            "extra_files": [],
        }

        # Configurer les mocks
        mock_transform_configuration.return_value = expected_config
        mock_validate_configuration.return_value = expected_config

        with mock.patch("os.path.isfile", return_value=False), mock.patch(
            "drumgizmo_kits_generator.logger.warning"
        ) as mock_warning:
            config_data = config.load_configuration(args)

            # Vérifier qu'un avertissement a été enregistré
            mock_warning.assert_called_once_with("Configuration file not found: nonexistent.ini")

        # Vérifier que les fonctions ont été appelées
        mock_transform_configuration.assert_called_once()
        mock_validate_configuration.assert_called_once_with(expected_config)

        # Vérifier les valeurs de configuration par défaut
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
        result = transform_configuration(config_data)

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
        validate_configuration(config_data)

        # Check that validator functions were called
        mock_validate_min.assert_called_once()
        mock_validate_max.assert_called_once()
        mock_validate_median.assert_called_once()
        mock_validate_channels.assert_called_once()
        mock_validate_main_channels.assert_called_once()
