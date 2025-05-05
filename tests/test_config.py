#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name
# pylint: disable=protected-access
# pylint: disable=use-implicit-booleaness-not-comparison
# pylint: disable=too-many-arguments
# pylint: disable=too-few-public-methods
"""
Tests for the config module.
"""

import argparse
import os
import shutil
import tempfile
from unittest import mock

import pytest

from drumgizmo_kits_generator import config, constants, main
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


def test_process_channel_list_with_custom_value():
    """Test processing a channel list with a custom value."""
    custom_channels = "Channel1,Channel2,Channel3"
    result = config._process_channel_list(custom_channels, constants.DEFAULT_CHANNELS, "channels")

    # Check that the custom value is returned
    assert result == custom_channels


def test_process_channel_list_with_empty_value():
    """Test processing a channel list with an empty value."""
    result = config._process_channel_list(None, constants.DEFAULT_CHANNELS, "channels")

    # Check that the default value is returned
    assert result == constants.DEFAULT_CHANNELS


def test_process_channels():
    """Test processing channels and main channels."""
    # Test with custom values
    config_data = {"channels": "Channel1,Channel2,Channel3", "main_channels": "Channel1,Channel2"}
    result = config.process_channels(config_data)

    # Check that the values are unchanged
    assert result["channels"] == "Channel1,Channel2,Channel3"
    assert result["main_channels"] == "Channel1,Channel2"

    # Test with empty values
    config_data = {}
    result = config.process_channels(config_data)

    # Check that the default values are used
    assert result["channels"] == constants.DEFAULT_CHANNELS
    assert result["main_channels"] == constants.DEFAULT_MAIN_CHANNELS


def test_get_config_value():
    """Test getting a configuration value with fallback."""
    config_data = {"key1": "value1", "key2": "value2"}

    # Test getting an existing key
    assert config.get_config_value(config_data, "key1") == "value1"

    # Test getting a nonexistent key with default
    assert config.get_config_value(config_data, "key3", "default") == "default"

    # Test getting a nonexistent key without default
    assert config.get_config_value(config_data, "key3") is None


def test_merge_configs():
    """Test merging multiple configuration dictionaries."""
    config1 = {"key1": "value1", "key2": "value2"}
    config2 = {"key2": "new_value2", "key3": "value3"}
    config3 = {"key3": None, "key4": "value4"}

    # Test merging two configs
    result = config.merge_configs(config1, config2)
    assert result == {"key1": "value1", "key2": "new_value2", "key3": "value3"}

    # Test merging three configs, with None values
    result = config.merge_configs(config1, config2, config3)
    assert result == {"key1": "value1", "key2": "new_value2", "key3": "value3", "key4": "value4"}

    # Test merging empty configs
    result = config.merge_configs({}, {})
    assert result == {}


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
