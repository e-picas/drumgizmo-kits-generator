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


def create_volume_variations(
    instrument, kit_dir, extension, velocity_levels=10, target_samplerate=None
):
    """
    Creates volume variations for a given sample.

    Args:
        instrument (str): Name of the instrument
        kit_dir (str): Target directory for the kit
        extension (str): Audio file extension (with the dot)
        velocity_levels (int): Number of velocity levels to generate (default: 10)
        target_samplerate (str, optional): Target sample rate in Hz
    """
    instrument_dir = os.path.join(kit_dir, instrument)
    samples_dir = os.path.join(instrument_dir, "samples")

    print(f"Creating volume variations for: {instrument}", file=sys.stderr)

    # Skip if only one velocity level is requested
    if velocity_levels <= 1:
        print("Skipping volume variations (only 1 velocity level requested)", file=sys.stderr)
        return

    # Create velocity_levels-1 versions with decreasing volume
    for i in range(2, velocity_levels + 1):
        # Calculate volume factor: from 0.9 down to 0.1 for 10 levels
        # For different number of levels, scale accordingly
        volume = 1.0 - ((i - 1) / velocity_levels)
        source_file = os.path.join(samples_dir, f"1-{instrument}{extension}")
        dest_file = os.path.join(samples_dir, f"{i}-{instrument}{extension}")

        print(
            f"Creating version at {volume:.1f}% volume for {instrument} (file {i}-{instrument}{extension})",
            file=sys.stderr,
        )

        # Use SoX to create a version with reduced volume
        try:
            # If a target sample rate is provided, include it in the command
            if target_samplerate:
                subprocess.run(
                    ["sox", source_file, "-r", target_samplerate, dest_file, "vol", str(volume)],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
            else:
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


def convert_sample_rate(source_file, dest_file, target_samplerate):
    """
    Convert a sample file to the target sample rate.

    Args:
        source_file (str): Path to the source file
        dest_file (str): Path to the destination file
        target_samplerate (str): Target sample rate in Hz

    Returns:
        bool: True if the file was converted successfully, False otherwise
    """
    try:
        # Create destination directory if it doesn't exist
        dest_dir = os.path.dirname(dest_file)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)

        # Use SoX to convert the sample rate
        subprocess.run(
            ["sox", source_file, "-r", target_samplerate, dest_file],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error converting sample rate: {e}", file=sys.stderr)
        print(f"Command output: {e.stdout.decode()}", file=sys.stderr)
        print(f"Command error: {e.stderr.decode()}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"Error converting sample rate: {e}", file=sys.stderr)
        return False


def copy_sample_file(source_file, dest_file, target_samplerate=None):
    """
    Copy a sample file to the destination, optionally converting the sample rate.

    Args:
        source_file (str): Path to the source file
        dest_file (str): Path to the destination file
        target_samplerate (str, optional): Target sample rate in Hz. If provided,
                                          the file will be converted to this sample rate.

    Returns:
        bool: True if the file was copied successfully, False otherwise
    """
    try:
        # Create destination directory if it doesn't exist
        dest_dir = os.path.dirname(dest_file)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)

        # If a target sample rate is provided, convert the file
        if target_samplerate:
            print(
                f"Converting {os.path.basename(source_file)} to {target_samplerate} Hz",
                file=sys.stderr,
            )
            return convert_sample_rate(source_file, dest_file, target_samplerate)

        # Otherwise, just copy the file
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
