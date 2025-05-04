#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main script for DrumGizmo kit generation.
Uses all other modules to create a complete kit.
"""

import argparse
import os
import shutil
import sys
from typing import Any, Dict, List

from drumgizmo_kits_generator import (
    audio,
    config,
    constants,
    logger,
    transformers,
    utils,
    validators,
    xml_generator,
)


def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments.

    Returns:
        argparse.Namespace: Parsed command line arguments
    """
    # Create a parent parser for version display
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument(
        "-V",
        "--app-version",
        action="store_true",
        help="Show the application version number and exit",
    )

    # Check if --app-version is in sys.argv
    args, _ = parent_parser.parse_known_args()
    if args.app_version:
        print(f"{constants.APP_NAME} v{constants.APP_VERSION}")
        sys.exit(0)

    # Main parser for all other arguments
    parser = argparse.ArgumentParser(
        description="Create a DrumGizmo kit from a set of audio samples",
        epilog=f"For more information, visit the project homepage: {constants.APP_LINK}",
    )

    # Required arguments
    parser.add_argument(
        "-s", "--source", required=True, help="Source directory containing audio samples"
    )
    parser.add_argument(
        "-t", "--target", required=True, help="Target directory for the generated kit"
    )

    # Optional arguments
    parser.add_argument(
        "-c",
        "--config",
        default=constants.DEFAULT_CONFIG_FILE,
        help=f"Configuration file (default: `{constants.DEFAULT_CONFIG_FILE}`)",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument(
        "-x", "--dry-run", action="store_true", help="Dry run mode (no files will be created)"
    )
    parser.add_argument(
        "-V",
        "--app-version",
        action="store_true",
        help="Show the application version number and exit",
    )

    # Kit configuration options
    parser.add_argument("--name", help=f"Kit name (default: `{constants.DEFAULT_NAME}`)")
    parser.add_argument("--version", help=f"Kit version (default: `{constants.DEFAULT_VERSION}`)")
    parser.add_argument("--description", help="Kit description")
    parser.add_argument("--notes", help="Additional notes about the kit")
    parser.add_argument("--author", help="Kit author")
    parser.add_argument("--license", help=f"Kit license (default: `{constants.DEFAULT_LICENSE}`)")
    parser.add_argument("--website", help="Kit website")
    parser.add_argument("--logo", help="Kit logo filename")
    parser.add_argument(
        "--samplerate", help=f"Sample rate in Hz (default: `{constants.DEFAULT_SAMPLERATE}`)"
    )
    parser.add_argument("--extra-files", help="Additional files to copy, comma-separated")
    parser.add_argument(
        "--velocity-levels",
        help=f"Number of velocity levels to generate (default: `{constants.DEFAULT_VELOCITY_LEVELS}`)",
    )
    parser.add_argument(
        "--midi-note-min",
        help=f"Minimum MIDI note number allowed (default: `{constants.DEFAULT_MIDI_NOTE_MIN}`)",
    )
    parser.add_argument(
        "--midi-note-max",
        help=f"Maximum MIDI note number allowed (default: `{constants.DEFAULT_MIDI_NOTE_MAX}`)",
    )
    parser.add_argument(
        "--midi-note-median",
        help=f"Median MIDI note for distributing instruments (default: `{constants.DEFAULT_MIDI_NOTE_MEDIAN}`)",
    )
    parser.add_argument(
        "--extensions",
        help=f"Audio file extensions to process, comma-separated (default: `{constants.DEFAULT_EXTENSIONS}`)",
    )
    parser.add_argument(
        "--channels",
        help=f"Audio channels to use, comma-separated (default: `{constants.DEFAULT_CHANNELS}`)",
    )
    parser.add_argument(
        "--main-channels",
        help=f"Main audio channels, comma-separated (default: `{constants.DEFAULT_MAIN_CHANNELS}`)",
    )

    return parser.parse_args()


def load_configuration(args: argparse.Namespace) -> Dict[str, Any]:
    """
    Load configuration from defaults, config file, and command line arguments.

    Args:
        args: Parsed command line arguments

    Returns:
        Dict[str, Any]: Aggregated configuration
    """
    # Start with default configuration
    config_data = {
        "source": args.source,
        "target": args.target,
        "verbose": args.verbose,
        "dry_run": args.dry_run,
        "name": constants.DEFAULT_NAME,
        "version": constants.DEFAULT_VERSION,
        "license": constants.DEFAULT_LICENSE,
        "samplerate": constants.DEFAULT_SAMPLERATE,
        "extensions": constants.DEFAULT_EXTENSIONS,
        "velocity_levels": constants.DEFAULT_VELOCITY_LEVELS,
        "midi_note_min": constants.DEFAULT_MIDI_NOTE_MIN,
        "midi_note_max": constants.DEFAULT_MIDI_NOTE_MAX,
        "midi_note_median": constants.DEFAULT_MIDI_NOTE_MEDIAN,
        "channels": constants.DEFAULT_CHANNELS,
        "main_channels": constants.DEFAULT_MAIN_CHANNELS,
        "description": None,
        "notes": None,
        "author": None,
        "website": None,
        "logo": None,
        "extra_files": None,
    }

    # Load configuration from file if it exists
    config_file = args.config
    if os.path.isfile(os.path.join(args.source, config_file)):
        config_file = os.path.join(args.source, config_file)
        logger.info(f"Using configuration file: {config_file}")
        file_config = config.load_config_file(config_file)
        config_data.update(file_config)
    elif os.path.isfile(config_file):
        logger.info(f"Using configuration file: {config_file}")
        file_config = config.load_config_file(config_file)
        config_data.update(file_config)
    elif config_file != constants.DEFAULT_CONFIG_FILE:
        # Only show warning if a non-default config file was specified but not found
        logger.warning(f"Configuration file not found: {config_file}")

    # Override with command line arguments
    cli_config = {}
    for key in [
        "name",
        "version",
        "description",
        "notes",
        "author",
        "license",
        "website",
        "logo",
        "samplerate",
        "extra_files",
        "velocity_levels",
        "midi_note_min",
        "midi_note_max",
        "midi_note_median",
        "extensions",
        "channels",
        "main_channels",
    ]:
        cli_value = getattr(args, key, None)
        if cli_value is not None:
            cli_config[key] = cli_value

    config_data.update(cli_config)

    return config_data


def transform_configuration(config_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform configuration values to appropriate types.

    Args:
        config_data: Raw configuration data

    Returns:
        Dict[str, Any]: Transformed configuration data
    """
    transformed_config = config_data.copy()

    # Apply transformers for each configuration entry
    for key in transformed_config:
        transformer_name = f"transform_{key}"
        if hasattr(transformers, transformer_name):
            transformer = getattr(transformers, transformer_name)
            transformed_config[key] = transformer(transformed_config[key])

    return transformed_config


def validate_configuration(config_data: Dict[str, Any]) -> None:
    """
    Validate configuration values.

    Args:
        config_data: Configuration data to validate

    Raises:
        SystemExit: If validation fails
    """
    # Apply validators for each configuration entry
    for key in config_data:
        validator_name = f"validate_{key}"
        if hasattr(validators, validator_name):
            validator = getattr(validators, validator_name)
            validator(config_data[key], config_data)


def prepare_metadata(config_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prepare metadata for kit generation.

    Args:
        config_data: Validated configuration data

    Returns:
        Dict[str, Any]: Metadata for kit generation
    """
    metadata = config_data.copy()

    # Convert string values to appropriate types
    if isinstance(metadata["velocity_levels"], str):
        metadata["velocity_levels"] = int(metadata["velocity_levels"])

    if isinstance(metadata["midi_note_min"], str):
        metadata["midi_note_min"] = int(metadata["midi_note_min"])

    if isinstance(metadata["midi_note_max"], str):
        metadata["midi_note_max"] = int(metadata["midi_note_max"])

    if isinstance(metadata["midi_note_median"], str):
        metadata["midi_note_median"] = int(metadata["midi_note_median"])

    if isinstance(metadata["samplerate"], str):
        metadata["samplerate"] = int(metadata["samplerate"])

    return metadata


def print_metadata(metadata: Dict[str, Any]) -> None:
    """
    Print metadata information.

    Args:
        metadata: Metadata to print
    """
    logger.section("Kit Metadata")

    logger.info(f"Name: {metadata['name']}")
    logger.info(f"Version: {metadata['version']}")

    if metadata["description"]:
        logger.info(f"Description: {metadata['description']}")

    if metadata["notes"]:
        logger.info(f"Notes: {metadata['notes']}")

    if metadata["author"]:
        logger.info(f"Author: {metadata['author']}")

    logger.info(f"License: {metadata['license']}")

    if metadata["website"]:
        logger.info(f"Website: {metadata['website']}")

    if metadata["logo"]:
        logger.info(f"Logo: {metadata['logo']}")

    logger.info(f"Sample rate: {metadata['samplerate']} Hz")
    logger.info(f"Velocity levels: {metadata['velocity_levels']}")
    logger.info(f"MIDI note range: [{metadata['midi_note_min']}, {metadata['midi_note_max']}]")
    logger.info(f"MIDI note median: {metadata['midi_note_median']}")
    logger.info(f"Audio extensions: {metadata['extensions']}")
    logger.info(f"Audio channels: {metadata['channels']}")
    logger.info(f"Main channels: {metadata['main_channels']}")

    if metadata["extra_files"]:
        logger.info(f"Extra files: {metadata['extra_files']}")


def print_samples_info(audio_files: List[str], metadata: Dict[str, Any]) -> None:
    """
    Print information about the source audio samples.

    Args:
        audio_files: List of audio file paths
        metadata: Metadata with MIDI note range
    """
    logger.section("Source Audio Samples")

    logger.info(f"Found {len(audio_files)} audio files:")

    # Check if the number of files exceeds the MIDI note range
    midi_range = metadata["midi_note_max"] - metadata["midi_note_min"] + 1
    if len(audio_files) > midi_range:
        logger.warning(
            f"Number of audio files ({len(audio_files)}) exceeds MIDI note range "
            f"({metadata['midi_note_min']} - {metadata['midi_note_max']}, {midi_range} notes)"
        )

    # Print the list of audio files
    for file in audio_files:
        logger.info(f"- {os.path.basename(file)}")


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
    """
    logger.section("Processing Audio Files")

    processed_audio_files = {}
    velocity_levels = metadata.get("velocity_levels", constants.DEFAULT_VELOCITY_LEVELS)

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


def preview_midi_mapping(audio_files: List[str], metadata: Dict[str, Any]) -> None:
    """
    Preview MIDI mapping without generating files.
    For dry-run mode only.

    Args:
        audio_files: List of audio file paths
        metadata: Metadata for MIDI mapping
    """
    logger.section("MIDI Mapping Preview")

    # Extract instrument names from audio files
    instrument_names = utils.extract_instrument_names(audio_files)

    # Get MIDI note range
    midi_params = {
        "min": metadata.get("midi_note_min"),
        "max": metadata.get("midi_note_max"),
        "median": metadata.get("midi_note_median"),
    }

    if not instrument_names:
        logger.warning("No instruments found for MIDI mapping preview")
        return

    # Calculate MIDI mapping
    midi_mapping = utils.calculate_midi_mapping(instrument_names, midi_params)

    # Display MIDI mapping
    logger.info("MIDI mapping preview (alphabetical order):")
    for instrument, note in sorted(midi_mapping.items(), key=lambda x: x[0]):
        logger.info(f"  MIDI Note {note}: {instrument}")


def generate_xml_files(audio_files: List[str], target_dir: str, metadata: Dict[str, Any]) -> None:
    """
    Generate XML files for the DrumGizmo kit.

    Args:
        audio_files: List of audio file paths
        target_dir: Path to the target directory
        metadata: Metadata for XML generation
    """
    logger.section("Generating XML Files")

    # Extract instrument names from audio files
    instrument_names = utils.extract_instrument_names(audio_files)

    # Add instrument names to metadata
    metadata["instruments"] = instrument_names

    logger.info("Generating drumkit.xml")
    xml_generator.generate_drumkit_xml(target_dir, metadata)

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

        xml_generator.generate_instrument_xml(
            target_dir, instrument_name, metadata, instrument_files
        )

    logger.info("Generating midimap.xml")
    xml_generator.generate_midimap_xml(target_dir, metadata)


def copy_additional_files(source_dir: str, target_dir: str, metadata: Dict[str, Any]) -> None:
    """
    Copy logo and additional files to the target directory.

    Args:
        source_dir: Path to the source directory
        target_dir: Path to the target directory
        metadata: Metadata with logo and extra files information
    """
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


def print_summary(
    target_dir: str,
    metadata: Dict[str, Any],
    processed_audio_files: Dict[str, List[str]],
    audio_files: List[str],
) -> None:
    """
    Print a summary of the generated kit.

    Args:
        target_dir: The target directory where the kit was generated
        metadata: The metadata of the kit
        processed_audio_files: The processed audio files
        audio_files: The original audio files
    """
    logger.section("Summary")

    logger.info(f"Processing complete. DrumGizmo kit successfully created in: {target_dir}")
    logger.info(f"Number of instruments created: {len(processed_audio_files)}")
    logger.info("Main files:")
    logger.info(f"- {os.path.join(target_dir, 'drumkit.xml')}")
    logger.info(f"- {os.path.join(target_dir, 'midimap.xml')}")

    logger.info("\nKit metadata summary:")
    logger.info(f"Name: {metadata.get('name', '')}")
    logger.info(f"Version: {metadata.get('version', '')}")
    logger.info(f"Description: {metadata.get('description', '')}")
    logger.info(f"Notes: {metadata.get('notes', '')}")
    logger.info(f"Author: {metadata.get('author', '')}")
    logger.info(f"License: {metadata.get('license', '')}")
    logger.info(f"Sample rate: {metadata.get('samplerate', '')} Hz")
    logger.info(f"Website: {metadata.get('website', '')}")
    logger.info(f"Logo: {metadata.get('logo', '')}")

    logger.info("\nInstrument to sample mapping:")
    if isinstance(processed_audio_files, dict):
        # If processed_audio_files is a dictionary (new format)

        # Get MIDI parameters
        midi_params = {
            "min": metadata.get("midi_note_min", constants.DEFAULT_MIDI_NOTE_MIN),
            "max": metadata.get("midi_note_max", constants.DEFAULT_MIDI_NOTE_MAX),
            "median": metadata.get("midi_note_median", constants.DEFAULT_MIDI_NOTE_MEDIAN),
        }

        # Get instrument names
        instruments = list(processed_audio_files.keys())

        # Calculate MIDI mapping
        midi_mapping = utils.calculate_midi_mapping(instruments, midi_params)

        # Display mapping with MIDI notes
        for instrument, audio_file in zip(processed_audio_files.keys(), audio_files):
            midi_note = midi_mapping.get(instrument, "N/A")
            logger.info(f"  (MIDI Note {midi_note}) {instrument}: {os.path.basename(audio_file)}")
    else:
        # If processed_audio_files is a list (old format used in tests)
        for audio_file in audio_files:
            instrument_name = os.path.basename(audio_file)
            logger.info(f"  {instrument_name}: {instrument_name}")

    extra_files = []
    if metadata.get("logo"):
        extra_files.append(metadata["logo"])
    if metadata.get("extra_files"):
        extra_files.extend(metadata["extra_files"])

    if extra_files:
        logger.info("\nExtra files copied:")
        for extra_file in extra_files:
            logger.info(f"  {extra_file}")


def main() -> None:
    """
    Main function for DrumGizmo kit generation.
    """
    # Parse command line arguments
    args = parse_arguments()

    # Set verbose mode
    logger.set_verbose(args.verbose)

    # Display application information in verbose mode
    logger.debug(f"{constants.APP_NAME} v{constants.APP_VERSION} - {constants.APP_LINK}")

    # Validate directories
    utils.validate_directories(args.source, args.target, args.config)

    # Display processing directories
    logger.section("Processing Directories")
    logger.info(f"Source directory: {args.source}")
    logger.info(f"Target directory: {args.target}")

    # Load and process configuration
    config_data = load_configuration(args)
    transformed_config = transform_configuration(config_data)
    validate_configuration(transformed_config)
    metadata = prepare_metadata(transformed_config)

    # Print metadata
    print_metadata(metadata)

    # Scan source files
    extensions = metadata["extensions"]
    # If extensions is already a list, use it directly
    if not isinstance(extensions, list):
        extensions = extensions.split(",")
    audio_files = utils.scan_source_files(args.source, extensions)

    # Print samples information
    print_samples_info(audio_files, metadata)

    # Preview MIDI mapping in dry run mode
    if args.dry_run:
        preview_midi_mapping(audio_files, metadata)
        logger.message("\nDry run mode enabled, stopping here")
        return

    # Prepare target directory
    utils.prepare_target_directory(args.target)

    # Process audio files
    processed_audio_files = process_audio_files(audio_files, args.target, metadata)

    # Generate XML files
    generate_xml_files(audio_files, args.target, metadata)

    # Copy additional files
    copy_additional_files(args.source, args.target, metadata)

    # Print summary
    print_summary(args.target, metadata, processed_audio_files, audio_files)

    logger.message("\nKit generation completed successfully!")


if __name__ == "__main__":
    main()
