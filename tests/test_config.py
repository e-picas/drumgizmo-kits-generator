#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name
# pylint: disable=protected-access
# pylint: disable=use-implicit-booleaness-not-comparison
"""
Tests for the config module.
"""

import tempfile

import pytest

from drumgizmo_kits_generator import config, constants
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
