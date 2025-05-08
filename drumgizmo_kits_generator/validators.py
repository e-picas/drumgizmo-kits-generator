#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=unused-argument
"""
SPDX-License-Identifier: MIT
SPDX-PackageName: DrumGizmo kits generator
SPDX-PackageHomePage: https://github.com/e-picas/drumgizmo-kits-generator
SPDX-FileCopyrightText: 2025 Pierre Cassat (Picas)

Validation utilities for DrumGizmo kit generation.
Contains functions to validate configuration entries.

All validator functions should:
*   be named `validate_<configuration_entry_name>`
*   follow the theorical interface `validate(value: Any, config: Dict[str, Any]) -> None`
*   raise `ValidationError` on failure
"""

import os
from typing import Any, Dict, Optional

from drumgizmo_kits_generator import constants
from drumgizmo_kits_generator.exceptions import ValidationError


def validate_name(value: Optional[str], config: Dict[str, Any]) -> None:  # NOSONAR python:S1172
    """
    Validate the kit name.

    Args:
        value: The kit name to validate
        config: The complete configuration dictionary

    Returns:
        The validated kit name

    Raises:
        ValidationError: If the name is empty
    """
    if value is None or (isinstance(value, str) and not value.strip()):
        raise ValidationError("Kit name cannot be empty")


def validate_samplerate(value: Any, config: Dict[str, Any]) -> None:  # NOSONAR python:S1172
    """
    Validate the sample rate.

    Args:
        value: The sample rate to validate
        config: The complete configuration dictionary

    Raises:
        ValidationError: If the sample rate is not a positive number
        TypeError: If the value cannot be converted to an integer
    """
    if value is None or (isinstance(value, str) and not value.strip()):
        raise ValidationError("Sample rate cannot be empty")

    try:
        samplerate = int(value)
    except (ValueError, TypeError) as exc:
        raise ValidationError(f"Sample rate must be a number, got: {value}") from exc

    if samplerate <= 0:
        raise ValidationError(f"Sample rate must be greater than 0, got: {samplerate}")


def validate_velocity_levels(value: Any, config: Dict[str, Any]) -> None:  # NOSONAR python:S1172
    """
    Validate the number of velocity levels.
    Args:
        value: The number of velocity levels to validate
        config: The complete configuration dictionary

    Raises:
        ValidationError: If the number of velocity levels is not a positive integer
        TypeError: If the value cannot be converted to an integer
    """
    if value is None or (isinstance(value, str) and not value.strip()):
        raise ValidationError("Number of velocity levels cannot be empty")

    try:
        velocity_levels = int(value)
    except (ValueError, TypeError) as exc:
        raise ValidationError(f"Number of velocity levels must be a number, got: {value}") from exc

    if velocity_levels <= 0:
        raise ValidationError(
            f"Number of velocity levels must be greater than 0, got: {velocity_levels}"
        )


def _validate_midi_note(
    value: Optional[int], config: Dict[str, Any]
) -> None:  # NOSONAR python:S1172
    """
    Validate a MIDI note.

    Args:
        value: The MIDI note to validate
        config: The complete configuration dictionary

    Raises:
        ValidationError: If the MIDI note is not in the valid range
    """
    if value is None or (isinstance(value, str) and not value.strip()):
        raise ValidationError("A MIDI note cannot be empty")

    try:
        midi_note = int(value)
    except (ValueError, TypeError) as exc:
        raise ValidationError(f"A MIDI note must be an integer, got: {value}") from exc

    if midi_note < 0 or midi_note > 127:
        raise ValidationError(f"A MIDI note must be between 0 and 127, got: {value}")


def validate_midi_note_min(
    value: Optional[int], config: Dict[str, Any]
) -> None:  # NOSONAR python:S1172
    """
    Validate the minimum MIDI note.

    Args:
        value: The minimum MIDI note to validate
        config: The complete configuration dictionary

    Raises:
        ValidationError: If the minimum MIDI note is not in the valid range
    """
    _validate_midi_note(value, config)


def validate_midi_note_max(value: Any, config: Dict[str, Any]) -> None:  # NOSONAR python:S1172
    """
    Validate the maximum MIDI note.

    Args:
        value: The maximum MIDI note to validate
        config: The complete configuration dictionary

    Raises:
        ValidationError: If the maximum MIDI note is not in the valid range
        TypeError: If the value cannot be converted to an integer
    """
    _validate_midi_note(value, config)


def validate_midi_note_median(value: Any, config: Dict[str, Any]) -> None:  # NOSONAR python:S1172
    """
    Validate the median MIDI note.

    Args:
        value: The median MIDI note to validate
        config: The complete configuration dictionary

    Raises:
        ValidationError: If the median MIDI note is not in the valid range
        TypeError: If the value cannot be converted to an integer
    """
    _validate_midi_note(value, config)


def validate_extensions(value: Any, config: Dict[str, Any]) -> None:  # NOSONAR python:S1172
    """
    Validate the audio file extensions.

    Args:
        value: The list of extensions to validate
        config: The complete configuration dictionary

    Raises:
        ValidationError: If the extensions list is empty or contains invalid values
    """
    if not value or (isinstance(value, (list, tuple)) and not value):
        raise ValidationError("At least one file extension must be specified")

    if not isinstance(value, (list, tuple)):
        raise ValidationError("Extensions must be a list of strings")

    for ext in value:
        if not ext or not isinstance(ext, str) or not ext.strip():
            raise ValidationError("Extension cannot be empty")


def validate_channels(value: Any, config: Dict[str, Any]) -> None:  # NOSONAR python:S1172
    """
    Validate the audio channels.

    Args:
        value: The list of channels to validate
        config: The complete configuration dictionary

    Raises:
        ValidationError: If the channels list is empty or contains invalid values
    """
    if not value or (isinstance(value, (list, tuple)) and not value):
        raise ValidationError("At least one channel must be specified")

    if not isinstance(value, (list, tuple)):
        raise ValidationError("Channels must be a list of strings")

    for channel in value:
        if not channel or not isinstance(channel, str) or not channel.strip():
            raise ValidationError("Channel name cannot be empty")


def validate_main_channels(value: Any, config: Dict[str, Any]) -> None:  # NOSONAR python:S1172
    """
    Validate the main audio channels.
    Args:
        value: The list of main channels to validate
        config: The complete configuration dictionary

    Raises:
        ValidationError: If any main channel is not in the channels list or is invalid
    """
    if not value:
        return

    if not isinstance(value, (list, tuple)):
        raise ValidationError("Main channels must be a list of strings")

    # Check that all main channels are valid strings
    for channel in value:
        if not channel or not isinstance(channel, str) or not channel.strip():
            raise ValidationError("Main channel name cannot be empty")

    # Check that all main channels exist in the channels list
    if "channels" in config and config["channels"]:
        channels = [ch.strip() for ch in config["channels"]]
        for main_channel in value:
            if main_channel not in channels:
                raise ValidationError(f"Main channel {main_channel} not found in channels list")


def validate_logo(value: Any, config: Dict[str, Any]) -> None:  # NOSONAR python:S1172
    """
    Validate the logo file.
    Args:
        value: The logo file path to validate
        config: The complete configuration dictionary

    Raises:
        ValidationError: If the logo file is invalid or does not exist
    """
    if not value:
        return

    if not isinstance(value, str) or not value.strip():
        raise ValidationError("Logo path must be a non-empty string")

    # Check if the logo file exists in the source directory
    if "source" in config and config["source"]:
        logo_path = os.path.join(config["source"], value)
        if not os.path.isfile(logo_path):
            raise ValidationError(f"Logo file does not exist in the source directory: {logo_path}")


def validate_extra_files(value: Any, config: Dict[str, Any]) -> None:  # NOSONAR python:S1172
    """
    Validate the extra files.
    Args:
        value: The list of extra files to validate
        config: The complete configuration dictionary

    Raises:
        ValidationError: If any extra file is invalid or does not exist
    """
    if not value:
        return

    if not isinstance(value, (list, tuple)):
        raise ValidationError("Extra files must be a list of strings")

    # Check if the extra files exist in the source directory
    if "source" in config and config["source"]:
        for file_path in value:
            if not file_path or not isinstance(file_path, str) or not file_path.strip():
                raise ValidationError("Extra file path cannot be empty")

            full_path = os.path.join(config["source"], file_path)
            if not os.path.isfile(full_path):
                raise ValidationError(
                    f"Extra file does not exist in the source directory: {full_path}"
                )


def validate_website(value: Any, config: Dict[str, Any]) -> None:  # NOSONAR python:S1172
    """
    Validate the website URL.

    Args:
        value: The website URL to validate
        config: The complete configuration dictionary

    Raises:
        ValidationError: If the website URL is not a valid string
    """
    if value is not None and not isinstance(value, str):
        raise ValidationError("Website must be a string or None")


def validate_version(value: Any, config: Dict[str, Any]) -> None:  # NOSONAR python:S1172
    """
    Validate the kit version.

    Args:
        value: The kit version to validate
        config: The complete configuration dictionary

    Raises:
        ValidationError: If the version is not a valid string
    """
    if value is not None and not isinstance(value, str):
        raise ValidationError("Version must be a string or None")


def validate_description(value: Any, config: Dict[str, Any]) -> None:  # NOSONAR python:S1172
    """
    Validate the kit description.
    Args:
        value: The kit description to validate
        config: The complete configuration dictionary

    Raises:
        ValidationError: If the description is not a valid string
    """
    if value is not None and not isinstance(value, str):
        raise ValidationError("Description must be a string or None")


def validate_notes(value: Any, config: Dict[str, Any]) -> None:  # NOSONAR python:S1172
    """
    Validate the kit notes.
    Args:
        value: The kit notes to validate
        config: The complete configuration dictionary

    Raises:
        ValidationError: If the notes are not a valid string
    """
    if value is not None and not isinstance(value, str):
        raise ValidationError("Notes must be a string or None")


def validate_author(value: Any, config: Dict[str, Any]) -> None:  # NOSONAR python:S1172
    """
    Validate the kit author.
    Args:
        value: The kit author to validate
        config: The complete configuration dictionary

    Raises:
        ValidationError: If the author is not a valid string
    """
    if value is not None and not isinstance(value, str):
        raise ValidationError("Author must be a string or None")


def validate_license(value: Any, config: Dict[str, Any]) -> None:  # NOSONAR python:S1172
    """
    Validate the kit license.
    Args:
        value: The kit license to validate
        config: The complete configuration dictionary

    Raises:
        ValidationError: If the license is not a valid string
    """
    if value is not None and not isinstance(value, str):
        raise ValidationError("License must be a string or None")


def validate_variations_method(value: Any, config: Dict[str, Any]) -> None:  # NOSONAR python:S1172
    """
    Validate the variations method.

    Args:
        value: The variations method to validate (must be 'linear' or 'logarithmic')
        config: The complete configuration dictionary

    Raises:
        ValidationError: If the value is not 'linear' or 'logarithmic'
    """
    if value is None or (isinstance(value, str) and not value.strip()):
        raise ValidationError("Variations method cannot be empty")

    if not isinstance(value, str):
        raise ValidationError("Variations method must be a string")

    if value.lower() not in constants.ALLOWED_VARIATIONS_METHOD:
        raise ValidationError(
            f"Variations method must be one of {constants.ALLOWED_VARIATIONS_METHOD}, got: {value}"
        )


def validate_whole_config(config_data: Dict[str, Any]) -> None:
    """
    Validate the complete configuration for consistency.

    Args:
        config_data: The complete configuration dictionary

    Raises:
        ValidationError: If the configuration is not consistent
    """
    # Check relationship between midi_note_min and midi_note_max
    if config_data["midi_note_min"] >= config_data["midi_note_max"]:
        raise ValidationError(
            f"Minimum MIDI note ({config_data['midi_note_min']}) "
            f"must be less than maximum MIDI note ({config_data['midi_note_max']})"
        )

    # Check relationship between midi_note_min and midi_note_median
    if config_data["midi_note_min"] > config_data["midi_note_median"]:
        raise ValidationError(
            f"Minimum MIDI note ({config_data['midi_note_min']}) "
            f"must be less than or equal to median MIDI note ({config_data['midi_note_median']})"
        )

    # Check relationship between midi_note_max and midi_note_median
    if config_data["midi_note_max"] < config_data["midi_note_median"]:
        raise ValidationError(
            f"Maximum MIDI note ({config_data['midi_note_max']}) "
            f"must be greater than or equal to median MIDI note ({config_data['midi_note_median']})"
        )


def validate_directories(source_dir: str, target_dir: str) -> None:
    """
    Validate source and target directories.

    Args:
        source_dir: Path to source directory
        target_dir: Path to target directory

    Raises:
        ValidationError: If source directory doesn't exist
        ValidationError: If target's parent directory doesn't exist
    """
    # Check if source directory exists
    if not os.path.isdir(source_dir):
        raise ValidationError(f"Source directory '{source_dir}' does not exist")

    # Validate target directory
    target_parent = os.path.dirname(os.path.abspath(target_dir))
    if not os.path.exists(target_dir) and not os.path.isdir(target_parent):
        raise ValidationError(f"Parent directory of target '{target_parent}' does not exist")
