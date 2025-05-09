#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SPDX-License-Identifier: MIT
SPDX-PackageName: DrumGizmo kits generator
SPDX-PackageHomePage: https://github.com/e-picas/drumgizmo-kits-generator
SPDX-FileCopyrightText: 2025 Pierre Cassat (Picas)

DrumGizmo Kit Generator - Core logic module
"""

import os
import shutil
from typing import Any, Dict, List

from drumgizmo_kits_generator import audio, logger, utils, xml_generator
from drumgizmo_kits_generator.exceptions import (
    AudioProcessingError,
    DependencyError,
    DirectoryError,
    ValidationError,
    XMLGenerationError,
)


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
        logger.print_action_start(f"Creating target directory '{target_dir}'")
        os.makedirs(target_dir)
    else:
        # Clean directory if it exists
        logger.print_action_start(f"Cleaning target directory '{target_dir}'")
        for item in os.listdir(target_dir):
            item_path = os.path.join(target_dir, item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)

    logger.print_action_end()


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
    logger.info(f"Volume variations method: {metadata['variations_method']}")
    logger.info(f"MIDI note range: [{metadata['midi_note_min']}, {metadata['midi_note_max']}]")
    logger.info(f"MIDI note median: {metadata['midi_note_median']}")
    logger.info(f"Audio extensions: {metadata['extensions']}")
    logger.info(f"Audio channels: {metadata['channels']}")
    logger.info(f"Main channels: {metadata['main_channels']}")

    if metadata["extra_files"]:
        logger.info(f"Extra files: {metadata['extra_files']}")


def print_midi_mapping(audio_files: List[str], metadata: Dict[str, Any]) -> None:
    """
    Print the MIDI mapping for the given audio files and metadata.

    Args:
        audio_files: List of audio file paths
        metadata: Dictionary containing metadata for MIDI mapping
    """
    logger.info("\n=== MIDI Mapping Preview ===")
    midi_mapping = utils.evaluate_midi_mapping(audio_files, metadata)

    if not midi_mapping:
        logger.warning("No instruments found for MIDI mapping")
        return

    # Display MIDI mapping
    logger.info("MIDI mapping preview (alphabetical order):")
    for instrument, note in sorted(midi_mapping.items(), key=lambda x: x[0]):
        logger.info(f"- MIDI Note {note}: {instrument}")


def print_summary(
    target_dir: str,
    metadata: Dict[str, Any],
    processed_audio_files: Dict[str, List[str]],
    audio_files: List[str],
    generation_duration: float = None,
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

    if logger.is_raw_output():
        msg = f"Processing complete. DrumGizmo kit successfully created in {target_dir}"
    else:
        msg = f"Processing complete in {generation_duration:.2f} seconds. DrumGizmo kit successfully created in {target_dir}"
    logger.info(msg)
    logger.info(f"Number of instruments created: {len(processed_audio_files)}")
    logger.info("\nMain files:")
    logger.info(f"  - {os.path.join(target_dir, 'drumkit.xml')}")
    logger.info(f"  - {os.path.join(target_dir, 'midimap.xml')}")

    logger.info("\nKit metadata summary:")
    logger.info(f"  - Name: {metadata.get('name', '')}")
    logger.info(f"  - Version: {metadata.get('version', '')}")
    logger.info(f"  - Description: {metadata.get('description', '')}")
    logger.info(f"  - Notes: {metadata.get('notes', '')}")
    logger.info(f"  - Author: {metadata.get('author', '')}")
    logger.info(f"  - License: {metadata.get('license', '')}")
    logger.info(f"  - Sample rate: {metadata.get('samplerate', '')} Hz")
    logger.info(f"  - Website: {metadata.get('website', '')}")
    logger.info(f"  - Logo: {metadata.get('logo', '')}")

    logger.info("\nInstrument samples MIDI mapping:")

    # Get MIDI parameters
    midi_params = {
        "min": metadata.get("midi_note_min"),
        "max": metadata.get("midi_note_max"),
        "median": metadata.get("midi_note_median"),
    }

    # Get instrument names
    instruments = list(processed_audio_files.keys())

    # Calculate MIDI mapping
    midi_mapping = utils.calculate_midi_mapping(instruments, midi_params)

    # Display mapping with MIDI notes
    for instrument, audio_file in zip(processed_audio_files.keys(), audio_files):
        midi_note = midi_mapping.get(instrument, "N/A")
        logger.info(f"  - MIDI note {midi_note}: {instrument}: {os.path.basename(audio_file)}")

    extra_files = []
    if metadata.get("logo"):
        extra_files.append(metadata["logo"])
    if metadata.get("extra_files"):
        extra_files.extend(metadata["extra_files"])

    if extra_files:
        logger.info("\nExtra files copied:")
        for extra_file in extra_files:
            logger.info(f"  - {extra_file}")


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

    processed_audio_files = {}

    try:
        for file_path in audio_files:
            # Process the sample with sample rate conversion if needed
            processed_files = audio.process_sample(
                file_path, target_dir, metadata, audio_files[file_path]
            )

            # Get the instrument name from the first processed file
            if processed_files:
                instrument_name = os.path.basename(
                    os.path.dirname(os.path.dirname(processed_files[0]))
                )
                processed_audio_files[instrument_name] = processed_files

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

        logger.print_action_start("Generating 'drumkit.xml'")
        xml_generator.generate_drumkit_xml(target_dir, metadata)
        logger.print_action_end()

        logger.print_action_start("Generating instruments XML files")
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
                target_dir, instrument_name, metadata, instrument_files, audio_files
            )
        logger.print_action_end()

        logger.print_action_start("Generating 'midimap.xml'")
        xml_generator.generate_midimap_xml(target_dir, metadata)
        logger.print_action_end()
    except Exception as e:
        error_msg = f"Failed to generate XML files: {e}"
        raise XMLGenerationError(error_msg) from e


def scan_source_files(source_dir: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Scan source directory for audio files with extensions from metadata, with audio info for each audio file.

    Args:
        source_dir: Path to the source directory
        metadata: Metadata containing the list of extensions

    Returns:
        Dict[str, Any]: List of audio file paths, sorted alphabetically and audio infos: {file_path: audio_info}
    """
    logger.section("Scanning Source Directory")

    extensions = metadata["extensions"]
    logger.debug(
        f"Scanning source directory '{source_dir}' for audio files with extensions {extensions}"
    )
    audio_files = {}
    for root, _, files in os.walk(source_dir):
        for file in files:
            file_ext = os.path.splitext(file)[1].lower().lstrip(".")
            if file_ext in [ext.lower() for ext in extensions]:
                logger.debug(f"Found '{file}'")
                file_path = os.path.join(root, file)
                info = audio.get_audio_info(file_path)
                audio_files[file_path] = info

    # Sort audio files alphabetically by filename
    audio_files = dict(sorted(audio_files.items()))

    # Check if the number of files exceeds the MIDI note range
    midi_range = metadata["midi_note_max"] - metadata["midi_note_min"] + 1
    if len(audio_files) > midi_range:
        logger.warning(
            f"Number of audio files ({len(audio_files)}) exceeds MIDI note range "
            f"({metadata['midi_note_min']} - {metadata['midi_note_max']}, {midi_range} notes)"
        )

    # Print the list of audio files
    logger.info(f"Found {len(audio_files)} audio files:")
    for file, data in audio_files.items():
        logger.info(
            f"- {os.path.basename(file)} ({data['samplerate']} Hz - {data['channels']} channels)"
        )

    return audio_files


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
                logger.print_action_start(f"Copying logo file '{metadata['logo']}'")
                shutil.copy2(logo_path, target_dir)
                logger.print_action_end()
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
                    logger.print_action_start(f"Copying extra file '{extra_file}'")
                    shutil.copy2(extra_file_path, target_dir)
                    logger.print_action_end()
                else:
                    logger.warning(f"Extra file not found: {extra_file_path}")

    except Exception as e:
        error_msg = f"Failed to copy additional files: {e}"
        raise DirectoryError(error_msg) from e


def validate_directories(source_dir: str, target_dir: str) -> None:
    """
    Validate source and target directories.

    Args:
        source_dir: Path to source directory
        target_dir: Path to target directory

    Raises:
        ValidationError: If source directory doesn't exist
        ValidationError: If target's parent directory doesn't exist
    """
    # Check if source directory exists
    if not os.path.isdir(source_dir):
        raise ValidationError(f"Source directory '{source_dir}' does not exist")

    # Validate target directory
    target_parent = os.path.dirname(os.path.abspath(target_dir))
    if not os.path.exists(target_dir) and not os.path.isdir(target_parent):
        raise ValidationError(f"Parent directory of target '{target_parent}' does not exist")
