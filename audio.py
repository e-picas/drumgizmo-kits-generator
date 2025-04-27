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
        volume = 1.0 - (i - 1) * 0.1
        print(
            f"Creating version at {volume:.1f}% volume for {instrument} (file {i}-{instrument}{extension})",
            file=sys.stderr,
        )

        # Use sox to adjust volume
        subprocess.run(
            [
                "sox",
                os.path.join(samples_dir, f"1-{instrument}{extension}"),
                os.path.join(samples_dir, f"{i}-{instrument}{extension}"),
                "vol",
                f"{volume}",
            ],
            check=False,
        )


def copy_sample_file(source_file, dest_file):
    """
    Copies an audio source file to a destination file.

    Args:
        source_file (str): Path to the source file
        dest_file (str): Path to the destination file
    """
    try:
        shutil.copy2(source_file, dest_file)
        return True
    except Exception as e:
        print(f"Error copying file {source_file} to {dest_file}: {e}", file=sys.stderr)
        return False


def find_audio_files(source_dir, extensions):
    """
    Searches for audio files in a source directory.

    Args:
        source_dir (str): Source directory
        extensions (list): List of audio file extensions to search for

    Returns:
        list: List of paths to the found audio files
    """
    samples = []

    for ext in extensions:
        ext_pattern = f"*.{ext}"
        found_samples = glob.glob(os.path.join(source_dir, ext_pattern))
        samples.extend(found_samples)

    return samples
