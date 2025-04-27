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


def prepare_instrument_directory(instrument, target_dir):
    """
    Prepares the directory for an instrument.

    Args:
        instrument (str): Name of the instrument
        target_dir (str): Path to the target directory

    Returns:
        bool: True if preparation was successful, False otherwise
    """
    print(f"Creating directory for instrument: {instrument}", file=sys.stderr)

    # Create instrument directory
    instrument_dir = os.path.join(target_dir, instrument)
    if not os.path.exists(instrument_dir):
        try:
            os.makedirs(instrument_dir)
        except Exception as e:
            print(f"Error creating instrument directory: {e}", file=sys.stderr)
            return False

    # Create samples directory
    samples_dir = os.path.join(instrument_dir, "samples")
    if not os.path.exists(samples_dir):
        try:
            os.makedirs(samples_dir)
        except Exception as e:
            print(f"Error creating samples directory: {e}", file=sys.stderr)
            return False

    return True


def get_timestamp():
    """
    Get the current timestamp.

    Returns:
        str: Current timestamp in the format YYYY-MM-DD HH:MM
    """
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")


def extract_instrument_name(file_path):
    """
    Extract the instrument name from a file path.

    Args:
        file_path (str): Path to the file

    Returns:
        str: Instrument name
    """
    # Get the base name of the file (without path)
    base_name = os.path.basename(file_path)

    # Remove the extension
    instrument = os.path.splitext(base_name)[0]

    return instrument


def get_file_extension(file_path):
    """
    Get the file extension from a file path.

    Args:
        file_path (str): Path to the file

    Returns:
        str: File extension (with the dot)
    """
    # Get the extension
    _, extension = os.path.splitext(file_path)

    return extension


def print_summary(metadata, instruments, target_dir):
    """
    Print a summary of the generated kit.

    Args:
        metadata (dict): Kit metadata
        instruments (list): List of instruments
        target_dir (str): Path to the target directory
    """
    print(
        f"\nProcessing complete. DrumGizmo kit successfully created in: {target_dir}",
        file=sys.stderr,
    )
    print(f"Number of instruments created: {len(instruments)}", file=sys.stderr)
    print("Main files:", file=sys.stderr)
    print(f"- {os.path.join(target_dir, 'drumkit.xml')}", file=sys.stderr)
    print(f"- {os.path.join(target_dir, 'midimap.xml')}", file=sys.stderr)

    print("\nKit metadata summary:", file=sys.stderr)
    print(f"Name: {metadata.get('name', 'Unknown')}", file=sys.stderr)
    print(f"Version: {metadata.get('version', 'Unknown')}", file=sys.stderr)
    print(f"Description: {metadata.get('description', 'Unknown')}", file=sys.stderr)
    print(f"Notes: {metadata.get('notes', 'None')}", file=sys.stderr)
    print(f"Author: \"{metadata.get('author', 'Unknown')}\"", file=sys.stderr)
    print(f"License: {metadata.get('license', 'Unknown')}", file=sys.stderr)
    print(f"Sample rate: {metadata.get('samplerate', 'Unknown')} Hz", file=sys.stderr)
    print(f"Instrument prefix: \"{metadata.get('instrument_prefix', 'None')}\"", file=sys.stderr)
    print(f"Website: \"{metadata.get('website', 'None')}\"", file=sys.stderr)
    print(f"Logo: \"{metadata.get('logo', 'None')}\"", file=sys.stderr)
