#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration module for DrumGizmo kit generator.
Contains global variables and constants used across the application.
"""

import os
import sys
from typing import Any, Dict, List, Tuple

from drumgizmo_kits_generator.constants import DEFAULT_CHANNELS, DEFAULT_MAIN_CHANNELS

# Configuration storage
_config = {
    "channels": DEFAULT_CHANNELS.copy(),
    "main_channels": DEFAULT_MAIN_CHANNELS.copy(),
}


def get_channels() -> List[str]:
    """
    Get the current list of audio channels.

    Returns:
        List of audio channel names
    """
    return _config["channels"]


def get_main_channels() -> List[str]:
    """
    Get the current list of main audio channels.

    Returns:
        List of main audio channel names
    """
    return _config["main_channels"]


def update_channels_config(metadata: Dict[str, Any]) -> None:
    """
    Update the channels configuration from metadata.

    Args:
        metadata: Dictionary containing metadata with channels and main_channels
    """
    if "channels" in metadata:
        try:
            # Split comma-separated list of channels and remove whitespace at beginning and end
            channels_list = [ch.strip() for ch in str(metadata["channels"]).split(",")]
            # Filter out empty strings
            channels_list = [ch for ch in channels_list if ch]
            if channels_list:
                _config["channels"] = channels_list
                print(
                    f"Using custom channels from metadata: {_config['channels']}", file=sys.stderr
                )
        except ValueError as e:
            print(
                f"Warning: Invalid channels value in metadata: {metadata['channels']} - Value error: {e}",
                file=sys.stderr,
            )
        except TypeError as e:
            print(
                f"Warning: Invalid channels value in metadata: {metadata['channels']} - Type error: {e}",
                file=sys.stderr,
            )

    if "main_channels" in metadata:
        try:
            # Split comma-separated list of main channels and remove whitespace at beginning and end
            main_channels_list = [ch.strip() for ch in str(metadata["main_channels"]).split(",")]
            # Filter out empty strings
            main_channels_list = [ch for ch in main_channels_list if ch]
            if main_channels_list:
                _config["main_channels"] = main_channels_list
                print(
                    f"Using custom main channels from metadata: {_config['main_channels']}",
                    file=sys.stderr,
                )
        except ValueError as e:
            print(
                f"Warning: Invalid main_channels value in metadata: {metadata['main_channels']} - Value error: {e}",
                file=sys.stderr,
            )
        except TypeError as e:
            print(
                f"Warning: Invalid main_channels value in metadata: {metadata['main_channels']} - Type error: {e}",
                file=sys.stderr,
            )


# For backward compatibility
CHANNELS = DEFAULT_CHANNELS
MAIN_CHANNELS = DEFAULT_MAIN_CHANNELS


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
                    metadata[key_mapping[key]] = value

        # Update channels configuration
        update_channels_config(metadata)

        if metadata:
            print("Metadata read from configuration:", file=sys.stderr)
            for key, value in metadata.items():
                print(f"  {key}: {value}", file=sys.stderr)
        else:
            print("No valid metadata found in the configuration file", file=sys.stderr)
    except UnicodeDecodeError as e:
        print(f"Error reading configuration file: Unicode decode error: {e}", file=sys.stderr)
    except PermissionError as e:
        print(f"Error reading configuration file: Permission denied: {e}", file=sys.stderr)
    except OSError as e:
        print(f"Error reading configuration file: File system error: {e}", file=sys.stderr)

    print(f"Metadata loaded from config file: {metadata}", file=sys.stderr)
    return metadata
