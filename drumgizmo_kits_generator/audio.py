#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=broad-exception-caught
"""
Audio processing module for DrumGizmo kit generator.
Contains functions to manipulate audio files and create volume variations.
"""

import glob
import os
import shutil
import subprocess
import sys


def create_volume_variations(instrument, kit_dir, extension):
    """
    Creates 9 volume variations for a given sample.

    Args:
        instrument (str): Name of the instrument
        kit_dir (str): Target directory for the kit
        extension (str): Audio file extension (with the dot)
    """
    instrument_dir = os.path.join(kit_dir, instrument)
    samples_dir = os.path.join(instrument_dir, "samples")

    print(f"Creating volume variations for: {instrument}", file=sys.stderr)

    # Create 9 versions with a 10% volume decrease each time
    for i in range(2, 11):
        volume = 1.1 - (i / 10)
        source_file = os.path.join(samples_dir, f"1-{instrument}{extension}")
        dest_file = os.path.join(samples_dir, f"{i}-{instrument}{extension}")

        print(
            f"Creating version at {volume:.1f}% volume for {instrument} (file {i}-{instrument}{extension})",
            file=sys.stderr,
        )

        # Use SoX to create a version with reduced volume
        try:
            subprocess.run(
                ["sox", source_file, dest_file, "vol", str(volume)],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except subprocess.CalledProcessError as e:
            print(f"Error creating volume variation: {e}", file=sys.stderr)
            print(f"Command output: {e.stdout.decode()}", file=sys.stderr)
            print(f"Command error: {e.stderr.decode()}", file=sys.stderr)
        except Exception as e:
            print(f"Error creating volume variation: {e}", file=sys.stderr)


def copy_sample_file(source_file, dest_file):
    """
    Copy a sample file to the destination.

    Args:
        source_file (str): Path to the source file
        dest_file (str): Path to the destination file

    Returns:
        bool: True if the file was copied successfully, False otherwise
    """
    try:
        # Create destination directory if it doesn't exist
        dest_dir = os.path.dirname(dest_file)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)

        # Copy the file
        shutil.copy2(source_file, dest_file)
        return True
    except Exception as e:
        print(f"Error copying sample file: {e}", file=sys.stderr)
        return False


def find_audio_files(source_dir, extensions):
    """
    Find audio files in the source directory with the specified extensions.

    Args:
        source_dir (str): Source directory to search in
        extensions (list): List of file extensions to search for

    Returns:
        list: List of audio files found
    """
    audio_files = []

    for ext in extensions:
        # Add a dot to the extension if it doesn't have one
        if not ext.startswith("."):
            ext = f".{ext}"

        # Find files with the extension
        pattern = os.path.join(source_dir, f"*{ext}")
        audio_files.extend(glob.glob(pattern))

    return audio_files
