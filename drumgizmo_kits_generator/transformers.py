#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SPDX-License-Identifier: MIT
SPDX-PackageName: DrumGizmo kits generator
SPDX-PackageHomePage: https://github.com/e-picas/drumgizmo-kits-generator
SPDX-FileCopyrightText: 2025 Pierre Cassat (Picas)

Transformers module for DrumGizmo kit generator.
Contains functions for transforming configuration values.
"""

from typing import Any, List

from drumgizmo_kits_generator import constants, logger
from drumgizmo_kits_generator.utils import split_comma_separated, strip_quotes


def transform_velocity_levels(value: Any) -> int:
    """
    Transform velocity_levels to an integer.

    Args:
        value: The velocity_levels value to transform

    Returns:
        int: The transformed velocity_levels value, or default if invalid
    """
    if value is None:
        return constants.DEFAULT_VELOCITY_LEVELS

    try:
        return int(strip_quotes(value))
    except (ValueError, TypeError):
        return constants.DEFAULT_VELOCITY_LEVELS


def transform_midi_note_min(value: Any) -> int:
    """
    Transform midi_note_min to an integer.

    Args:
        value: The midi_note_min value to transform

    Returns:
        int: The transformed midi_note_min value, or default if invalid
    """
    if value is None:
        return constants.DEFAULT_MIDI_NOTE_MIN

    try:
        return int(strip_quotes(value))
    except (ValueError, TypeError):
        return constants.DEFAULT_MIDI_NOTE_MIN


def transform_midi_note_max(value: Any) -> int:
    """
    Transform midi_note_max to an integer.

    Args:
        value: The midi_note_max value to transform

    Returns:
        int: The transformed midi_note_max value, or default if invalid
    """
    if value is None:
        return constants.DEFAULT_MIDI_NOTE_MAX

    try:
        return int(strip_quotes(value))
    except (ValueError, TypeError):
        return constants.DEFAULT_MIDI_NOTE_MAX


def transform_midi_note_median(value: Any) -> int:
    """
    Transform midi_note_median to an integer.

    Args:
        value: The midi_note_median value to transform

    Returns:
        int: The transformed midi_note_median value, or default if invalid
    """
    if value is None:
        return constants.DEFAULT_MIDI_NOTE_MEDIAN

    try:
        return int(strip_quotes(value))
    except (ValueError, TypeError):
        return constants.DEFAULT_MIDI_NOTE_MEDIAN


def transform_samplerate(value: Any) -> int:
    """
    Transform samplerate to an integer.

    Args:
        value: The samplerate value to transform

    Returns:
        int: The transformed samplerate value, or default if invalid
    """
    if value is None:
        return int(constants.DEFAULT_SAMPLERATE)

    try:
        return int(strip_quotes(value))
    except (ValueError, TypeError):
        logger.warning(f"Invalid samplerate value, using default: {constants.DEFAULT_SAMPLERATE}")
        return int(constants.DEFAULT_SAMPLERATE)


def transform_extensions(value: Any) -> List[str]:
    """
    Transform extensions string to a list of extensions.

    Args:
        value: The extensions value to transform (comma-separated string)

    Returns:
        List[str]: The transformed extensions list, or default if empty/invalid
    """
    # If value is None, return default extensions
    if value is None:
        value = constants.DEFAULT_EXTENSIONS

    # If not a string or list, use default
    if not isinstance(value, (str, list)):
        logger.warning(f"Invalid extensions type, using default: {constants.DEFAULT_EXTENSIONS}")
        value = constants.DEFAULT_EXTENSIONS

    # Split the value and get the result
    extensions = split_comma_separated(value)

    # If no extensions found, use default
    if not extensions:
        logger.warning(f"No valid extensions found, using default: {constants.DEFAULT_EXTENSIONS}")
        extensions = split_comma_separated(constants.DEFAULT_EXTENSIONS)

    return extensions


def transform_channels(value: Any) -> List[str]:
    """
    Transform channels string to a list of channels.

    Args:
        value: The channels value to transform (comma-separated string)

    Returns:
        List[str]: The transformed channels list, or default if empty/invalid
    """
    # If value is None, return default channels
    if value is None:
        value = constants.DEFAULT_CHANNELS

    # If not a string or list, use default
    if not isinstance(value, (str, list)):
        logger.warning(f"Invalid channels type, using default: {constants.DEFAULT_CHANNELS}")

    # Split the value and get the result
    channels = split_comma_separated(value)

    # If no channels found, use default
    if not channels:
        logger.warning(f"No valid channels found, using default: {constants.DEFAULT_CHANNELS}")
        channels = split_comma_separated(constants.DEFAULT_CHANNELS)

    return channels


def transform_main_channels(value: Any) -> List[str]:
    """
    Transform main_channels string to a list of main channels.

    Args:
        value: The main_channels value to transform (comma-separated string)

    Returns:
        List[str]: The transformed main_channels list, or default if empty/invalid
    """
    # If value is None, return default main channels
    if value is None:
        value = constants.DEFAULT_MAIN_CHANNELS

    # If not a string or list, use default
    if not isinstance(value, (str, list)):
        logger.warning(
            f"Invalid main_channels type, using default: {constants.DEFAULT_MAIN_CHANNELS}"
        )
        value = constants.DEFAULT_MAIN_CHANNELS

    # Split the value and get the result
    main_channels = split_comma_separated(value)

    # If no main_channels found, return empty list (main channels can be empty)
    if not main_channels:
        return []
    return main_channels


def transform_extra_files(value: Any) -> List[str]:
    """
    Transform extra_files string to a list of file paths.

    Args:
        value: The extra_files value to transform (comma-separated string)

    Returns:
        List[str]: The transformed extra_files list, or empty list if None/invalid
    """
    # If value is None, return empty list
    if value is None:
        return []

    # If value is already a list, return it
    if isinstance(value, list):
        return value

    # If not a string, return empty list
    if not isinstance(value, str):
        logger.warning("Invalid extra_files type, using empty list")
        return []

    # Split by comma and strip whitespace
    extra_files = split_comma_separated(value)
    return extra_files


def transform_name(value: Any) -> str:
    """
    Transform name to a string.

    Args:
        value: The name value to transform

    Returns:
        str: The transformed name value
    """
    if value is None:
        return constants.DEFAULT_NAME
    return str(strip_quotes(value)).strip()


def transform_version(value: Any) -> str:
    """
    Transform version to a string.

    Args:
        value: The version value to transform

    Returns:
        str: The transformed version value
    """
    if value is None:
        return constants.DEFAULT_VERSION
    return str(strip_quotes(value)).strip()


def transform_description(value: Any) -> str:
    """
    Transform description to a string.

    Args:
        value: The description value to transform

    Returns:
        str: The transformed description value, or empty string if None
    """
    if value is None:
        return ""
    return str(strip_quotes(value)).strip()


def transform_notes(value: Any) -> str:
    """
    Transform notes to a string.

    Args:
        value: The notes value to transform

    Returns:
        str: The transformed notes value, or empty string if None
    """
    if value is None:
        return ""
    return str(strip_quotes(value)).strip()


def transform_author(value: Any) -> str:
    """
    Transform author to a string.

    Args:
        value: The author value to transform

    Returns:
        str: The transformed author value, or empty string if None
    """
    if value is None:
        return ""
    return str(strip_quotes(value)).strip()


def transform_license(value: Any) -> str:
    """
    Transform license to a string.

    Args:
        value: The license value to transform

    Returns:
        str: The transformed license value, or default if None
    """
    if value is None:
        return constants.DEFAULT_LICENSE
    return str(strip_quotes(value)).strip()


def transform_website(value: Any) -> str:
    """
    Transform website to a string.

    Args:
        value: The website value to transform

    Returns:
        str: The transformed website value, or empty string if None
    """
    if value is None:
        return ""
    return str(strip_quotes(value)).strip()


def transform_logo(value: Any) -> str:
    """
    Transform logo to a string.

    Args:
        value: The logo value to transform

    Returns:
        str: The transformed logo value, or empty string if None
    """
    if value is None:
        return ""
    return str(strip_quotes(value)).strip()


def transform_variations_method(value: Any) -> str:
    """
    Transform variations_method to a valid value (linear or logarithmic).

    Args:
        value: The variations_method value to transform

    Returns:
        str: The transformed variations_method value, or default if invalid

    Raises:
        InvalidConfigurationError: If the value is not 'linear' or 'logarithmic'
    """
    if value is None:
        value = constants.DEFAULT_VARIATIONS_METHOD

    return str(strip_quotes(value)).strip().lower()
