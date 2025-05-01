#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration module for DrumGizmo kit generator.
Contains functions for reading and processing configuration files.
"""

import os
import sys
from typing import Any, Dict, List, Tuple

from drumgizmo_kits_generator.constants import DEFAULT_CHANNELS, DEFAULT_MAIN_CHANNELS


def parse_config_line(line: str) -> Tuple[str, str]:
    """
    Parse a configuration line into key and value.

    Args:
        line: Configuration line to parse

    Returns:
        Tuple of (key, value) or (None, None) if line is invalid
    """
    line = line.strip()

    # Skip empty lines and comments
    if not line or line.startswith("#"):
        return "", ""

    # Parse key-value pairs with format key=value
    if "=" in line:
        key, value = line.split("=", 1)
        key = key.strip().lower()
        value = value.strip()

        # Remove quotes if present
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]

        return key, value

    # Try with format KEY_NAME="value"
    parts = line.split('"', 2)
    if len(parts) >= 3:
        key = parts[0].rstrip("=").rstrip().lower()
        value = parts[1]
        return key, value

    # Invalid line format
    return "", ""


def read_config_file(config_file: str) -> Dict[str, Any]:
    """
    Read configuration from a file and return a dictionary of metadata.

    Args:
        config_file: Path to the configuration file.

    Returns:
        Dictionary of metadata read from the configuration file.
    """
    if not config_file or not os.path.isfile(config_file):
        print(f"Configuration file not found: {config_file}", file=sys.stderr)
        return {}

    print(f"Reading configuration from: {config_file}", file=sys.stderr)

    # Initialize metadata dictionary
    metadata: Dict[str, Any] = {}

    # Define key mapping for configuration file
    key_mapping = {
        "kit_name": "name",
        "kit_description": "description",
        "kit_version": "version",
        "kit_author": "author",
        "kit_license": "license",
        "kit_notes": "notes",
        "kit_website": "website",
        "kit_logo": "logo",
        "kit_samplerate": "samplerate",
        "kit_extra_files": "extra_files",
        "kit_midi_note_min": "midi_note_min",
        "kit_midi_note_max": "midi_note_max",
        "kit_midi_note_median": "midi_note_median",
        "kit_velocity_levels": "velocity_levels",
        "kit_extensions": "extensions",
        "kit_channels": "channels",
        "kit_main_channels": "main_channels",
    }

    # Define keys that should be treated as lists
    list_keys = ["kit_extensions", "kit_extra_files"]

    try:
        # Read the file content line by line
        with open(config_file, "r", encoding="utf-8") as f:
            for line in f:
                key, value = parse_config_line(line)

                # Skip invalid lines
                if not key:
                    continue

                # Map configuration keys to metadata keys
                if key in key_mapping:
                    metadata_key = key_mapping[key]

                    # Traiter les clés qui doivent être des listes
                    if key in list_keys and value:
                        # Convertir en liste en séparant par des virgules et en supprimant les espaces
                        metadata[metadata_key] = [
                            item.strip() for item in value.split(",") if item.strip()
                        ]
                    else:
                        metadata[metadata_key] = value

        # Process channels and main_channels
        process_channels_config(metadata)

        if not metadata:
            print("No valid metadata found in the configuration file", file=sys.stderr)
    except UnicodeDecodeError as e:
        print(f"Error reading configuration file: Unicode decode error: {e}", file=sys.stderr)
    except PermissionError as e:
        print(f"Error reading configuration file: Permission denied: {e}", file=sys.stderr)
    except OSError as e:
        print(f"Error reading configuration file: File system error: {e}", file=sys.stderr)

    return metadata


def clean_channel_name(channel: str) -> str:
    """
    Clean a channel name by removing list formatting characters.

    Args:
        channel: Channel name to clean

    Returns:
        Cleaned channel name
    """
    # Remove list formatting characters and quotes
    return str(channel).strip("[]'\"")


def _process_channel_list(
    channels_value: Any, default_channels: str, channel_type: str = "channels"
) -> List[str]:
    """
    Process a channel list from metadata.

    Args:
        channels_value: Value from metadata
        default_channels: Default channels to use if the list is invalid
        channel_type: Type of channels ('channels' or 'main_channels')

    Returns:
        List of channels
    """
    try:
        # Handle the case where channels_value is already a list
        if isinstance(channels_value, list):
            # Clean each channel name in the list
            channels_list = [clean_channel_name(ch) for ch in channels_value]
            # Filter out empty strings
            channels_list = [ch for ch in channels_list if ch]
            if channels_list:
                return channels_list

        # Handle the case where channels_value is a string
        # Split comma-separated list of channels and remove whitespace at beginning and end
        channels_list = [ch.strip() for ch in str(channels_value).split(",")]
        # Clean each channel name
        channels_list = [clean_channel_name(ch) for ch in channels_list]
        # Filter out empty strings
        channels_list = [ch for ch in channels_list if ch]

        if channels_list:
            return channels_list

        # Use default channels if the list is empty
        # Split the default channels string into a list
        default_channels_list = [ch.strip() for ch in default_channels.split(",")]
        return [ch for ch in default_channels_list if ch]
    except (ValueError, TypeError) as e:
        print(
            f"Warning: Invalid {channel_type} value in metadata: {channels_value} - Error: {e}",
            file=sys.stderr,
        )
        # Split the default channels string into a list
        default_channels_list = [ch.strip() for ch in default_channels.split(",")]
        return [ch for ch in default_channels_list if ch]


def process_channels_config(metadata: Dict[str, Any]) -> None:
    """
    Process channels and main_channels in metadata.

    Args:
        metadata: Dictionary containing metadata with channels and main_channels
    """
    # Process channels
    if "channels" in metadata:
        metadata["channels"] = _process_channel_list(
            metadata["channels"], DEFAULT_CHANNELS, "channels"
        )
    else:
        # Set default channels if not provided
        metadata["channels"] = _process_channel_list(DEFAULT_CHANNELS, DEFAULT_CHANNELS, "channels")

    # Process main_channels
    if "main_channels" in metadata:
        main_channels_list = _process_channel_list(
            metadata["main_channels"], DEFAULT_MAIN_CHANNELS, "main_channels"
        )

        # Validate that all main channels exist in the channels list
        channels_list = metadata["channels"]
        invalid_channels = [ch for ch in main_channels_list if ch not in channels_list]
        if invalid_channels:
            print(
                f"Warning: The following main channels do not exist in channels list: {invalid_channels}",
                file=sys.stderr,
            )
            # Remove invalid channels from the main channels list
            main_channels_list = [ch for ch in main_channels_list if ch in channels_list]

        # Only update if there are valid main channels
        if main_channels_list:
            metadata["main_channels"] = main_channels_list
        else:
            print(
                f"Warning: No valid main channels found, using default: {DEFAULT_MAIN_CHANNELS}",
                file=sys.stderr,
            )
            metadata["main_channels"] = _process_channel_list(
                DEFAULT_MAIN_CHANNELS, DEFAULT_MAIN_CHANNELS, "main_channels"
            )
    else:
        # Set default main channels if not provided
        metadata["main_channels"] = _process_channel_list(
            DEFAULT_MAIN_CHANNELS, DEFAULT_MAIN_CHANNELS, "main_channels"
        )


def get_channels_from_metadata(metadata: Dict[str, Any]) -> List[str]:
    """
    Get the list of audio channels from metadata.

    Args:
        metadata: Dictionary containing metadata with channels

    Returns:
        List of audio channel names
    """
    return metadata.get(
        "channels", _process_channel_list(DEFAULT_CHANNELS, DEFAULT_CHANNELS, "channels")
    )


def get_main_channels_from_metadata(metadata: Dict[str, Any]) -> List[str]:
    """
    Get the list of main audio channels from metadata.

    Args:
        metadata: Dictionary containing metadata with main_channels

    Returns:
        List of main audio channel names
    """
    return metadata.get(
        "main_channels",
        _process_channel_list(DEFAULT_MAIN_CHANNELS, DEFAULT_MAIN_CHANNELS, "main_channels"),
    )
