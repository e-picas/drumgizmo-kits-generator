#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Command-line interface for the DrumGizmo Kit Generator.
"""

import argparse
import os
import sys
from typing import Any, Dict, List

from drumgizmo_kits_generator import constants, logger, utils


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


def print_midi_mapping(audio_files: List[str], metadata: Dict[str, Any]) -> None:
    """
    Print the MIDI mapping for the given audio files and metadata.

    Args:
        audio_files: List of audio file paths
        metadata: Dictionary containing metadata for MIDI mapping
    """
    logger.info("=== MIDI Mapping Preview ===")
    midi_mapping = utils.evaluate_midi_mapping(audio_files, metadata)

    if not midi_mapping:
        logger.warning("No instruments found for MIDI mapping")
        return

    # Display MIDI mapping
    logger.info("MIDI mapping preview (alphabetical order):")
    for instrument, note in sorted(midi_mapping.items(), key=lambda x: x[0]):
        logger.info(f"  MIDI Note {note}: {instrument}")


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
    logger.section("Generation Complete")

    # Basic information
    logger.info(f"Successfully generated DrumGizmo kit: {metadata['name']} v{metadata['version']}")
    logger.info(f"Location: {os.path.abspath(target_dir)}")

    # Sample statistics
    total_processed = sum(len(files) for files in processed_audio_files.values())
    logger.info(f"\nSamples processed: {total_processed} files")

    # List of generated instruments and their sample counts
    if processed_audio_files:
        logger.info("\nInstruments generated:")
        for instrument, files in processed_audio_files.items():
            logger.info(f"- {instrument}: {len(files)} samples")

    # Warnings if any
    midi_range = metadata["midi_note_max"] - metadata["midi_note_min"] + 1
    if len(audio_files) > midi_range:
        logger.warning(
            f"\nWarning: Number of audio files ({len(audio_files)}) exceeds MIDI note range "
            f"({metadata['midi_note_min']}-{metadata['midi_note_max']}, {midi_range} notes). "
            "Some samples may not be accessible."
        )

    # Next steps
    logger.info(
        "\nTo use this kit in DrumGizmo, copy it to your DrumGizmo kits directory "
        "and restart your DAW."
    )

    # Additional notes if any
    if metadata.get("notes"):
        logger.info(f"\nNotes: {metadata['notes']}")

    # Final message
    logger.info("\nDone!")


if __name__ == "__main__":
    parse_arguments()
