#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utility module for DrumGizmo kit generator.
Contains various helper functions.
"""

import argparse
import datetime
import os
import shutil
import subprocess
import sys
from typing import Any, Dict, List, Optional


def prepare_target_directory(target_dir: str) -> bool:
    """
    Prepares the target directory by removing it if it already exists.

    Args:
        target_dir: Path to the target directory

    Returns:
        True if preparation was successful, False otherwise
    """
    # Remove target directory if it already exists
    if os.path.exists(target_dir):
        print(f"Removing existing target directory: {target_dir}", file=sys.stderr)
        try:
            shutil.rmtree(target_dir)
        except PermissionError as e:
            print(f"Error removing target directory: Permission denied: {e}", file=sys.stderr)
            return False
        except shutil.Error as e:
            print(f"Error removing target directory: Shutil error: {e}", file=sys.stderr)
            return False
        except (OSError, IOError) as e:
            print(f"Error removing target directory: File system error: {e}", file=sys.stderr)
            return False

    # Create target directory
    try:
        os.makedirs(target_dir)
        return True
    except PermissionError as e:
        print(f"Error creating target directory: Permission denied: {e}", file=sys.stderr)
        return False
    except (OSError, IOError) as e:
        print(f"Error creating target directory: File system error: {e}", file=sys.stderr)
        return False


def prepare_instrument_directory(instrument: str, target_dir: str) -> bool:
    """
    Prepares the directory for an instrument.

    Args:
        instrument: Name of the instrument
        target_dir: Path to the target directory

    Returns:
        True if preparation was successful, False otherwise
    """
    print(f"Creating directory for instrument: {instrument}", file=sys.stderr)

    # Create instrument directory
    instrument_dir = os.path.join(target_dir, instrument)
    if not os.path.exists(instrument_dir):
        try:
            os.makedirs(instrument_dir)
        except PermissionError as e:
            print(f"Error creating instrument directory: Permission denied: {e}", file=sys.stderr)
            return False
        except (OSError, IOError) as e:
            print(f"Error creating instrument directory: File system error: {e}", file=sys.stderr)
            return False

    # Create samples directory
    samples_dir = os.path.join(instrument_dir, "samples")
    if not os.path.exists(samples_dir):
        try:
            os.makedirs(samples_dir)
        except PermissionError as e:
            print(f"Error creating samples directory: Permission denied: {e}", file=sys.stderr)
            return False
        except (OSError, IOError) as e:
            print(f"Error creating samples directory: File system error: {e}", file=sys.stderr)
            return False

    return True


def get_timestamp() -> str:
    """
    Get the current timestamp.

    Returns:
        Current timestamp in the format YYYY-MM-DD HH:MM
    """
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")


def extract_instrument_name(file_path: str) -> str:
    """
    Extract the instrument name from a file path.

    Args:
        file_path: Path to the file

    Returns:
        Instrument name
    """
    # Get the base name of the file (without path)
    base_name = os.path.basename(file_path)

    # Remove the extension
    instrument = os.path.splitext(base_name)[0]

    return instrument


def get_file_extension(file_path: str) -> str:
    """
    Get the file extension from a file path.

    Args:
        file_path: Path to the file

    Returns:
        File extension (with the dot)
    """
    # Get the extension
    _, extension = os.path.splitext(file_path)

    return extension


def get_audio_samplerate(audio_file: str) -> Optional[int]:
    """
    Get the sample rate of an audio file using SoX.

    Args:
        audio_file: Path to the audio file

    Returns:
        Sample rate in Hz, or None if the file could not be read
    """
    if not os.path.exists(audio_file):
        print(f"Error: Audio file not found: {audio_file}", file=sys.stderr)
        return None

    try:
        # Use SoX to get the sample rate
        result = subprocess.run(
            ["soxi", "-r", audio_file],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        # Parse the output (should be just the sample rate)
        samplerate = int(result.stdout.strip())
        return samplerate
    except subprocess.CalledProcessError as e:
        print(f"Error getting sample rate: {e}", file=sys.stderr)
        print(f"Command error: {e.stderr}", file=sys.stderr)
        return None
    except FileNotFoundError as e:
        print(f"Error getting sample rate: SoX command not found: {e}", file=sys.stderr)
        return None
    except ValueError as e:
        print(f"Error getting sample rate: Invalid sample rate value: {e}", file=sys.stderr)
        return None
    except (OSError, IOError) as e:
        print(f"Error getting sample rate: File system error: {e}", file=sys.stderr)
        return None


def print_verbose(message: str, args: argparse.Namespace) -> None:
    """
    Print a verbose message if verbose mode is enabled.

    Args:
        message: Message to print
        args: Command line arguments with a 'verbose' attribute
    """
    if args.verbose:
        print(f"DEBUG: {message}", file=sys.stderr)


def print_summary(metadata: Dict[str, Any], instruments: List[str], target_dir: str) -> None:
    """
    Print a summary of the generated kit.

    Args:
        metadata: Kit metadata
        instruments: List of instruments
        target_dir: Path to the target directory
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
    print(f"Website: \"{metadata.get('website', 'None')}\"", file=sys.stderr)
    print(f"Logo: \"{metadata.get('logo', 'None')}\"", file=sys.stderr)
