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


def convert_sample_rate(file_path: str, target_sample_rate: str) -> str:
    """
    Convert the sample rate of an audio file.

    Args:
        file_path: Path to the audio file
        target_sample_rate: Target sample rate

    Returns:
        str: Path to the converted file
    """
    logger.debug(f"Converting {file_path} to {target_sample_rate} Hz")

    # Create a temporary directory for the converted audio
    temp_dir = tempfile.mkdtemp(prefix="drumgizmo_")

    # Get file name and extension
    file_name = os.path.basename(file_path)
    file_base, file_ext = os.path.splitext(file_name)

    # Create the converted file path in the temporary directory
    # Keep the original extension
    converted_file = os.path.join(temp_dir, f"{file_base}{file_ext}")

    # Use SoX to convert the sample rate
    try:
        if shutil.which("sox"):
            cmd = ["sox", file_path, "-r", str(target_sample_rate), converted_file]
            subprocess.run(cmd, check=True, capture_output=True)
            logger.debug(f"Converted sample rate to {target_sample_rate} Hz")
            return converted_file
        logger.error("SoX not found in the system, can not generate samples")
        return file_path
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to convert sample rate: {e}")
        # Clean up the temporary directory in case of error
        shutil.rmtree(temp_dir, ignore_errors=True)
        return file_path


def get_audio_info(file_path: str) -> Dict[str, Any]:
    """
    Get information about an audio file using SoX.

    Args:
        file_path: Path to the audio file

    Returns:
        Dict[str, Any]: Dictionary with audio information
    """
    info = {
        "channels": 2,  # Default to stereo
        "samplerate": 44100,  # Default to 44.1 kHz
        "bits": 16,  # Default to 16-bit
        "duration": 0,  # Default to 0 seconds
    }

    try:
        if shutil.which("soxi"):
            # Get number of channels
            cmd = ["soxi", "-c", file_path]
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            info["channels"] = int(result.stdout.strip())

            # Get sample rate
            cmd = ["soxi", "-r", file_path]
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            info["samplerate"] = int(result.stdout.strip())

            # Get bit depth
            cmd = ["soxi", "-b", file_path]
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            info["bits"] = int(result.stdout.strip())

            # Get duration in seconds
            cmd = ["soxi", "-D", file_path]
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            info["duration"] = float(result.stdout.strip())

            logger.debug(f"Audio info for {file_path}: {info}")
        else:
            logger.warning("soxi not found, using default audio information")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get audio information: {e}")

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
        List[str]: List of audio file paths
    """
    audio_files = []
    for root, _, files in os.walk(source_dir):
        for file in files:
            file_ext = os.path.splitext(file)[1].lower().lstrip(".")
            if file_ext in [ext.lower() for ext in extensions]:
                audio_files.append(os.path.join(root, file))

    return audio_files


def validate_directories(source_dir: str, target_dir: str, config_file: str = None) -> None:
    """
    Validate source and target directories, and config file if specified.

    Args:
        source_dir: Path to the source directory
        target_dir: Path to the target directory
        config_file: Path to the configuration file (optional)

    Raises:
        SystemExit: If validation fails
    """
    # Validate source directory
    if not os.path.isdir(source_dir):
        logger.error(f"Source directory does not exist: {source_dir}")

    # Validate target directory
    target_parent = os.path.dirname(os.path.abspath(target_dir))
    if not os.path.exists(target_dir) and not os.path.isdir(target_parent):
        logger.error(f"Parent directory of target does not exist: {target_parent}")

    # Validate config file if specified
    if config_file and config_file != constants.DEFAULT_CONFIG_FILE:
        if not os.path.isfile(config_file):
            logger.error(f"Configuration file does not exist: {config_file}")


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
