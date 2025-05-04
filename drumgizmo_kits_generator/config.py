#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration module for DrumGizmo kit generator.
Contains functions for reading and processing configuration files and command line options.
"""

import configparser
import os
from typing import Any, Dict, Optional

from drumgizmo_kits_generator import constants, logger
from drumgizmo_kits_generator.exceptions import ConfigurationError


def _strip_quotes(value: str) -> str:
    """
    Strip quotes from a string value.

    Args:
        value: The string value to strip quotes from

    Returns:
        str: The value without quotes
    """
    if (
        isinstance(value, str)
        and (value.startswith('"') and value.endswith('"'))
        or (value.startswith("'") and value.endswith("'"))
    ):
        return value[1:-1]
    return value


def load_config_file(config_file_path: str) -> Dict[str, Any]:
    """
    Load configuration from an INI file.

    Args:
        config_file_path: Path to the configuration file

    Returns:
        Dict[str, Any]: Configuration data from the file

    Raises:
        ConfigurationError: If the file does not exist or cannot be parsed
    """
    if not os.path.isfile(config_file_path):
        raise ConfigurationError(f"Configuration file not found: {config_file_path}")

    config_parser = configparser.ConfigParser()
    try:
        config_parser.read(config_file_path)
    except configparser.Error as e:
        raise ConfigurationError(f"Error parsing configuration file: {e}") from e

    # Extract configuration data
    config_data = {}
    section_name = "drumgizmo_kit_generator"

    if section_name in config_parser:
        section = config_parser[section_name]

        # Process general kit information
        config_data["name"] = _strip_quotes(section.get("name", constants.DEFAULT_NAME))
        config_data["version"] = _strip_quotes(section.get("version", constants.DEFAULT_VERSION))
        config_data["description"] = _strip_quotes(section.get("description", ""))
        config_data["notes"] = _strip_quotes(section.get("notes", ""))
        config_data["author"] = _strip_quotes(section.get("author", ""))
        config_data["license"] = _strip_quotes(section.get("license", constants.DEFAULT_LICENSE))
        config_data["website"] = _strip_quotes(section.get("website", ""))

        # Process additional files
        config_data["logo"] = _strip_quotes(section.get("logo", ""))
        config_data["extra_files"] = _strip_quotes(section.get("extra_files", ""))

        # Process audio parameters
        config_data["samplerate"] = _strip_quotes(
            section.get("samplerate", str(constants.DEFAULT_SAMPLERATE))
        )
        config_data["velocity_levels"] = section.get(
            "velocity_levels", str(constants.DEFAULT_VELOCITY_LEVELS)
        )

        # Process MIDI configuration
        config_data["midi_note_min"] = section.get(
            "midi_note_min", str(constants.DEFAULT_MIDI_NOTE_MIN)
        )
        config_data["midi_note_max"] = section.get(
            "midi_note_max", str(constants.DEFAULT_MIDI_NOTE_MAX)
        )
        config_data["midi_note_median"] = section.get(
            "midi_note_median", str(constants.DEFAULT_MIDI_NOTE_MEDIAN)
        )

        # Process file extensions
        config_data["extensions"] = _strip_quotes(
            section.get("extensions", constants.DEFAULT_EXTENSIONS)
        )

        # Process channels
        config_data["channels"] = _strip_quotes(section.get("channels", constants.DEFAULT_CHANNELS))
        config_data["main_channels"] = _strip_quotes(
            section.get("main_channels", constants.DEFAULT_MAIN_CHANNELS)
        )
    else:
        logger.warning(f"Section '{section_name}' not found in {config_file_path}")

    return config_data


def _process_channel_list(
    channel_list: Optional[str], default_channels: str, channel_type: str
) -> str:
    """
    Process a channel list from configuration.

    Args:
        channel_list: Comma-separated list of channels or None
        default_channels: Default channels to use if channel_list is empty
        channel_type: Type of channels (for debug messages)

    Returns:
        str: Processed channel list
    """
    if channel_list:
        # Using custom channels
        logger.debug(f"Using custom {channel_type} from metadata: {channel_list}")
        return channel_list

    # Special case for main_channels: allow empty list
    if channel_type == "main channels" and not default_channels:
        logger.debug(f"Empty {channel_type} list, using empty list")
        return ""

    # Using default channels
    logger.debug(f"Empty {channel_type} list, using default: {default_channels}")
    return default_channels


def process_channels(config_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process channels and main channels from configuration.

    Args:
        config_data: Configuration data

    Returns:
        Dict[str, Any]: Updated configuration data
    """
    # Process channels
    config_data["channels"] = _process_channel_list(
        config_data.get("channels"), constants.DEFAULT_CHANNELS, "channels"
    )

    # Process main channels
    config_data["main_channels"] = _process_channel_list(
        config_data.get("main_channels"), constants.DEFAULT_MAIN_CHANNELS, "main channels"
    )

    return config_data


def get_config_value(config_data: Dict[str, Any], key: str, default_value: Any = None) -> Any:
    """
    Get a configuration value with fallback to default.

    Args:
        config_data: Configuration data
        key: Configuration key
        default_value: Default value if key is not found

    Returns:
        Any: Configuration value or default
    """
    return config_data.get(key, default_value)


def merge_configs(*configs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge multiple configuration dictionaries.
    Later dictionaries take precedence over earlier ones.

    Args:
        *configs: Configuration dictionaries to merge

    Returns:
        Dict[str, Any]: Merged configuration
    """
    result = {}
    for config in configs:
        for key, value in config.items():
            if value is not None:  # Only update if value is not None
                result[key] = value
    return result
