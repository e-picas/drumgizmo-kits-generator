#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DrumGizmo Kit Generator - Main module
"""

import os
import shutil
import traceback
from typing import Any, Dict, List

from drumgizmo_kits_generator import audio, cli, config, constants, logger, utils, validators
from drumgizmo_kits_generator.config import load_configuration
from drumgizmo_kits_generator.exceptions import (
    AudioProcessingError,
    DependencyError,
    DirectoryError,
    DrumGizmoError,
    XMLGenerationError,
)
from drumgizmo_kits_generator.xml_generator import (
    generate_drumkit_xml,
    generate_instrument_xml,
    generate_midimap_xml,
)


def process_audio_files(
    audio_files: List[str], target_dir: str, metadata: Dict[str, Any]
) -> Dict[str, List[str]]:
    """
    Process audio files by creating velocity variations.

    Args:
        audio_files: List of audio file paths
        target_dir: Path to the target directory
        metadata: Metadata for audio processing

    Returns:
        Dict[str, List[str]]: Dictionary mapping instrument names to processed audio files

    Raises:
        AudioProcessingError: If processing audio files fails
        DependencyError: If SoX is not found
    """
    logger.section("Processing Audio Files")

    # Verify SoX dependency before processing any files
    utils.check_dependency("sox", "SoX not found in the system, can not generate samples")

    processed_audio_files = {}
    velocity_levels = metadata.get("velocity_levels", constants.DEFAULT_VELOCITY_LEVELS)

    try:
        for file_path in audio_files:
            file_name = os.path.basename(file_path)
            logger.info(f"Processing {file_name}")

            # Get base name without extension
            # pylint: disable-next=unused-variable
            file_base, file_ext = os.path.splitext(file_name)

            # Clean up the instrument name
            instrument_name = utils.clean_instrument_name(file_base)

            # Create directory for the instrument
            instrument_dir = os.path.join(target_dir, instrument_name)
            samples_dir = os.path.join(instrument_dir, "samples")

            if not os.path.exists(instrument_dir):
                logger.info(f"Creating directory for instrument: {instrument_name}")
                os.makedirs(instrument_dir)
                os.makedirs(samples_dir)

            # Create velocity variations
            processed_files = audio.create_velocity_variations(
                file_path, samples_dir, velocity_levels, instrument_name
            )

            # Store processed files for this instrument
            processed_audio_files[instrument_name] = processed_files

            logger.info(f"Processed {file_name} with {velocity_levels} volume variations")

        return processed_audio_files
    except Exception as e:
        error_msg = f"Failed to process audio files: {e}"
        if not isinstance(e, (AudioProcessingError, DependencyError)):
            raise AudioProcessingError(error_msg) from e
        raise


def generate_xml_files(audio_files: List[str], target_dir: str, metadata: Dict[str, Any]) -> None:
    """
    Generate XML files for the DrumGizmo kit.

    Args:
        audio_files: List of audio file paths
        target_dir: Path to the target directory
        metadata: Metadata for XML generation

    Raises:
        XMLGenerationError: If generating XML files fails
    """
    logger.section("Generating XML Files")

    try:
        # Extract instrument names from audio files
        instrument_names = utils.extract_instrument_names(audio_files)

        # Add instrument names to metadata
        metadata["instruments"] = instrument_names

        logger.info("Generating drumkit.xml")
        generate_drumkit_xml(target_dir, metadata)

        logger.info("Generating instrument XML files")
        for instrument_name in instrument_names:
            instrument_files = []
            for f in audio_files:
                base_name = os.path.basename(f)
                # It could be with or without velocity prefix, and with or without "_converted" suffix
                if utils.is_instrument_file(base_name, instrument_name) or any(
                    base_name.startswith(f"{i}-")
                    and utils.is_instrument_file(base_name[len(f"{i}-") :], instrument_name)
                    for i in range(1, 10)
                ):
                    instrument_files.append(f)

            generate_instrument_xml(target_dir, instrument_name, metadata, instrument_files)

        logger.info("Generating midimap.xml")
        generate_midimap_xml(target_dir, metadata)
    except Exception as e:
        error_msg = f"Failed to generate XML files: {e}"
        raise XMLGenerationError(error_msg) from e


def copy_additional_files(source_dir: str, target_dir: str, metadata: Dict[str, Any]) -> None:
    """
    Copy logo and additional files to the target directory.

    Args:
        source_dir: Path to the source directory
        target_dir: Path to the target directory
        metadata: Metadata with logo and extra files information

    Raises:
        DirectoryError: If copying additional files fails
    """
    try:
        # Copy logo if specified
        if metadata["logo"]:
            logger.section("Copying Logo")
            logo_path = os.path.join(source_dir, metadata["logo"])
            if os.path.isfile(logo_path):
                logger.info(f"Copying logo: {metadata['logo']}")
                shutil.copy2(logo_path, target_dir)
            else:
                logger.warning(f"Logo file not found: {logo_path}")

        # Copy extra files if specified
        if metadata["extra_files"]:
            logger.section("Copying Additional Files")
            extra_files = metadata["extra_files"]
            # If extra_files is already a list, use it directly
            if not isinstance(extra_files, list):
                extra_files = extra_files.split(",")
            for extra_file in extra_files:
                extra_file = extra_file.strip()
                extra_file_path = os.path.join(source_dir, extra_file)
                if os.path.isfile(extra_file_path):
                    logger.info(f"Copying extra file: {extra_file}")
                    shutil.copy2(extra_file_path, target_dir)
                else:
                    logger.warning(f"Extra file not found: {extra_file_path}")
    except Exception as e:
        error_msg = f"Failed to copy additional files: {e}"
        raise DirectoryError(error_msg) from e


def main() -> None:
    """Main entry point for the DrumGizmo Kit Generator."""
    try:
        args = cli.parse_arguments()

        # Initialize logger with verbosity level
        logger.set_verbose(args.verbose)

        # Display application information in verbose mode
        logger.debug(f"{constants.APP_NAME} v{constants.APP_VERSION} - {constants.APP_LINK}")

        # Validate directories
        validators.validate_directories(args.source, args.target, args.dry_run)

        # Display processing directories
        logger.section("Processing Directories")
        logger.info(f"Source directory: {args.source}")
        logger.info(f"Target directory: {args.target}")

        # Load configuration (already transformed and validated)
        config_data = load_configuration(args)
        metadata = config.prepare_metadata(config_data)

        # Print metadata
        cli.print_metadata(metadata)

        # Scan source files
        extensions = metadata["extensions"]
        # If extensions is already a list, use it directly
        if isinstance(extensions, str):
            extensions = extensions.split(",")
        audio_files = utils.scan_source_files(args.source, extensions)

        # Print samples information
        cli.print_samples_info(audio_files, metadata)

        # Preview MIDI mapping in dry run mode
        if args.dry_run:
            cli.print_midi_mapping(audio_files, metadata)
            logger.message("\nDry run mode enabled, stopping here")
            return

        # Check SoX dependency before proceeding
        utils.check_dependency("sox", "SoX not found in the system, can not generate samples")

        # Prepare target directory
        utils.prepare_target_directory(args.target)

        # Process audio files
        processed_audio_files = process_audio_files(audio_files, args.target, metadata)

        # Generate XML files
        generate_xml_files(audio_files, args.target, metadata)

        # Copy additional files
        copy_additional_files(args.source, args.target, metadata)

        # Print summary
        cli.print_summary(args.target, metadata, processed_audio_files, audio_files)

        logger.message("\nKit generation completed successfully!")
    except DrumGizmoError as e:
        logger.error(f"Error: {e}")
    # pylint: disable=broad-exception-caught
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        if logger.is_verbose():
            logger.error(traceback.format_exc())


if __name__ == "__main__":
    main()
