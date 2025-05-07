#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SPDX-License-Identifier: MIT
SPDX-PackageName: DrumGizmo kits generator
SPDX-PackageHomePage: https://github.com/e-picas/drumgizmo-kits-generator
SPDX-FileCopyrightText: 2025 Pierre Cassat (Picas)

Utility module for DrumGizmo kit generator.
Contains various helper functions.
"""

import os
import shutil
import subprocess
import tempfile
from contextlib import contextmanager
from typing import Any, Dict, List

from drumgizmo_kits_generator import constants, logger
from drumgizmo_kits_generator.exceptions import AudioProcessingError, DependencyError


def check_dependency(command: str, error_message: str = None) -> None:
    """
    Check if a command is available in the system.

    Args:
        command: Command to check
        error_message: Custom error message (optional)

    Raises:
        DependencyError: If the command is not found
    """
    if not shutil.which(command):
        msg = error_message or f"Required dependency '{command}' not found in the system"
        raise DependencyError(msg)


def strip_quotes(value: str) -> str:
    """
    Strip quotes from a string value.

    Args:
        value: The string value to strip quotes from

    Returns:
        str: The value without quotes
    """
    if not isinstance(value, str):
        return value

    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    return value


def clean_instrument_name(file_base: str) -> str:
    """
    Clean up the instrument name by removing velocity prefixes and _converted suffixes.

    Args:
        file_base: Base name of the file (without extension)

    Returns:
        str: Cleaned instrument name
    """
    # Remove any existing velocity prefix (e.g., "1-", "2-")
    if file_base.startswith(tuple(f"{i}-" for i in range(1, 10))):
        # Remove velocity prefix
        instrument_name = file_base[2:]
    else:
        instrument_name = file_base

    # Remove any "_converted" suffixes
    instrument_name = instrument_name.replace("_converted", "")

    return instrument_name


def scan_source_files(source_dir: str, extensions: List[str]) -> List[str]:
    """
    Scan source directory for audio files with specified extensions.

    Args:
        source_dir: Path to the source directory
        extensions: List of file extensions to include

    Returns:
        List[str]: List of audio file paths, sorted alphabetically
    """
    audio_files = []
    for root, _, files in os.walk(source_dir):
        for file in files:
            file_ext = os.path.splitext(file)[1].lower().lstrip(".")
            if file_ext in [ext.lower() for ext in extensions]:
                audio_files.append(os.path.join(root, file))

    # Sort audio files alphabetically by filename
    audio_files.sort(key=lambda x: os.path.basename(x).lower())

    return audio_files


def prepare_target_directory(target_dir: str) -> None:
    """
    Prepare the target directory by creating it if it doesn't exist
    or cleaning it if it does.

    Args:
        target_dir: Path to the target directory
    """
    logger.section("Preparing Target Directory")

    # Create directory if it doesn't exist
    if not os.path.exists(target_dir):
        logger.info(f"Creating target directory: {target_dir}")
        os.makedirs(target_dir)
    else:
        # Clean directory if it exists
        logger.info(f"Cleaning target directory: {target_dir}")
        for item in os.listdir(target_dir):
            item_path = os.path.join(target_dir, item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)


def is_instrument_file(base_name: str, instrument_name: str, extensions: List[str] = None) -> bool:
    """
    Check if a file belongs to a specific instrument.

    Args:
        base_name: Base name of the file
        instrument_name: Name of the instrument
        extensions: List of valid extensions (optional)

    Returns:
        bool: True if the file belongs to the instrument, False otherwise
    """
    # If no extensions provided, use default extensions
    if extensions is None:
        extensions_str = constants.DEFAULT_EXTENSIONS
        extensions = [ext.strip() for ext in extensions_str.split(",")]

    # Process extensions to ensure they have a leading dot
    processed_exts = []
    for ext in extensions:
        ext = ext.lower()
        if not ext.startswith("."):
            ext = f".{ext}"
        processed_exts.append(ext)

    # Check for instrument match with any of the extensions
    for ext in processed_exts:
        # Check for direct instrument match
        if base_name.endswith(f"{instrument_name}{ext}"):
            return True
        # Check for converted instrument match
        if base_name.endswith(f"{instrument_name}_converted{ext}"):
            return True

    return False


def extract_instrument_names(audio_files: List[str]) -> List[str]:
    """
    Extract instrument names from audio files.

    Args:
        audio_files: List of audio file paths

    Returns:
        List[str]: List of instrument names sorted alphabetically
    """
    instrument_names = set()
    for file_path in audio_files:
        file_name = os.path.basename(file_path)
        # Extract the base instrument name without velocity prefix
        if file_name.startswith(tuple(f"{i}-" for i in range(1, 10))):
            # Remove the velocity prefix (e.g., "1-", "2-")
            parts = file_name.split("-", 1)
            if len(parts) > 1:
                instrument_name = parts[1].split(".")[0]  # Remove extension
                # Remove any "_converted" suffixes
                instrument_name = instrument_name.replace("_converted", "")
                instrument_names.add(instrument_name)
        else:
            # No velocity prefix
            file_base, _ = os.path.splitext(file_name)
            # Remove any "_converted" suffixes
            file_base = file_base.replace("_converted", "")
            instrument_names.add(file_base)

    # Convert to list for consistent ordering
    return sorted(list(instrument_names))


def calculate_midi_mapping(instruments: List[str], midi_params: Dict[str, int]) -> Dict[str, int]:
    """
    Calculate MIDI note mapping for a list of instruments.

    Args:
        instruments: List of instrument names
        midi_params: Dictionary with MIDI parameters (min, max, median)

    Returns:
        Dict[str, int]: Dictionary mapping instrument names to MIDI note numbers
    """
    # Use default values if parameters are None
    min_note = midi_params.get("min")
    if min_note is None:
        min_note = constants.DEFAULT_MIDI_NOTE_MIN

    max_note = midi_params.get("max")
    if max_note is None:
        max_note = constants.DEFAULT_MIDI_NOTE_MAX

    median_note = midi_params.get("median")
    if median_note is None:
        median_note = constants.DEFAULT_MIDI_NOTE_MEDIAN

    # Calculate how many instruments we have on each side of the median
    instruments_count = len(instruments)
    left_count = instruments_count // 2

    # Generate notes for each instrument
    midi_mapping = {}
    for i, instrument_name in enumerate(instruments):
        # Calculate note based on position
        if i < left_count:
            # Instruments to the left of median
            offset = left_count - i
            note = median_note - offset
        else:
            # Instruments to the right of median (including the middle one)
            offset = i - left_count
            note = median_note + offset

        # Ensure note is within the allowed range
        note = max(min_note, min(note, max_note))
        midi_mapping[instrument_name] = note

    return midi_mapping


def calculate_midi_note(
    i: int, left_count: int, midi_note_median: int, midi_note_min: int, midi_note_max: int
) -> int:
    """
    Calculate the MIDI note for an instrument based on its position.

    Args:
        i: Index of the instrument
        left_count: Number of instruments to the left of the median
        midi_note_median: Median MIDI note
        midi_note_min: Minimum MIDI note
        midi_note_max: Maximum MIDI note

    Returns:
        int: The calculated MIDI note
    """
    # Calculate note based on position relative to median
    if i < left_count:
        # Instruments to the left of median
        offset = left_count - i
        note = midi_note_median - offset
    else:
        # Instruments at or to the right of median
        offset = i - left_count
        note = midi_note_median + offset

    # Ensure note is within range
    return max(midi_note_min, min(note, midi_note_max))


def handle_subprocess_error(e: Exception, operation_name: str, from_exception: bool = True) -> None:
    """
    Handle errors from subprocess calls in a consistent way.

    Args:
        e: The caught exception
        operation_name: Name of the operation being performed
        from_exception: Whether to include the original exception in the raised exception

    Raises:
        AudioProcessingError: With appropriate error message

    Example:
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as e:
            handle_subprocess_error(e, "converting sample rate")
        except Exception as e:
            handle_subprocess_error(e, "converting sample rate", False)
    """
    if isinstance(e, subprocess.CalledProcessError):
        error_msg = f"Failed while {operation_name}: {e}"
        if hasattr(e, "stderr") and e.stderr:
            error_msg += f" (stderr: {e.stderr.strip()})"
        if from_exception:
            raise AudioProcessingError(error_msg) from e
        raise AudioProcessingError(error_msg)

    # For other types of exceptions
    error_msg = f"Unexpected error while {operation_name}: {e}"
    if from_exception:
        raise AudioProcessingError(error_msg) from e
    raise AudioProcessingError(error_msg)


@contextmanager
def temp_directory(prefix=None):
    """
    Context manager for temporary directory handling.

    Args:
        prefix: Prefix for the temporary directory (optional)

    Yields:
        str: Path to the temporary directory

    Example:
        with temp_directory() as temp_dir:
            # Do something with temp_dir
            ...
        # Directory is automatically cleaned up after the block
    """
    if prefix is None:
        prefix = constants.DEFAULT_TEMP_DIR_PREFIX

    temp_dir = tempfile.mkdtemp(prefix=prefix)
    try:
        yield temp_dir
    finally:
        if os.path.exists(temp_dir) and temp_dir.startswith(tempfile.gettempdir()):
            shutil.rmtree(temp_dir, ignore_errors=True)


# Path utilities
def get_filename(file_path: str) -> str:
    """
    Get the filename from a path.

    Args:
        file_path: Path to the file

    Returns:
        str: Filename without directory path
    """
    return os.path.basename(file_path)


def get_file_extension(file_path: str, with_dot: bool = False, lowercase: bool = True) -> str:
    """
    Get the file extension from a path.

    Args:
        file_path: Path to the file
        with_dot: Whether to include the dot in the extension
        lowercase: Whether to convert the extension to lowercase

    Returns:
        str: File extension
    """
    _, ext = os.path.splitext(file_path)
    if not with_dot:
        ext = ext.lstrip(".")
    if lowercase:
        ext = ext.lower()
    return ext


def get_file_basename(file_path: str) -> str:
    """
    Get the base filename without extension.

    Args:
        file_path: Path to the file

    Returns:
        str: Base filename without extension
    """
    filename = get_filename(file_path)
    basename, _ = os.path.splitext(filename)
    return basename


def join_paths(*paths: str) -> str:
    """
    Join path components intelligently.

    Args:
        *paths: Path components to join

    Returns:
        str: Joined path
    """
    return os.path.join(*paths)


def evaluate_midi_mapping(audio_files: List[str], metadata: Dict[str, Any]) -> Dict[str, int]:
    """
    Calculate MIDI mapping for given audio files based on metadata.

    Args:
        audio_files: List of audio file paths
        metadata: Dictionary containing MIDI note range information

    Returns:
        Dict[str, int]: Mapping of instrument names to MIDI note numbers
    """
    # Extract instrument names from audio files
    instrument_names = extract_instrument_names(audio_files)

    if not instrument_names:
        return {}

    # Get MIDI note range
    midi_params = {
        "min": metadata.get("midi_note_min"),
        "max": metadata.get("midi_note_max"),
        "median": metadata.get("midi_note_median"),
    }

    # Calculate MIDI mapping
    return calculate_midi_mapping(instrument_names, midi_params)
