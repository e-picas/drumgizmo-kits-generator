#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=unused-argument
"""
Validation utilities for DrumGizmo kit generation.
Contains functions to validate configuration entries.
All methods should be named `validate_<configuration_entry_name>`.
"""

import os
from typing import Any, Dict, List, Optional

from drumgizmo_kits_generator import constants, logger
from drumgizmo_kits_generator.exceptions import ValidationError


def validate_name(value: Optional[str], config: Dict[str, Any]) -> str:  # NOSONAR python:S1172
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
    if not value:
        raise ValidationError("Kit name cannot be empty")
    return value


def validate_samplerate(
    value: Optional[str], config: Dict[str, Any]
) -> str:  # NOSONAR python:S1172
    """
    Validate the sample rate.

    Args:
        value: The sample rate to validate
        config: The complete configuration dictionary

    Returns:
        The validated sample rate

    Raises:
        ValidationError: If the sample rate is not a positive number
    """
    if not value:
        logger.warning(f"Sample rate is empty, using default: {constants.DEFAULT_SAMPLERATE}")
        return constants.DEFAULT_SAMPLERATE

    try:
        samplerate = int(value)
        if samplerate <= 0:
            raise ValidationError(f"Sample rate must be greater than 0, got: {samplerate}")
    except ValueError as e:
        raise ValidationError(f"Sample rate must be a number, got: {value}") from e

    return value


def validate_velocity_levels(
    value: Optional[int], config: Dict[str, Any]
) -> int:  # NOSONAR python:S1172
    """
    Validate the velocity levels.

    Args:
        value: The velocity levels to validate
        config: The complete configuration dictionary

    Returns:
        The validated velocity levels

    Raises:
        ValidationError: If the velocity levels is not a positive number
    """
    if not value:
        logger.warning(
            f"Velocity levels is empty, using default: {constants.DEFAULT_VELOCITY_LEVELS}"
        )
        return constants.DEFAULT_VELOCITY_LEVELS

    if value <= 0:
        raise ValidationError(f"Velocity levels must be greater than 0, got: {value}")

    return value


def validate_midi_note_min(
    value: Optional[int], config: Dict[str, Any]
) -> int:  # NOSONAR python:S1172
    """
    Validate the minimum MIDI note.

    Args:
        value: The minimum MIDI note to validate
        config: The complete configuration dictionary

    Returns:
        The validated minimum MIDI note

    Raises:
        ValidationError: If the minimum MIDI note is not in the valid range
    """
    if not value and value != 0:  # Handle case where value is 0
        logger.warning(
            f"Minimum MIDI note is empty, using default: {constants.DEFAULT_MIDI_NOTE_MIN}"
        )
        return constants.DEFAULT_MIDI_NOTE_MIN

    if value < 0 or value > 127:
        raise ValidationError(f"Minimum MIDI note must be between 0 and 127, got: {value}")

    # Check relationship with midi_note_max if it exists in config
    if "midi_note_max" in config and config["midi_note_max"] is not None:
        if value >= config["midi_note_max"]:
            raise ValidationError(
                f"Minimum MIDI note ({value}) must be less than maximum MIDI note ({config['midi_note_max']})"
            )

    # Check relationship with midi_note_median if it exists in config
    if "midi_note_median" in config and config["midi_note_median"] is not None:
        if value > config["midi_note_median"]:
            raise ValidationError(
                f"Minimum MIDI note ({value}) must be less than or equal to median MIDI note ({config['midi_note_median']})"
            )

    return value


def validate_midi_note_max(
    value: Optional[int], config: Dict[str, Any]
) -> int:  # NOSONAR python:S1172
    """
    Validate the maximum MIDI note.

    Args:
        value: The maximum MIDI note to validate
        config: The complete configuration dictionary

    Returns:
        The validated maximum MIDI note

    Raises:
        ValidationError: If the maximum MIDI note is not in the valid range
    """
    if not value:
        logger.warning(
            f"Maximum MIDI note is empty, using default: {constants.DEFAULT_MIDI_NOTE_MAX}"
        )
        return constants.DEFAULT_MIDI_NOTE_MAX

    if value < 0 or value > 127:
        raise ValidationError(f"Maximum MIDI note must be between 0 and 127, got: {value}")

    # Check relationship with midi_note_min if it exists in config
    if "midi_note_min" in config and config["midi_note_min"] is not None:
        if value <= config["midi_note_min"]:
            raise ValidationError(
                f"Maximum MIDI note ({value}) must be greater than minimum MIDI note ({config['midi_note_min']})"
            )

    # Check relationship with midi_note_median if it exists in config
    if "midi_note_median" in config and config["midi_note_median"] is not None:
        if value < config["midi_note_median"]:
            raise ValidationError(
                f"Maximum MIDI note ({value}) must be greater than or equal to median MIDI note ({config['midi_note_median']})"
            )

    return value


def validate_midi_note_median(
    value: Optional[int], config: Dict[str, Any]
) -> int:  # NOSONAR python:S1172
    """
    Validate the median MIDI note.

    Args:
        value: The median MIDI note to validate
        config: The complete configuration dictionary

    Returns:
        The validated median MIDI note

    Raises:
        ValidationError: If the median MIDI note is not in the valid range
    """
    if not value:
        logger.warning(
            f"Median MIDI note is empty, using default: {constants.DEFAULT_MIDI_NOTE_MEDIAN}"
        )
        return constants.DEFAULT_MIDI_NOTE_MEDIAN

    if value < 0 or value > 127:
        raise ValidationError(f"Median MIDI note must be between 0 and 127, got: {value}")

    # Check relationship with midi_note_min if it exists in config
    if "midi_note_min" in config and config["midi_note_min"] is not None:
        if value < config["midi_note_min"]:
            raise ValidationError(
                f"Median MIDI note ({value}) must be greater than or equal to minimum MIDI note ({config['midi_note_min']})"
            )

    # Check relationship with midi_note_max if it exists in config
    if "midi_note_max" in config and config["midi_note_max"] is not None:
        if value > config["midi_note_max"]:
            raise ValidationError(
                f"Median MIDI note ({value}) must be less than or equal to maximum MIDI note ({config['midi_note_max']})"
            )

    return value


def validate_extensions(
    value: Optional[List[str]], config: Dict[str, Any]
) -> List[str]:  # NOSONAR python:S1172
    """
    Validate the audio file extensions.

    Args:
        value: The list of extensions to validate
        config: The complete configuration dictionary

    Returns:
        The validated list of extensions

    Raises:
        ValidationError: If the extensions list is empty
    """
    if not value:
        raise ValidationError("Extensions list cannot be empty")

    # Ensure all extensions are trimmed
    return [ext.strip() for ext in value] if value else []


def validate_channels(
    value: Optional[List[str]], config: Dict[str, Any]
) -> List[str]:  # NOSONAR python:S1172
    """
    Validate the audio channels.

    Args:
        value: The list of channels to validate
        config: The complete configuration dictionary

    Returns:
        The validated list of channels

    Raises:
        ValidationError: If the channels list is empty
    """
    if not value:
        raise ValidationError("Channels list cannot be empty")

    # Ensure all channels are trimmed
    return [channel.strip() for channel in value] if value else []


def validate_main_channels(
    value: Optional[List[str]], config: Dict[str, Any]
) -> List[str]:  # NOSONAR python:S1172
    """
    Validate the main audio channels.

    Args:
        value: The list of main channels to validate
        config: The complete configuration dictionary

    Returns:
        The validated list of main channels

    Raises:
        ValidationError: If any main channel is not in the channels list
    """
    if not value:
        return []

    # Ensure all main channels are trimmed
    trimmed_value = [channel.strip() for channel in value]

    # Check that all main channels exist in the channels list
    if "channels" in config and config["channels"]:
        channels = [channel.strip() for channel in config["channels"]]
        for main_channel in trimmed_value:
            if main_channel not in channels:
                raise ValidationError(
                    f"Main channel '{main_channel}' is not in the channels list: {', '.join(channels)}"
                )

    return trimmed_value


def validate_logo(
    value: Optional[str], config: Dict[str, Any]
) -> Optional[str]:  # NOSONAR python:S1172
    """
    Validate the logo file.

    Args:
        value: The logo file path to validate
        config: The complete configuration dictionary

    Returns:
        The validated logo file path

    Raises:
        ValidationError: If the logo file does not exist
    """
    if not value:
        return None

    # Check if the logo file exists in the source directory
    if "source" in config and config["source"]:
        logo_path = os.path.join(config["source"], value)
        if not os.path.isfile(logo_path):
            raise ValidationError(f"Logo file does not exist: {logo_path}")

    return value


def validate_extra_files(
    value: Optional[List[str]], config: Dict[str, Any]
) -> List[str]:  # NOSONAR python:S1172
    """
    Validate the extra files.

    Args:
        value: The list of extra files to validate
        config: The complete configuration dictionary

    Returns:
        The validated list of extra files

    Raises:
        ValidationError: If any extra file does not exist
    """
    if not value:
        return []

    # Ensure all extra files are trimmed
    trimmed_value = [file_path.strip() for file_path in value]

    # Check if the extra files exist in the source directory
    if "source" in config and config["source"]:
        for file_path in trimmed_value:
            full_path = os.path.join(config["source"], file_path)
            if not os.path.isfile(full_path):
                raise ValidationError(f"Extra file does not exist: {full_path}")

    return trimmed_value


def validate_website(
    value: Optional[str], config: Dict[str, Any]
) -> Optional[str]:  # NOSONAR python:S1172
    """
    Validate the website URL.

    Args:
        value: The website URL to validate
        config: The complete configuration dictionary

    Returns:
        The validated website URL or None if empty
    """
    # Return None for empty strings
    if value == "":
        return None
    return value


def validate_version(value: Optional[str], config: Dict[str, Any]) -> str:  # NOSONAR python:S1172
    """
    Validate the kit version.

    Args:
        value: The kit version to validate
        config: The complete configuration dictionary

    Returns:
        The validated kit version

    Note:
        This function does not raise any exceptions as it accepts any string value
        and defaults to DEFAULT_VERSION if the value is empty.
    """
    # No specific validation required for version
    return value if value else constants.DEFAULT_VERSION


def validate_description(
    value: Optional[str], config: Dict[str, Any]
) -> Optional[str]:  # NOSONAR python:S1172
    """
    Validate the kit description.

    Args:
        value: The kit description to validate
        config: The complete configuration dictionary

    Returns:
        The validated kit description

    Note:
        This function does not raise any exceptions as it accepts any string value.
    """
    # No specific validation required for description
    return value


def validate_notes(
    value: Optional[str], config: Dict[str, Any]
) -> Optional[str]:  # NOSONAR python:S1172
    """
    Validate the kit notes.

    Args:
        value: The kit notes to validate
        config: The complete configuration dictionary

    Returns:
        The validated kit notes

    Note:
        This function does not raise any exceptions as it accepts any string value.
    """
    # No specific validation required for notes
    return value


def validate_author(
    value: Optional[str], config: Dict[str, Any]
) -> Optional[str]:  # NOSONAR python:S1172
    """
    Validate the kit author.

    Args:
        value: The kit author to validate
        config: The complete configuration dictionary

    Returns:
        The validated kit author

    Note:
        This function does not raise any exceptions as it accepts any string value.
    """
    # No specific validation required for author
    return value


def validate_license(value: Optional[str], config: Dict[str, Any]) -> str:  # NOSONAR python:S1172
    """
    Validate the kit license.

    Args:
        value: The kit license to validate
        config: The complete configuration dictionary

    Returns:
        The validated kit license

    Note:
        This function does not raise any exceptions as it accepts any string value
        and defaults to DEFAULT_LICENSE if the value is empty.
    """
    # No specific validation required for license
    return value if value else constants.DEFAULT_LICENSE
