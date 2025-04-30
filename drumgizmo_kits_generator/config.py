#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=broad-exception-caught
"""
Configuration module for DrumGizmo kit generator.
Contains global variables and constants used across the application.
"""

import os
import sys

# Default values for command line arguments
DEFAULT_EXTENSIONS = "wav,WAV,flac,FLAC,ogg,OGG"
DEFAULT_VELOCITY_LEVELS = 10
DEFAULT_MIDI_NOTE_MIN = 0
DEFAULT_MIDI_NOTE_MAX = 127
DEFAULT_MIDI_NOTE_MEDIAN = 60
DEFAULT_NAME = "DrumGizmo Kit"
DEFAULT_VERSION = "1.0"
DEFAULT_LICENSE = "Private license"
DEFAULT_SAMPLERATE = "44100"

# Default list of audio channels used in XML files
DEFAULT_CHANNELS = [
    "AmbL",
    "AmbR",
    "Hihat",
    "Kdrum_back",
    "Kdrum_front",
    "OHL",
    "OHR",
    "Ride",
    "Snare_bottom",
    "Snare_top",
    "Tom1",
    "Tom2",
    "Tom3",
]

# Default list of main channels (with main="true" attribute)
DEFAULT_MAIN_CHANNELS = ["AmbL", "AmbR", "OHL", "OHR"]

# Configuration storage
_config = {
    "channels": DEFAULT_CHANNELS.copy(),
    "main_channels": DEFAULT_MAIN_CHANNELS.copy(),
}


def get_channels():
    """
    Get the current list of audio channels.

    Returns:
        list: List of audio channel names
    """
    return _config["channels"]


def get_main_channels():
    """
    Get the current list of main audio channels.

    Returns:
        list: List of main audio channel names
    """
    return _config["main_channels"]


def update_channels_config(metadata):
    """
    Update the channels configuration from metadata.

    Args:
        metadata (dict): Dictionary containing metadata with channels and main_channels
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
        except Exception:
            print(
                f"Warning: Invalid channels value in metadata: {metadata['channels']}",
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
        except Exception:
            print(
                f"Warning: Invalid main_channels value in metadata: {metadata['main_channels']}",
                file=sys.stderr,
            )


# For backward compatibility
CHANNELS = DEFAULT_CHANNELS
MAIN_CHANNELS = DEFAULT_MAIN_CHANNELS


# pylint: disable-next=too-many-branches
def read_config_file(config_file):
    """
    Read configuration from a file and return a dictionary of metadata.

    Args:
        config_file (str): Path to the configuration file.

    Returns:
        dict: Dictionary of metadata read from the configuration file.
    """
    if not config_file or not os.path.isfile(config_file):
        print(f"Configuration file not found: {config_file}", file=sys.stderr)
        return {}

    print(f"Reading configuration from: {config_file}", file=sys.stderr)

    # Initialize metadata dictionary
    metadata = {}

    try:
        # Read the file content line by line
        with open(config_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue  # Skip empty lines and comments

                # Parse key-value pairs
                if "=" in line:
                    key, value = line.split("=", 1)
                else:
                    # Try with format KEY_NAME="value"
                    parts = line.split('"', 2)
                    if len(parts) >= 3:
                        key = parts[0].rstrip("=").rstrip()
                        value = parts[1]
                    else:
                        continue  # Skip invalid lines

                key = key.strip().lower()
                value = value.strip()

                # Remove quotes if present
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]

                # Map configuration keys to metadata keys
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

                if key in key_mapping:
                    metadata[key_mapping[key]] = value

        # Update channels and main_channels in the _config dictionary
        if "channels" in metadata:
            # Split comma-separated list of channels and remove whitespace at beginning and end
            channels_list = [ch.strip() for ch in metadata["channels"].split(",")]
            # Filter out empty strings
            channels_list = [ch for ch in channels_list if ch]
            if channels_list:
                _config["channels"] = channels_list
                print(f"Using custom channels from config: {_config['channels']}", file=sys.stderr)

        if "main_channels" in metadata:
            # Split comma-separated list of main channels and remove whitespace at beginning and end
            main_channels_list = [ch.strip() for ch in metadata["main_channels"].split(",")]
            # Filter out empty strings
            main_channels_list = [ch for ch in main_channels_list if ch]
            if main_channels_list:
                _config["main_channels"] = main_channels_list
                print(
                    f"Using custom main channels from config: {_config['main_channels']}",
                    file=sys.stderr,
                )

        if metadata:
            print("Metadata read from configuration:", file=sys.stderr)
            for key, value in metadata.items():
                print(f"  {key}: {value}", file=sys.stderr)
        else:
            print("No valid metadata found in the configuration file", file=sys.stderr)
    except Exception as e:
        print(f"Error reading configuration file: {e}", file=sys.stderr)

    print(f"Metadata loaded from config file: {metadata}", file=sys.stderr)
    return metadata
