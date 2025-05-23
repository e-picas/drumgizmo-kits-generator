#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SPDX-License-Identifier: MIT
SPDX-PackageName: DrumGizmo kits generator
SPDX-PackageHomePage: https://github.com/e-picas/drumgizmo-kits-generator
SPDX-FileCopyrightText: 2025 Pierre Cassat (Picas)

Audio processing module for DrumGizmo kit generation.
"""

import math
import os
import shutil
import subprocess
import tempfile
from typing import Any, Dict, List

from drumgizmo_kits_generator import constants, logger, utils
from drumgizmo_kits_generator.exceptions import AudioProcessingError, DependencyError


def _cleanup_temp_files(output_file: str = None, temp_dir: str = None) -> None:
    """
    Clean up temporary files created during audio processing.

    Args:
        output_file: Path to the output file to delete
        temp_dir: Path to the temporary directory to delete
    """
    # Delete the output file if it exists
    if output_file and os.path.exists(output_file):
        try:
            os.remove(output_file)
            logger.log("INFO", f"Temporary file deleted: {output_file}")
        except OSError as e:
            logger.warning(f"Unable to delete temporary file {output_file}: {e}")

    # Delete the temporary directory if it exists
    if temp_dir and os.path.exists(temp_dir):
        try:
            os.rmdir(temp_dir)
            logger.log("INFO", f"Temporary directory deleted: {temp_dir}")
        except OSError as e:
            logger.warning(f"Unable to delete temporary directory {temp_dir}: {e}")


def convert_sample_rate(
    file_path: str,
    target_sample_rate: str,
    target_dir: str = None,
) -> str:
    """
    Convert the sample rate of an audio file.

    Args:
        file_path: Path to the audio file
        target_sample_rate: Target sample rate
        target_dir: Optional directory to copy the converted file to

    Returns:
        str: Path to the converted file (in target_dir if provided, otherwise in temp dir)

    Raises:
        DependencyError: If SoX is not found
        AudioProcessingError: If sample rate conversion fails
    """
    # Get file name components
    file_basename = utils.get_file_basename(file_path)
    file_extension = utils.get_file_extension(file_path, with_dot=True)

    logger.debug(f"Converting '{file_basename}{file_extension}' to {target_sample_rate} Hz")

    # Check if SoX is available and get its path
    sox_path = utils.check_dependency(
        "sox", "SoX not found in the system, can not generate samples"
    )

    # Define the output file name
    output_filename = f"{file_basename}{file_extension}"

    # If target_dir is provided, create it if it doesn't exist
    if target_dir:
        os.makedirs(target_dir, exist_ok=True)
        output_file = os.path.join(target_dir, output_filename)
    else:
        # Use a temporary directory if no target_dir is provided
        temp_dir = tempfile.mkdtemp(prefix=constants.DEFAULT_TEMP_DIR_PREFIX)
        output_file = os.path.join(temp_dir, output_filename)

    try:
        # Use SoX to convert the sample rate
        cmd = [
            sox_path,
            file_path,
            "-r",
            str(target_sample_rate),
            output_file,
        ]
        subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
        )

        # Return the path to the converted file
        return output_file

    except subprocess.CalledProcessError as e:
        # Cleanup temporary files
        _cleanup_temp_files(output_file, temp_dir if not target_dir else None)
        # Enhanced error context
        error_context = {
            "file": file_path,
            "target_samplerate": target_sample_rate,
            "exit_code": e.returncode,
            "stderr": e.stderr if hasattr(e, "stderr") else None,
        }
        raise AudioProcessingError(
            f"Failed to convert sample rate with SoX: {e}", error_context
        ) from e
    except FileNotFoundError as e:
        # Cleanup temporary files
        _cleanup_temp_files(output_file, temp_dir if not target_dir else None)
        # Enhanced error context
        error_context = {
            "file": e.filename if hasattr(e, "filename") else file_path,
            "target_samplerate": target_sample_rate,
        }
        raise AudioProcessingError(
            f"File not found during sample rate conversion: {e}", error_context
        ) from e
    except PermissionError as e:
        # Cleanup temporary files
        _cleanup_temp_files(output_file, temp_dir if not target_dir else None)
        # Enhanced error context
        error_context = {
            "file": e.filename if hasattr(e, "filename") else file_path,
            "target_samplerate": target_sample_rate,
        }
        raise AudioProcessingError(
            f"Permission error during sample rate conversion: {e}", error_context
        ) from e
    except OSError as e:
        # Cleanup temporary files
        _cleanup_temp_files(output_file, temp_dir if not target_dir else None)
        # Enhanced error context
        error_context = {
            "file": e.filename if hasattr(e, "filename") else file_path,
            "target_samplerate": target_sample_rate,
            "error_code": e.errno if hasattr(e, "errno") else None,
        }
        raise AudioProcessingError(
            f"System error during sample rate conversion: {e}", error_context
        ) from e
    except Exception as e:  # pylint: disable=broad-exception-caught
        # Cleanup temporary files
        _cleanup_temp_files(output_file, temp_dir if not target_dir else None)
        # Enhanced error context
        error_context = {
            "file": file_path,
            "target_samplerate": target_sample_rate,
            "exception_type": type(e).__name__,
        }
        raise AudioProcessingError(
            f"Unexpected error during sample rate conversion: {e}", error_context
        ) from e


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
    logger.debug(f"Getting audio information for '{file_path}'")

    # Check if the file exists
    if not os.path.isfile(file_path):
        raise AudioProcessingError(f"Audio file not found: {file_path}")

    # Check if soxi is available and get its path
    soxi_path = utils.check_dependency(
        "soxi", "soxi (part of SoX) not found in the system, can not get audio information"
    )

    # Initialize default info
    audio_info = {
        "channels": None,
        "samplerate": None,
        "bits": None,
        "duration": None,
    }

    try:
        # Get number of channels
        cmd = [soxi_path, "-c", file_path]
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
        )
        audio_info["channels"] = int(result.stdout.strip())

        # Get sample rate
        cmd = [soxi_path, "-r", file_path]
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
        )
        audio_info["samplerate"] = int(result.stdout.strip())

        # Get bit depth
        cmd = [soxi_path, "-b", file_path]
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
        )
        audio_info["bits"] = int(result.stdout.strip())

        # Get duration in seconds
        cmd = [soxi_path, "-D", file_path]
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
        )
        audio_info["duration"] = float(result.stdout.strip())

        logger.debug(f"Audio info for '{file_path}': {audio_info}")
    except subprocess.CalledProcessError as e:
        # Enhanced error context
        error_context = {
            "file": file_path,
            "command": e.cmd if hasattr(e, "cmd") else None,
            "exit_code": e.returncode,
            "stderr": e.stderr if hasattr(e, "stderr") else None,
        }
        raise AudioProcessingError(
            f"Failed to get audio information with SoX: {e}", error_context
        ) from e
    except ValueError as e:
        # Gestion spécifique des erreurs de conversion de valeurs
        error_context = {"file": file_path, "error_message": str(e)}
        raise AudioProcessingError(f"Unable to parse audio information: {e}", error_context) from e
    except FileNotFoundError as e:
        # Gestion spécifique des erreurs de fichier non trouvé
        error_context = {"file": e.filename if hasattr(e, "filename") else file_path}
        raise AudioProcessingError(f"Audio file not found: {e}", error_context) from e
    except PermissionError as e:
        # Gestion spécifique des erreurs de permission
        error_context = {"file": e.filename if hasattr(e, "filename") else file_path}
        raise AudioProcessingError(
            f"Permission error when accessing audio file: {e}", error_context
        ) from e
    except OSError as e:
        # Gestion spécifique des erreurs de système de fichiers
        error_context = {
            "file": e.filename if hasattr(e, "filename") else file_path,
            "error_code": e.errno if hasattr(e, "errno") else None,
        }
        raise AudioProcessingError(
            f"System error when accessing audio file: {e}", error_context
        ) from e
    except Exception as e:  # pylint: disable=broad-exception-caught
        # Capture other unexpected exceptions
        error_context = {"file": file_path, "exception_type": type(e).__name__}
        raise AudioProcessingError(
            f"Unexpected error when getting audio information: {e}", error_context
        ) from e

    return audio_info


# pylint: disable=too-many-locals
def process_sample(
    file_path: str,
    target_dir: str,
    metadata: Dict[str, Any],
    audio_info: dict = None,
) -> List[str]:
    """
    Process an audio sample: copy to target directory and create velocity variations.

    Args:
        file_path: Path to the audio file
        target_dir: Path to the target directory
        metadata: Metadata with processing parameters
        audio_info: Optional precomputed audio info dict (to avoid duplicate get_audio_info call)

    Returns:
        List[str]: List of paths to the created velocity variation files

    Raises:
        AudioProcessingError: If processing fails
        DependencyError: If SoX is not found
    """
    # Get file name and base name
    file_basename = utils.get_file_basename(file_path)

    # Clean up the instrument name
    instrument_name = utils.get_instrument_name(file_basename)

    velocity_levels = metadata.get("velocity_levels", constants.DEFAULT_VELOCITY_LEVELS)
    samplerate = metadata.get("samplerate", constants.DEFAULT_SAMPLERATE)

    logger.print_action_start(
        f"Processing '{utils.get_filename(file_path)}' with {velocity_levels} volume variations"
        f" at {samplerate} Hz"
    )

    # Create instrument directory
    instrument_dir = utils.join_paths(target_dir, instrument_name)
    samples_dir = utils.join_paths(instrument_dir, constants.DEFAULT_SAMPLES_DIR)
    logger.debug(f"Creating directory for instrument '{instrument_name}' at '{samples_dir}'")
    os.makedirs(samples_dir, exist_ok=True)

    try:
        requested_sr = str(samplerate)
        # Utiliser audio_info fourni ou get_audio_info
        try:
            if audio_info is None:
                audio_info = get_audio_info(file_path)
            input_sr = str(audio_info.get("samplerate"))
        # pylint: disable=broad-exception-caught
        except Exception:
            input_sr = None
        # Si le sample rate est connu et correct, pas de conversion
        if input_sr == requested_sr:
            file_to_process = file_path
            temp_dir = None
            logger.debug(f"Sample '{file_path}' already at {requested_sr} Hz, skipping conversion")
        else:
            temp_dir = tempfile.mkdtemp(prefix=constants.DEFAULT_TEMP_DIR_PREFIX)
            try:
                converted_file = convert_sample_rate(file_path, requested_sr, target_dir=temp_dir)
                file_to_process = converted_file
            # pylint: disable=broad-exception-caught
            except Exception:
                # Clean up temp dir if something goes wrong
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                raise

        try:
            # Create velocity variations
            variation_files = create_velocity_variations(
                file_to_process,
                samples_dir,
                velocity_levels,
                instrument_name,
                variations_method=metadata.get(
                    "variations_method", constants.DEFAULT_VARIATIONS_METHOD
                ),
            )
        finally:
            # Clean up the temporary file and directory if they exist
            if temp_dir and os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

        logger.print_action_end()
        return variation_files
    # pylint: disable=try-except-raise
    except (AudioProcessingError, DependencyError):
        # Re-raise the exception to be handled by the caller
        raise


def _calculate_linear_volume(level: int, total_levels: int) -> float:
    """
    Calculate the volume factor for a given velocity level using a linear scale.

    Args:
        level: Current velocity level (1-based)
        total_levels: Total number of velocity levels

    Returns:
        float: Volume factor between 0.0 and 1.0
    """
    if level == 1:
        return constants.DEFAULT_VELOCITY_VOLUME_MAX  # 100% volume for level 1

    # Linear decrease from MAX to MIN for velocity levels
    return constants.DEFAULT_VELOCITY_VOLUME_MAX - ((level - 1) / (total_levels - 1)) * (
        constants.DEFAULT_VELOCITY_VOLUME_MAX - constants.DEFAULT_VELOCITY_VOLUME_MIN
    )


def _calculate_logarithmic_volume(level: int, total_levels: int) -> float:
    """
    Calculate the volume factor for a given velocity level using a logarithmic scale.

    This creates a more natural-sounding volume curve where lower velocities
    have more variation in volume than higher velocities.

    Args:
        level: Current velocity level (1-based)
        total_levels: Total number of velocity levels

    Returns:
        float: Volume factor between 0.0 and 1.0
    """
    if level == 1:
        return constants.DEFAULT_VELOCITY_VOLUME_MAX  # 100% volume for level 1
    if level == total_levels:
        return constants.DEFAULT_VELOCITY_VOLUME_MIN  # MIN volume for last level

    # Calculate position in the range [0, 1] (inverted so higher levels = lower volume)
    position = 1.0 - ((level - 1) / (total_levels - 1))

    # Apply logarithmic scaling (base 10)
    # We map [0,1] to [1,10] to get a nice logarithmic curve
    log_value = math.log10(1 + (9 * position))

    # Scale to the desired range [MIN, MAX]
    return constants.DEFAULT_VELOCITY_VOLUME_MIN + (
        log_value * (constants.DEFAULT_VELOCITY_VOLUME_MAX - constants.DEFAULT_VELOCITY_VOLUME_MIN)
    )


def create_velocity_variation(
    file_path: str,
    target_file: str,
    volume_factor: float,
) -> None:
    """
    Create a single velocity variation with the specified volume factor.

    Args:
        file_path: Path to the source audio file
        target_file: Path where to save the velocity variation
        volume_factor: Volume factor (0.0 to 1.0)

    Raises:
        AudioProcessingError: If creating the variation fails
        DependencyError: If SoX is not found
    """
    # Check if source file exists
    if not os.path.exists(file_path):
        raise AudioProcessingError(f"Source file not found: {file_path}")

    # Check if SoX is available and get its path
    sox_path = utils.check_dependency(
        "sox", "SoX not found in the system, can not create velocity variations"
    )

    try:
        # Convert volume factor to dB
        db_adjustment = 20 * (volume_factor - 1)

        # Create a copy with adjusted volume using SoX
        cmd = [
            sox_path,
            file_path,
            target_file,
            "gain",
            f"{db_adjustment:.2f}",
        ]
        subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as e:
        raise AudioProcessingError(f"Error creating velocity variation: {e}") from e
    except Exception as e:  # pylint: disable=broad-exception-caught
        raise AudioProcessingError(f"Error creating velocity variation: {e}") from e


def create_velocity_variations(
    file_path: str,
    target_dir: str,
    velocity_levels: int,
    instrument_name: str,
    variations_method: str = "linear",
) -> Dict[str, str]:
    """
    Create velocity variations of an audio file.

    Args:
        file_path: Path to the audio file
        target_dir: Path to the target directory
        velocity_levels: Number of velocity levels to create
        instrument_name: Name of the instrument (used for file naming)
        variations_method: Type of volume curve to use ("linear" or "logarithmic")

    Returns:
        List[str]: List of paths to the created velocity variation files

    Raises:
        AudioProcessingError: If creating velocity variations fails
        DependencyError: If SoX is not found
        ValueError: If an invalid volume curve type is specified
    """
    logger.debug(
        f"Creating {velocity_levels} velocity variations for '{utils.get_filename(file_path)}' with {variations_method} curve"
    )

    # Check if source file exists
    if not os.path.exists(file_path):
        raise AudioProcessingError(f"Source file not found: {file_path}")

    # Get file extension
    file_ext = utils.get_file_extension(file_path, with_dot=True)

    # Select volume calculation function based on curve type
    if variations_method == "linear":
        calculate_volume = _calculate_linear_volume
    elif variations_method == "logarithmic":
        calculate_volume = _calculate_logarithmic_volume
    else:
        raise ValueError(f"Invalid variations method: {variations_method}")

    variation_files = {}
    for i in range(1, velocity_levels + 1):
        # Create a file name for this velocity level using the standard format
        velocity_file = utils.join_paths(
            target_dir,
            constants.DEFAULT_VELOCITY_FILENAME_FORMAT.format(
                level=i,
                instrument=instrument_name,
                ext=file_ext,
            ),
        )

        # Calculate volume factor for this level
        volume_factor = calculate_volume(i, velocity_levels)

        # Create the velocity variation
        logger.debug(
            f"Creating velocity variation {i}/{velocity_levels} at {volume_factor:.2f} volume"
        )
        create_velocity_variation(file_path, velocity_file, volume_factor)

        variation_files.update({velocity_file: {"volume": volume_factor}})

    return variation_files
