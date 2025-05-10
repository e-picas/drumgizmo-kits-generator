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
from typing import Any, List

from drumgizmo_kits_generator import constants
from drumgizmo_kits_generator.exceptions import AudioProcessingError, DependencyError


def check_dependency(command: str, error_message: str = None) -> str:
    """
    Check if a command is available in the system.

    Args:
        command: Command to check
        error_message: Custom error message (optional)

    Returns:
        str: The full path to the command if found

    Raises:
        DependencyError: If the command is not found
    """
    cmd_path = shutil.which(command)
    if not cmd_path:
        msg = error_message or f"Dependency '{command}' not found in the system"
        raise DependencyError(msg)
    return cmd_path


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


def split_comma_separated(
    value: Any, strip_items: bool = True, remove_empty: bool = True
) -> List[str]:
    """
    Split a comma-separated string into a list of strings.

    This function handles various input types and provides options for cleaning the result.
    It preserves commas inside quotes and handles both single and double quotes.

    Args:
        value: The value to split. Can be a string, list, or any other type.
               If the value is not a string or list, returns an empty list.
        strip_items: Whether to strip whitespace from each item.
        remove_empty: Whether to remove empty strings from the result.

    Returns:
        List[str]: A list of strings from the split operation, or empty list if input is not a string or list.

    Examples:
        >>> split_comma_separated("a, b, c")
        ['a', 'b', 'c']
        >>> split_comma_separated(["a", "b", "c"])
        ['a', 'b', 'c']
        >>> split_comma_separated("a,,b,\n  c")
        ['a', 'b', 'c']
        >>> split_comma_separated('a,"b,c",d')
        ['a', 'b,c', 'd']
        >>> split_comma_separated(None)
        []
        >>> split_comma_separated(123)
        []
    """
    # Handle None or empty values
    if value is None:
        return []

    # If value is already a list, return a copy with stripped items if needed
    if isinstance(value, list):
        result = list(value)
        if strip_items:
            result = [item.strip() if isinstance(item, str) else str(item) for item in result]
            result = [strip_quotes(item) for item in result]
        return [item for item in result if item] if remove_empty else result

    # If value is a string, process it
    if not isinstance(value, str):
        return []

    result = strip_quotes(value)
    result = result.split(",")

    # Clean up the result
    if strip_items:
        result = [item.strip() for item in result]
        result = [strip_quotes(item) for item in result]

    if remove_empty:
        result = [item for item in result if item]

    return result


def get_instrument_name(file_name: str) -> str:
    """
    Extract and clean the instrument name from a file name.
    Removes velocity prefix (e.g. '1-'), extension, and '_converted' suffix if present.

    Args:
        file_name: File name (with or without extension)

    Returns:
        str: Cleaned instrument name
    """
    base = os.path.basename(file_name)
    # Remove extension if present
    file_base, _ = os.path.splitext(base)
    # Remove velocity prefix (e.g., '1-')
    if file_base.startswith(tuple(f"{i}-" for i in range(1, 10))):
        parts = file_base.split("-", 1)
        if len(parts) > 1:
            instrument_name = parts[1]
        else:
            instrument_name = file_base
    else:
        instrument_name = file_base
    # Remove any '_converted' suffix
    instrument_name = instrument_name.replace("_converted", "")
    return instrument_name


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
        instrument_name = get_instrument_name(file_path)
        instrument_names.add(instrument_name)
    return sorted(list(instrument_names))


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
