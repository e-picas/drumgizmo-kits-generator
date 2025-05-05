#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration module for DrumGizmo kit generator.
Contains functions for reading and processing configuration files and command line options.
"""

import configparser
import os
from typing import Any, Dict, Optional

from drumgizmo_kits_generator import constants, logger, transformers, validators
from drumgizmo_kits_generator.exceptions import ConfigurationError, ValidationError
from drumgizmo_kits_generator.utils import strip_quotes


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
        config_data["name"] = strip_quotes(section.get("name", constants.DEFAULT_NAME))
        config_data["version"] = strip_quotes(section.get("version", constants.DEFAULT_VERSION))
        config_data["description"] = strip_quotes(section.get("description", ""))
        config_data["notes"] = strip_quotes(section.get("notes", ""))
        config_data["author"] = strip_quotes(section.get("author", ""))
        config_data["license"] = strip_quotes(section.get("license", constants.DEFAULT_LICENSE))
        config_data["website"] = strip_quotes(section.get("website", ""))

        # Process additional files
        config_data["logo"] = strip_quotes(section.get("logo", ""))
        config_data["extra_files"] = strip_quotes(section.get("extra_files", ""))

        # Process audio parameters
        config_data["samplerate"] = strip_quotes(
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
        config_data["extensions"] = strip_quotes(
            section.get("extensions", constants.DEFAULT_EXTENSIONS)
        )

        # Process channels
        config_data["channels"] = strip_quotes(section.get("channels", constants.DEFAULT_CHANNELS))
        config_data["main_channels"] = strip_quotes(
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


def load_configuration(args):
    """
    Load configuration from defaults, config file, and command line arguments.

    Args:
        args: Parsed command line arguments

    Returns:
        Dict[str, Any]: Aggregated configuration

    Raises:
        ConfigurationError: If loading configuration fails
    """
    # Start with default configuration
    config_data = {
        "source": args.source,
        "target": args.target,
        "verbose": args.verbose,
        "dry_run": args.dry_run,
        "name": constants.DEFAULT_NAME,
        "version": constants.DEFAULT_VERSION,
        "license": constants.DEFAULT_LICENSE,
        "samplerate": constants.DEFAULT_SAMPLERATE,
        "extensions": constants.DEFAULT_EXTENSIONS,
        "velocity_levels": constants.DEFAULT_VELOCITY_LEVELS,
        "midi_note_min": constants.DEFAULT_MIDI_NOTE_MIN,
        "midi_note_max": constants.DEFAULT_MIDI_NOTE_MAX,
        "midi_note_median": constants.DEFAULT_MIDI_NOTE_MEDIAN,
        "channels": constants.DEFAULT_CHANNELS,
        "main_channels": constants.DEFAULT_MAIN_CHANNELS,
        "description": None,
        "notes": None,
        "author": None,
        "website": None,
        "logo": None,
        "extra_files": None,
    }

    # Load configuration from file if it exists
    config_file = args.config
    try:
        if os.path.isfile(os.path.join(args.source, config_file)):
            config_file = os.path.join(args.source, config_file)
            logger.info(f"Using configuration file: {config_file}")
            file_config = load_config_file(config_file)
            config_data.update(file_config)
        elif os.path.isfile(config_file):
            logger.info(f"Using configuration file: {config_file}")
            file_config = load_config_file(config_file)
            config_data.update(file_config)
        elif config_file != constants.DEFAULT_CONFIG_FILE:
            # Only show warning if a non-default config file was specified but not found
            logger.warning(f"Configuration file not found: {config_file}")
    except Exception as e:
        error_msg = f"Failed to load configuration file: {e}"
        raise ConfigurationError(error_msg) from e

    # Override with command line arguments
    cli_config = {}
    for key in [
        "name",
        "version",
        "description",
        "notes",
        "author",
        "license",
        "website",
        "logo",
        "samplerate",
        "extra_files",
        "velocity_levels",
        "midi_note_min",
        "midi_note_max",
        "midi_note_median",
        "extensions",
        "channels",
        "main_channels",
    ]:
        cli_value = getattr(args, key, None)
        if cli_value is not None:
            cli_config[key] = cli_value

    config_data.update(cli_config)

    return config_data


def transform_configuration(config_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform configuration values to appropriate types.

    Args:
        config_data: Raw configuration data

    Returns:
        Dict[str, Any]: Transformed configuration data

    Raises:
        ConfigurationError: If transformation fails
    """
    transformed_config = config_data.copy()

    try:
        # Apply transformers for each configuration entry
        for key in transformed_config:
            transformer_name = f"transform_{key}"
            if hasattr(transformers, transformer_name):
                transformer = getattr(transformers, transformer_name)
                transformed_config[key] = transformer(transformed_config[key])
    except Exception as e:
        error_msg = f"Failed to transform configuration: {e}"
        raise ConfigurationError(error_msg) from e

    return transformed_config


def validate_configuration(config_data: Dict[str, Any]) -> None:
    """
    Validate configuration values.

    Args:
        config_data: Configuration data to validate

    Raises:
        ValidationError: If validation fails
    """
    try:
        # Apply validators for each configuration entry
        for key in config_data:
            validator_name = f"validate_{key}"
            if hasattr(validators, validator_name):
                validator = getattr(validators, validator_name)
                validator(config_data[key], config_data)

        # Additional validation for MIDI note range
        if config_data["midi_note_min"] > config_data["midi_note_max"]:
            error_msg = f"MIDI note min ({config_data['midi_note_min']}) is greater than max ({config_data['midi_note_max']})"
            raise ValidationError(error_msg)
    except Exception as e:
        if not isinstance(e, ValidationError):
            error_msg = f"Failed to validate configuration: {e}"
            raise ValidationError(error_msg) from e
        raise
