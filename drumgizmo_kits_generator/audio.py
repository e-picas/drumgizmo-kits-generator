#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Audio processing module for DrumGizmo kit generator.
Contains functions for processing audio files.
"""

import os
import shutil
import subprocess
import tempfile
from typing import Any, Dict, List

from drumgizmo_kits_generator import constants, logger, utils


def process_sample(file_path: str, target_dir: str, metadata: Dict[str, Any]) -> List[str]:
    """
    Process an audio sample: copy to target directory and create velocity variations.

    Args:
        file_path: Path to the audio file
        target_dir: Path to the target directory
        metadata: Metadata with processing parameters

    Returns:
        List[str]: List of paths to the created velocity variation files
    """
    # Get file name and extension
    file_name = os.path.basename(file_path)
    file_base, _ = os.path.splitext(file_name)

    # Clean up the instrument name
    instrument_name = utils.clean_instrument_name(file_base)

    # Create instrument directory
    instrument_dir = os.path.join(target_dir, instrument_name)
    samples_dir = os.path.join(instrument_dir, "samples")
    os.makedirs(samples_dir, exist_ok=True)
    logger.info(f"Creating directory for instrument: {instrument_name}")

    # Convert sample rate if needed
    temp_dirs = []  # Track temporary directories to clean up later
    try:
        if "samplerate" in metadata and metadata["samplerate"]:
            converted_file = utils.convert_sample_rate(file_path, metadata["samplerate"])
            # If the file was converted, track the temp directory
            if converted_file != file_path:
                temp_dirs.append(os.path.dirname(converted_file))
        else:
            converted_file = file_path

        # Create velocity variations
        velocity_levels = metadata.get("velocity_levels", constants.DEFAULT_VELOCITY_LEVELS)
        variation_files = create_velocity_variations(
            converted_file, samples_dir, velocity_levels, instrument_name
        )

        # Log success
        logger.info(f"Processed {file_name} with {velocity_levels} volume variations")

        return variation_files
    finally:
        # Clean up temporary directories
        for temp_dir in temp_dirs:
            if os.path.exists(temp_dir) and temp_dir.startswith(tempfile.gettempdir()):
                shutil.rmtree(temp_dir, ignore_errors=True)


def create_velocity_variations(
    file_path: str, target_dir: str, velocity_levels: int, instrument_name: str
) -> List[str]:
    """
    Create velocity variations of an audio file.

    Args:
        file_path: Path to the audio file
        target_dir: Path to the target directory
        velocity_levels: Number of velocity levels to create
        instrument_name: Name of the instrument (used for file naming)

    Returns:
        List[str]: List of paths to the created velocity variation files
    """
    logger.debug(f"Creating {velocity_levels} velocity variations for {file_path}")

    # Get file extension
    _, file_ext = os.path.splitext(file_path)

    variation_files = []
    for i in range(1, velocity_levels + 1):
        # Create a file name for this velocity level
        velocity_file = os.path.join(target_dir, f"{i}-{instrument_name}{file_ext}")

        # Calculate volume adjustment based on velocity level
        # Level 1 = 100% volume (0 dB)
        # Other levels decrease in volume
        if i == 1:
            volume_factor = 1.0  # 100% volume
        else:
            # Linear decrease from 1.0 to 0.25 for velocity levels
            volume_factor = 1.0 - ((i - 1) / (velocity_levels - 1)) * 0.75

        # Use SoX to adjust volume and save to the new file
        try:
            if os.path.exists(file_path):
                # If SoX is available, use it to adjust volume
                if shutil.which("sox"):
                    # Convert volume factor to dB
                    db_adjustment = 20 * (volume_factor - 1)

                    # Create a copy with adjusted volume
                    cmd = ["sox", file_path, velocity_file, "gain", f"{db_adjustment:.2f}"]
                    subprocess.run(cmd, check=True, capture_output=True)
                else:
                    # If SoX is not available, just copy the file
                    logger.warning("SoX not found, copying file without volume adjustment")
                    shutil.copy2(file_path, velocity_file)

                variation_files.append(velocity_file)
                logger.debug(
                    f"Created velocity variation {i}/{velocity_levels} at {volume_factor:.2f} volume"
                )
            else:
                logger.error(f"Source file not found: {file_path}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create velocity variation: {e}")
            # Fall back to copying the file
            shutil.copy2(file_path, velocity_file)
            variation_files.append(velocity_file)

    return variation_files
