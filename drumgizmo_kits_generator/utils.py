#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utility module for DrumGizmo kit generator.
Contains various helper functions.
"""

import os
import shutil
import subprocess
import tempfile
from typing import Any, Dict, List

from drumgizmo_kits_generator import constants, logger
from drumgizmo_kits_generator.exceptions import (
    AudioProcessingError,
    DependencyError,
    DirectoryError,
)


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


def convert_sample_rate(file_path: str, target_sample_rate: str) -> str:
    """
    Convert the sample rate of an audio file.

    Args:
        file_path: Path to the audio file
        target_sample_rate: Target sample rate

    Returns:
        str: Path to the converted file

    Raises:
        DependencyError: If SoX is not found
        AudioProcessingError: If sample rate conversion fails
    """
    logger.debug(f"Converting {file_path} to {target_sample_rate} Hz")

    # Check if SoX is available
    if not shutil.which("sox"):
        error_msg = "SoX not found in the system, can not generate samples"
        raise DependencyError(error_msg)

    # Get file name and extension
    file_name = os.path.basename(file_path)
    file_base, file_ext = os.path.splitext(file_name)

    # Create a temporary directory for the converted audio
    temp_dir = tempfile.mkdtemp(prefix="drumgizmo_")
    converted_file = os.path.join(temp_dir, f"{file_base}{file_ext}")

    try:
        # Use SoX to convert the sample rate
        cmd = ["sox", file_path, "-r", str(target_sample_rate), converted_file]
        subprocess.run(cmd, check=True, capture_output=True, text=True)

        # Log success
        logger.debug(f"Successfully converted sample rate to {target_sample_rate} Hz")
        return converted_file
    except subprocess.CalledProcessError as e:
        error_msg = f"Failed to convert sample rate: {e}"
        if hasattr(e, "stderr") and e.stderr:
            error_msg += f" (stderr: {e.stderr.strip()})"
        # Clean up the temporary directory in case of error
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise AudioProcessingError(error_msg) from e
    except Exception as e:
        error_msg = f"Unexpected error during sample rate conversion: {e}"
        # Clean up the temporary directory in case of error
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise AudioProcessingError(error_msg) from e


def get_audio_info(file_path: str) -> Dict[str, Any]:
    """
    Get information about an audio file using SoX.

    Args:
        file_path: Path to the audio file

    Returns:
        Dict[str, Any]: Dictionary with audio information

    Raises:
        DependencyError: If SoX (soxi) is not found
        AudioProcessingError: If getting audio information fails
    """
    logger.debug(f"Getting audio information for {file_path}")

    # Check if the file exists
    if not os.path.isfile(file_path):
        raise AudioProcessingError(f"Audio file not found: {file_path}")

    # Check if soxi is available
    soxi_path = shutil.which("soxi")
    if not soxi_path:
        error_msg = "SoX (soxi) not found in the system, cannot get audio information"
        raise DependencyError(error_msg)

    # Initialize default info
    info = {
        "channels": None,
        "samplerate": None,
        "bits": None,
        "duration": None,
    }

    try:
        # Get number of channels
        cmd = [soxi_path, "-c", file_path]
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        info["channels"] = int(result.stdout.strip())

        # Get sample rate
        cmd = [soxi_path, "-r", file_path]
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        info["samplerate"] = int(result.stdout.strip())

        # Get bit depth
        cmd = [soxi_path, "-b", file_path]
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        info["bits"] = int(result.stdout.strip())

        # Get duration in seconds
        cmd = [soxi_path, "-D", file_path]
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        info["duration"] = float(result.stdout.strip())

        logger.debug(f"Audio info for {file_path}: {info}")
    except subprocess.CalledProcessError as e:
        error_msg = f"Failed to get audio information: {e}"
        if hasattr(e, "stderr") and e.stderr:
            error_msg += f" (stderr: {e.stderr.strip()})"
        raise AudioProcessingError(error_msg) from e
    except ValueError as e:
        error_msg = f"Failed to parse audio information: {e}"
        raise AudioProcessingError(error_msg) from e
    except Exception as e:
        error_msg = f"Unexpected error while getting audio information: {e}"
        raise AudioProcessingError(error_msg) from e

    return info


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


def validate_directories(source_dir: str, target_dir: str, config_file: str = None) -> None:
    """
    Validate source and target directories, and config file if specified.

    Args:
        source_dir: Path to the source directory
        target_dir: Path to the target directory
        config_file: Path to the configuration file (optional)

    Raises:
        DirectoryError: If validation fails
    """
    # Validate source directory
    if not os.path.isdir(source_dir):
        raise DirectoryError(f"Source directory does not exist: {source_dir}")

    # Validate target directory
    target_parent = os.path.dirname(os.path.abspath(target_dir))
    if not os.path.exists(target_dir) and not os.path.isdir(target_parent):
        raise DirectoryError(f"Parent directory of target does not exist: {target_parent}")

    # Validate config file if specified
    if config_file and config_file != constants.DEFAULT_CONFIG_FILE:
        if not os.path.isfile(config_file):
            raise DirectoryError(f"Configuration file does not exist: {config_file}")


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


def is_instrument_file(base_name: str, instrument_name: str) -> bool:
    """
    Check if a file belongs to a specific instrument.

    Args:
        base_name: Base name of the file
        instrument_name: Name of the instrument

    Returns:
        bool: True if the file belongs to the instrument, False otherwise
    """
    # Check for common audio file extensions
    for ext in [".wav", ".flac", ".ogg"]:
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
        Dict[str, int]: Dictionary mapping instrument names to MIDI notes
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
