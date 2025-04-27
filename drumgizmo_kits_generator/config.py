#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=broad-exception-caught
"""
Configuration module for DrumGizmo kit generator.
Contains global variables and constants used across the application.
"""

import os
import sys

# List of audio channels used in XML files
CHANNELS = [
    "AmbL",
    "AmbR",
    "Hihat",
    "Kdrum_back",
    "Kdrum_front",
    "Hihat",
    "OHL",
    "OHR",
    "Ride",
    "Snare_bottom",
    "Snare_top",
    "Tom1",
    "Tom2",
    "Tom3",
]

# List of main channels (with main="true" attribute)
MAIN_CHANNELS = ["AmbL", "AmbR", "OHL", "OHR"]


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
                    "kit_instrument_prefix": "instrument_prefix",
                    "kit_extra_files": "extra_files",
                }

                if key in key_mapping:
                    metadata[key_mapping[key]] = value

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
