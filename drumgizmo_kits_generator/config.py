#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SPDX-License-Identifier: MIT
SPDX-PackageName: DrumGizmo kits generator
SPDX-PackageHomePage: https://github.com/e-picas/drumgizmo-kits-generator
SPDX-FileCopyrightText: 2025 Pierre Cassat (Picas)

Configuration module for DrumGizmo kit generator.
Contains functions for reading and processing configuration files and command line options.
"""

import configparser
import os
from typing import Any, Dict

from drumgizmo_kits_generator import constants, logger, transformers, validators
from drumgizmo_kits_generator.exceptions import ConfigurationError, ValidationError


def load_configuration(args):
    """
    Load configuration from defaults, config file, and command line arguments,
    then transform and validate the configuration.

    Args:
        args: Parsed command line arguments

    Returns:
        Dict[str, Any]: Aggregated, transformed and validated configuration

    Raises:
        ConfigurationError: If loading or transforming configuration fails
        ValidationError: If configuration validation fails
    """
    # Start with default configuration
    config_data = constants.DEFAULT_CONFIG_DATA.copy()

    # Add command line arguments
    config_data.update(
        {
            "source": args.source,
            "target": args.target,
            "config": args.config,
            "verbose": args.verbose,
            "dry_run": args.dry_run,
        }
    )

    # Load configuration from file if it exists
    config_file = args.config
    try:
        if os.path.isfile(os.path.join(args.source, config_file)):
            config_file = os.path.join(args.source, config_file)
            logger.info(f"Using configuration file: {config_file}")
            file_config = load_config_file(config_file)
            config_data.update(file_config)
            config_data.update({"config_file": config_file})
        elif os.path.isfile(config_file):
            logger.info(f"Using configuration file: {config_file}")
            file_config = load_config_file(config_file)
            config_data.update(file_config)
            config_data.update({"config_file": config_file})
        elif config_file != constants.DEFAULT_CONFIG_FILE:
            # Only show warning if a non-default config file was specified but not found
            logger.warning(f"Configuration file not found: {config_file}")
    except Exception as e:
        error_msg = f"Failed to load configuration file: {e}"
        raise ConfigurationError(error_msg) from e

    # Override with command line arguments
    cli_config = {}
    for key in constants.DEFAULT_CONFIG_DATA:
        cli_value = getattr(args, key, None)
        if cli_value is not None:
            cli_config[key] = cli_value

    config_data.update(cli_config)

    # Transform configuration values
    try:
        config_data = transform_configuration(config_data)
    except Exception as e:
        error_msg = f"Failed to transform configuration: {e}"
        raise ConfigurationError(error_msg) from e

    # Validate configuration
    try:
        validate_configuration(config_data)
    except ValidationError as e:
        error_msg = f"Configuration validation failed: {e}"
        raise ValidationError(error_msg) from e
    except Exception as e:
        error_msg = f"Unexpected error during configuration validation: {e}"
        raise ConfigurationError(error_msg) from e

    return config_data


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

        # Process all configuration keys from DEFAULT_CONFIG_DATA
        for key in constants.DEFAULT_CONFIG_DATA:
            config_data[key] = section.get(key)
    else:
        logger.warning(f"Section '{section_name}' not found in {config_file_path}")
        # If section not found, return empty config (will use defaults in transform_configuration)
        return config_data

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
