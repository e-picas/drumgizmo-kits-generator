#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audio processing module for DrumGizmo kit generator.
Contains functions to manipulate audio files and create volume variations.
"""

import glob
import os
import shutil
import subprocess
import sys
from typing import List, Optional


def create_volume_variations(
    instrument: str,
    kit_dir: str,
    extension: str,
    velocity_levels: int = 10,
    target_samplerate: Optional[str] = None,
) -> None:
    """
    Creates volume variations for a given sample.

    Args:
        instrument: Name of the instrument
        kit_dir: Target directory for the kit
        extension: Audio file extension (with the dot)
        velocity_levels: Number of velocity levels to generate (default: 10)
        target_samplerate: Target sample rate in Hz
    """
    instrument_dir = os.path.join(kit_dir, instrument)
    samples_dir = os.path.join(instrument_dir, "samples")

    print(f"Creating volume variations for: {instrument}", file=sys.stderr)

    # Skip if only one velocity level is requested
    if velocity_levels <= 1:
        print("Skipping volume variations (only 1 velocity level requested)", file=sys.stderr)
        return

    # Create velocity_levels-1 versions with decreasing volume
    source_file = os.path.join(samples_dir, f"1-{instrument}{extension}")

    for i in range(2, velocity_levels + 1):
        # Calculate volume factor: from 0.9 down to 0.1 for 10 levels
        # For different number of levels, scale accordingly
        volume = 1.0 - ((i - 1) / velocity_levels)
        dest_file = os.path.join(samples_dir, f"{i}-{instrument}{extension}")

        print(
            f"Creating version at {volume:.1f}% volume for {instrument} (file {i}-{instrument}{extension})",
            file=sys.stderr,
        )

        # Use SoX to create a version with reduced volume
        try:
            # If a target sample rate is provided, include it in the command
            sox_cmd = ["sox", source_file]

            if target_samplerate:
                sox_cmd.extend(["-r", target_samplerate])

            sox_cmd.extend([dest_file, "vol", str(volume)])

            subprocess.run(
                sox_cmd,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        except subprocess.CalledProcessError as e:
            print(f"Error creating volume variation: {e}", file=sys.stderr)
            print(f"Command output: {e.stdout}", file=sys.stderr)
            print(f"Command error: {e.stderr}", file=sys.stderr)
        except FileNotFoundError as e:
            print(f"Error creating volume variation: SoX command not found: {e}", file=sys.stderr)
        except PermissionError as e:
            print(f"Error creating volume variation: Permission denied: {e}", file=sys.stderr)
        except (OSError, IOError) as e:
            print(f"Error creating volume variation: File system error: {e}", file=sys.stderr)
        except Exception as e:  # pylint: disable=broad-exception-caught
            # Gardé pour la compatibilité avec les tests existants
            print(f"Error creating volume variation: {e}", file=sys.stderr)


def convert_sample_rate(source_file: str, dest_file: str, target_samplerate: str) -> bool:
    """
    Convert a sample file to the target sample rate.

    Args:
        source_file: Path to the source file
        dest_file: Path to the destination file
        target_samplerate: Target sample rate in Hz

    Returns:
        True if the file was converted successfully, False otherwise
    """
    success = False
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
            text=True,
        )
        success = True
    except subprocess.CalledProcessError as e:
        print(f"Error converting sample rate: {e}", file=sys.stderr)
        print(f"Command output: {e.stdout}", file=sys.stderr)
        print(f"Command error: {e.stderr}", file=sys.stderr)
    except FileNotFoundError as e:
        print(f"Error converting sample rate: SoX command not found: {e}", file=sys.stderr)
    except PermissionError as e:
        print(f"Error converting sample rate: Permission denied: {e}", file=sys.stderr)
    except (OSError, IOError) as e:
        print(f"Error converting sample rate: File system error: {e}", file=sys.stderr)
    except Exception as e:  # pylint: disable=broad-exception-caught
        # Gardé pour la compatibilité avec les tests existants
        print(f"Error converting sample rate: {e}", file=sys.stderr)
    return success


def copy_sample_file(
    source_file: str, dest_file: str, target_samplerate: Optional[str] = None
) -> bool:
    """
    Copy a sample file to the destination, optionally converting the sample rate.

    Args:
        source_file: Path to the source file
        dest_file: Path to the destination file
        target_samplerate: Target sample rate in Hz. If provided,
                          the file will be converted to this sample rate.

    Returns:
        True if the file was copied successfully, False otherwise
    """
    success = False
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
            success = convert_sample_rate(source_file, dest_file, target_samplerate)
        else:
            # Otherwise, just copy the file
            shutil.copy2(source_file, dest_file)
            success = True
    except FileNotFoundError as e:
        print(f"Error copying sample file: File not found: {e}", file=sys.stderr)
    except PermissionError as e:
        print(f"Error copying sample file: Permission denied: {e}", file=sys.stderr)
    except shutil.Error as e:
        print(f"Error copying sample file: Shutil error: {e}", file=sys.stderr)
    except (OSError, IOError) as e:
        print(f"Error copying sample file: File system error: {e}", file=sys.stderr)
    except Exception as e:  # pylint: disable=broad-exception-caught
        # Gardé pour la compatibilité avec les tests existants
        print(f"Error copying sample file: {e}", file=sys.stderr)
    return success


def find_audio_files(source_dir: str, extensions: str) -> List[str]:
    """
    Find audio files in the source directory with the specified extensions.

    Args:
        source_dir: Source directory to search in
        extensions: Comma-separated list of file extensions to search for

    Returns:
        List of audio files found
    """
    audio_files = []

    # Convert extensions string to list
    if isinstance(extensions, str):
        extensions = extensions.split(",")

    for ext in extensions:
        # Remove whitespace
        ext = ext.strip()

        # Skip empty extensions
        if not ext:
            continue

        # Add a dot to the extension if it doesn't have one
        if not ext.startswith("."):
            ext = f".{ext}"

        # Find files with the extension
        pattern = os.path.join(source_dir, f"*{ext}")
        print(f"Searching for pattern: {pattern}", file=sys.stderr)
        found_files = glob.glob(pattern)
        print(f"Found {len(found_files)} files with extension {ext}", file=sys.stderr)
        audio_files.extend(found_files)

    return audio_files
