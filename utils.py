#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=broad-exception-caught
"""
Utility module for DrumGizmo kit generator.
Contains various helper functions.
"""

import datetime
import os
import shutil
import sys


def prepare_target_directory(target_dir):
    """
    Prepares the target directory by removing it if it already exists.

    Args:
        target_dir (str): Path to the target directory

    Returns:
        bool: True if preparation was successful, False otherwise
    """
    # Remove target directory if it already exists
    if os.path.exists(target_dir):
        print(f"Removing existing target directory: {target_dir}", file=sys.stderr)
        try:
            shutil.rmtree(target_dir)
        except Exception as e:
            print(f"Error removing target directory: {e}", file=sys.stderr)
            return False

    # Create target directory
    try:
        os.makedirs(target_dir)
        return True
    except Exception as e:
        print(f"Error creating target directory: {e}", file=sys.stderr)
        return False


def prepare_instrument_directory(instrument, kit_dir):
    """
    Prepares the directory for an instrument.

    Args:
        instrument (str): Name of the instrument
        kit_dir (str): Target directory for the kit

    Returns:
        bool: True if preparation was successful, False otherwise
    """
    instrument_dir = os.path.join(kit_dir, instrument)
    samples_dir = os.path.join(instrument_dir, "samples")

    print(f"Creating directory for instrument: {instrument}", file=sys.stderr)

    try:
        os.makedirs(instrument_dir, exist_ok=True)
        os.makedirs(samples_dir, exist_ok=True)
        return True
    except Exception as e:
        print(f"Error creating directory for instrument {instrument}: {e}", file=sys.stderr)
        return False


def get_timestamp():
    """
    Returns the current date and time in YYYY-MM-DD HH:MM format.

    Returns:
        str: Formatted current date and time
    """
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M")


def extract_instrument_name(filename):
    """
    Extracts the instrument name from a filename.

    Args:
        filename (str): Audio filename

    Returns:
        str: Instrument name
    """
    # Get the base filename without the path
    basename = os.path.basename(filename)

    # Remove the extension
    instrument = os.path.splitext(basename)[0]

    return instrument


def get_file_extension(filename):
    """
    Gets the file extension with the dot.

    Args:
        filename (str): Filename

    Returns:
        str: File extension with the dot
    """
    return os.path.splitext(filename)[1]


def print_summary(metadata, instruments, kit_dir):
    """
    Displays a summary of the kit generation.

    Args:
        metadata (dict): Kit metadata
        instruments (list): List of instrument names
        kit_dir (str): Target directory for the kit
    """
    print(f"Processing complete. DrumGizmo kit successfully created in: {kit_dir}", file=sys.stderr)
    print(f"Number of instruments created: {len(instruments)}", file=sys.stderr)
    print("Main files:", file=sys.stderr)
    print(f"- {os.path.join(kit_dir, 'drumkit.xml')}", file=sys.stderr)
    print(f"- {os.path.join(kit_dir, 'midimap.xml')}", file=sys.stderr)
    print("", file=sys.stderr)
    print("Kit metadata summary:", file=sys.stderr)
    print(f"Name: {metadata.get('name', 'N/A')}", file=sys.stderr)
    print(f"Version: {metadata.get('version', 'N/A')}", file=sys.stderr)
    print(f"Description: {metadata.get('description', 'N/A')}", file=sys.stderr)

    notes = metadata.get("notes", "")
    if notes:
        # Remove quotes if present
        if notes.startswith('"') and notes.endswith('"'):
            notes = notes[1:-1]
        elif notes.startswith("'") and notes.endswith("'"):
            notes = notes[1:-1]

    print(
        f'Notes: "{notes}" - Generated with create_drumgizmo_kit.py at {get_timestamp()}',
        file=sys.stderr,
    )

    author = metadata.get("author", "")
    if author:
        # Remove quotes if present
        if author.startswith('"') and author.endswith('"'):
            author = author[1:-1]
        elif author.startswith("'") and author.endswith("'"):
            author = author[1:-1]

    print(f'Author: "{author}"', file=sys.stderr)
    print(f"License: {metadata.get('license', 'N/A')}", file=sys.stderr)
    print(f"Sample rate: {metadata.get('samplerate', 'N/A')} Hz", file=sys.stderr)
    print(f"Instrument prefix: \"{metadata.get('instrument_prefix', 'N/A')}\"", file=sys.stderr)

    website = metadata.get("website", "")
    if website:
        # Remove quotes if present
        if website.startswith('"') and website.endswith('"'):
            website = website[1:-1]
        elif website.startswith("'") and website.endswith("'"):
            website = website[1:-1]

    print(f'Website: "{website}"', file=sys.stderr)

    logo = metadata.get("logo", "")
    if logo:
        # Remove quotes if present
        if logo.startswith('"') and logo.endswith('"'):
            logo = logo[1:-1]
        elif logo.startswith("'") and logo.endswith("'"):
            logo = logo[1:-1]

    print(f'Logo: "{logo}"', file=sys.stderr)
