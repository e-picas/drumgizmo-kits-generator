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
            processed_files = audio.process_sample(file_path, target_dir, metadata)

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
                target_dir, instrument_name, metadata, instrument_files
            )
        logger.print_action_end()

        logger.print_action_start("Generating 'midimap.xml'")
        xml_generator.generate_midimap_xml(target_dir, metadata)
        logger.print_action_end()
    except Exception as e:
        error_msg = f"Failed to generate XML files: {e}"
        raise XMLGenerationError(error_msg) from e


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
