#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SPDX-License-Identifier: MIT
SPDX-PackageName: DrumGizmo kits generator
SPDX-PackageHomePage: https://github.com/e-picas/drumgizmo-kits-generator
SPDX-FileCopyrightText: 2025 Pierre Cassat (Picas)

DrumGizmo Kit Generator - Core logic module

All functions of this module are expected to be called from the main module.
All functions are expected to treat a `RunData` object and modify it.
"""

import os
import shutil
from typing import Dict, List

from drumgizmo_kits_generator import audio, constants, logger, utils, xml_generator
from drumgizmo_kits_generator.exceptions import (
    AudioProcessingError,
    DependencyError,
    DirectoryError,
    ValidationError,
    XMLGenerationError,
)
from drumgizmo_kits_generator.state import RunData


def prepare_target_directory(run_data: RunData) -> None:
    """
    Prepare the target directory by creating it if it doesn't exist
    or cleaning it if it does.

    Args:
        run_data: RunData
    """
    logger.section("Preparing Target Directory")

    # Create directory if it doesn't exist
    if not os.path.exists(run_data.target_dir):
        logger.print_action_start(f"Creating target directory '{run_data.target_dir}'")
        os.makedirs(run_data.target_dir)
    else:
        # Clean directory if it exists
        logger.print_action_start(f"Cleaning target directory '{run_data.target_dir}'")
        for item in os.listdir(run_data.target_dir):
            item_path = os.path.join(run_data.target_dir, item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)

    logger.print_action_end()


def print_metadata(run_data: RunData) -> None:
    """
    Print metadata information.

    Args:
        run_data: RunData
    """
    logger.section("Kit Metadata")

    logger.info(f"Name: {run_data.config['name']}")
    logger.info(f"Version: {run_data.config['version']}")

    if run_data.config["description"]:
        logger.info(f"Description: {run_data.config['description']}")

    if run_data.config["notes"]:
        logger.info(f"Notes: {run_data.config['notes']}")

    if run_data.config["author"]:
        logger.info(f"Author: {run_data.config['author']}")

    logger.info(f"License: {run_data.config['license']}")

    if run_data.config["website"]:
        logger.info(f"Website: {run_data.config['website']}")

    if run_data.config["logo"]:
        logger.info(f"Logo: {run_data.config['logo']}")

    logger.info(f"Sample rate: {run_data.config['samplerate']} Hz")
    logger.info(f"Velocity levels: {run_data.config['velocity_levels']}")
    logger.info(f"Volume variations method: {run_data.config['variations_method']}")
    logger.info(
        f"MIDI note range: [{run_data.config['midi_note_min']}, {run_data.config['midi_note_max']}]"
    )
    logger.info(f"MIDI note median: {run_data.config['midi_note_median']}")
    logger.info(f"Audio extensions: {run_data.config['extensions']}")
    logger.info(f"Audio channels: {run_data.config['channels']}")
    logger.info(f"Main channels: {run_data.config['main_channels']}")

    if run_data.config["extra_files"]:
        logger.info(f"Extra files: {run_data.config['extra_files']}")


def evaluate_midi_mapping(run_data: RunData) -> None:
    """
    Calculate MIDI mapping for given run_data dict.

    Args:
        run_data: RunData instance containing at least 'audio_files' and 'config' keys

    Returns:
        None
    """
    audio_files = run_data.audio_sources
    metadata = run_data.config

    # Get MIDI note range
    min_note = metadata.get("midi_note_min", constants.DEFAULT_MIDI_NOTE_MIN)
    max_note = metadata.get("midi_note_max", constants.DEFAULT_MIDI_NOTE_MAX)
    median_note = metadata.get("midi_note_median", constants.DEFAULT_MIDI_NOTE_MEDIAN)

    instruments_count = len(audio_files)
    note_range = max_note - min_note + 1

    midi_mapping = {}
    if instruments_count == note_range and instruments_count > 0:
        # Cas spécial : chaque instrument couvre toute la plage
        for i, filename in enumerate(audio_files):
            instrument_name = utils.get_instrument_name(filename)
            midi_mapping[instrument_name] = min_note + i
            run_data.midi_mapping[instrument_name] = min_note + i
            logger.log("DEBUG", f"Mapping {instrument_name} to MIDI note {min_note + i}")
    else:
        left_count = instruments_count // 2
        for i, filename in enumerate(audio_files):
            instrument_name = utils.get_instrument_name(filename)
            # Algo médian classique
            if i < left_count:
                offset = left_count - i
                note = median_note - offset
            else:
                offset = i - left_count
                note = median_note + offset
            note = max(min_note, min(note, max_note))
            run_data.midi_mapping[instrument_name] = note
            logger.log("DEBUG", f"Mapping {instrument_name} to MIDI note {note}")


def print_midi_mapping(run_data: RunData) -> None:
    """
    Print the MIDI mapping for the given run_data dict.

    Args:
        run_data: RunData instance containing at least 'audio_files' and 'config' keys
    """
    logger.info("\n=== MIDI Mapping Preview ===")
    audio_files = run_data.midi_mapping

    if not audio_files:
        logger.warning("No instruments found for MIDI mapping")
        return

    # Display MIDI mapping
    logger.info("MIDI mapping preview (alphabetical order):")
    for instrument, note in sorted(audio_files.items(), key=lambda x: x[0]):
        logger.info(f"- MIDI Note {note}: {instrument}")


def print_summary(run_data: RunData) -> None:
    """
    Print a summary of the generated kit.

    Args:
        run_data: RunData instance containing at least 'config', 'audio_files', 'audio_files_processed', 'midi_mapping', 'generation_time' keys
    """
    logger.section("Summary")

    target_dir = run_data.target_dir
    metadata = run_data.config
    processed_audio_files = run_data.audio_processed
    audio_files = run_data.audio_sources
    midi_mapping = run_data.midi_mapping

    if logger.is_raw_output():
        msg = "Processing complete."
    else:
        msg = f"Processing complete in {run_data.generation_time:.2f} seconds."
    logger.info(msg, write_log=False)
    logger.info(f"DrumGizmo kit successfully created in {target_dir}", write_log=False)
    logger.info("\nMain files:", write_log=False)
    logger.info(f"  - {os.path.join(target_dir, 'drumkit.xml')}", write_log=False)
    logger.info(f"  - {os.path.join(target_dir, 'midimap.xml')}", write_log=False)

    logger.info("\nKit metadata summary:", write_log=False)
    logger.info(f"  - Name: {metadata.get('name', '')}", write_log=False)
    logger.info(f"  - Version: {metadata.get('version', '')}", write_log=False)
    logger.info(f"  - Description: {metadata.get('description', '')}", write_log=False)
    logger.info(f"  - Notes: {metadata.get('notes', '')}", write_log=False)
    logger.info(f"  - Author: {metadata.get('author', '')}", write_log=False)
    logger.info(f"  - License: {metadata.get('license', '')}", write_log=False)
    logger.info(f"  - Sample rate: {metadata.get('samplerate', '')} Hz", write_log=False)
    logger.info(f"  - Website: {metadata.get('website', '')}", write_log=False)
    logger.info(f"  - Logo: {metadata.get('logo', '')}", write_log=False)

    logger.info(f"\nNumber of instruments created: {len(processed_audio_files)}", write_log=False)
    logger.info("\nInstrument samples MIDI mapping:", write_log=False)

    # Display mapping with MIDI notes
    for instrument in processed_audio_files:
        midi_note = midi_mapping.get(instrument, "N/A")
        original_file = audio_files.get(instrument, {}).get("source_path", "N/A")
        logger.info(
            f"  - MIDI note {midi_note}: {instrument}: {os.path.basename(original_file)}",
            write_log=False,
        )

    extra_files = []
    if metadata.get("logo"):
        extra_files.append(metadata["logo"])
    if metadata.get("extra_files"):
        extra_files.extend(metadata["extra_files"])

    if extra_files:
        logger.info("\nExtra files copied:", write_log=False)
        for extra_file in extra_files:
            logger.info(f"  - {extra_file}", write_log=False)


def process_audio_files(run_data: RunData) -> Dict[str, List[str]]:
    """
    Process audio files by creating velocity variations.

    Args:
        run_data: RunData instance containing at least 'audio_files' and 'config' keys

    Raises:
        AudioProcessingError: If processing audio files fails
        DependencyError: If SoX is not found
    """
    audio_files = run_data.audio_sources
    metadata = run_data.config
    logger.section("Processing Audio Files")

    run_data.audio_processed = {}

    try:
        for instrument_name in audio_files:
            # Process the sample with sample rate conversion if needed
            processed_files = audio.process_sample(
                audio_files[instrument_name]["source_path"],
                run_data.target_dir,
                metadata,
                audio_files[instrument_name],
            )

            # Get the instrument name from the first processed file
            if processed_files:
                run_data.audio_processed[instrument_name] = processed_files

    except AudioProcessingError as e:
        # Enrich the error with more context
        error_context = {
            "instrument": instrument_name,
            "source_path": audio_files[instrument_name]["source_path"],
            "target_dir": run_data.target_dir,
        }
        raise AudioProcessingError(f"Failed to process audio file: {e}", error_context) from e
    except DependencyError as e:
        # Enrich the error with more context about the missing dependency
        raise DependencyError(f"Missing dependency during audio processing: {e}") from e
    except OSError as e:
        # Handle file system errors specifically
        error_context = {
            "instrument": instrument_name if "instrument_name" in locals() else "unknown",
            "error_code": e.errno if hasattr(e, "errno") else "unknown",
        }
        raise AudioProcessingError(
            f"System error during audio processing: {e}", error_context
        ) from e
    except Exception as e:
        # Capture other unexpected exceptions
        error_context = {
            "instrument": instrument_name if "instrument_name" in locals() else "unknown",
            "exception_type": type(e).__name__,
        }
        raise AudioProcessingError(
            f"Unexpected error during audio processing: {e}", error_context
        ) from e


def generate_xml_files(run_data: RunData) -> None:
    """
    Generate XML files for the DrumGizmo kit.

    Args:
        run_data: RunData instance containing at least 'audio_files' and 'config' keys

    Raises:
        XMLGenerationError: If generating XML files fails
    """
    logger.section("Generating XML Files")

    metadata = run_data.config

    try:
        # Extract instrument names from audio files
        instrument_names = run_data.audio_processed.keys()

        logger.print_action_start("Generating 'drumkit.xml'")
        xml_generator.generate_drumkit_xml(run_data.target_dir, instrument_names, metadata)
        logger.print_action_end()

        logger.print_action_start("Generating instruments XML files")
        for instrument_name in run_data.audio_processed:
            xml_generator.generate_instrument_xml(
                run_data.target_dir,
                instrument_name,
                run_data.audio_sources,
                run_data.audio_processed,
                run_data.config,
            )
        logger.print_action_end()

        # Generate midimap.xml
        logger.print_action_start("Generating 'midimap.xml'")
        xml_generator.generate_midimap_xml(run_data.target_dir, run_data.midi_mapping)
        logger.print_action_end()

    except XMLGenerationError as e:
        # Reuse the existing error with more context
        raise XMLGenerationError(f"Failed to generate XML files: {e}") from e
    except OSError as e:
        # Handle I/O errors specifically
        error_context = {
            "target_dir": run_data.target_dir,
            "error_code": e.errno if hasattr(e, "errno") else "unknown",
            "error_file": e.filename if hasattr(e, "filename") else "unknown",
        }
        raise XMLGenerationError(f"I/O error during XML file generation: {e}", error_context) from e
    except ValueError as e:
        # Handle invalid value errors
        error_context = {
            "instrument_count": len(run_data.audio_processed)
            if hasattr(run_data, "audio_processed")
            else 0,
            "midi_mapping_count": len(run_data.midi_mapping)
            if hasattr(run_data, "midi_mapping")
            else 0,
        }
        raise XMLGenerationError(
            f"Invalid values during XML file generation: {e}", error_context
        ) from e
    except Exception as e:
        # Capture other unexpected exceptions
        error_context = {"exception_type": type(e).__name__, "target_dir": run_data.target_dir}
        raise XMLGenerationError(
            f"Unexpected error during XML file generation: {e}", error_context
        ) from e


# pylint: disable=too-many-locals
def scan_source_files(run_data: RunData) -> None:
    """
    Scan source directory for audio files with extensions from config in run_data, with audio info for each audio file.

    Args:
        run_data: RunData containing at least 'config' with the metadata
    """
    logger.section("Scanning Source Directory")

    source_dir = run_data.source_dir
    extensions = run_data.config.get("extensions", constants.DEFAULT_EXTENSIONS)

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
                instrument_name = utils.get_instrument_name(file)
                audio_files[instrument_name] = {"source_path": file_path}

    # Sort audio files alphabetically by filename
    audio_files = dict(sorted(audio_files.items()))

    # Check if the number of files exceeds the MIDI note range
    midi_note_max = run_data.config.get("midi_note_max")
    midi_note_min = run_data.config.get("midi_note_min")

    if midi_note_max is None or midi_note_min is None:
        raise ValidationError("Missing MIDI note range in options (min or max)")

    midi_range = midi_note_max - midi_note_min + 1
    if len(audio_files) > midi_range:
        logger.warning(
            f"Number of audio files ({len(audio_files)}) exceeds MIDI note range "
            f"({midi_note_min} - {midi_note_max}, {midi_range} notes)."
            f"\nOnly the first {midi_range} files will be processed."
        )
        audio_files = dict(list(audio_files.items())[:midi_range])

    # get audio info for each sample
    for instrument_name, file_info in audio_files.items():
        info = audio.get_audio_info(file_info["source_path"])
        file_info.update(info)

    # Print the list of audio files
    logger.info(f"Found {len(audio_files)} audio files:", write_log=False)
    for instrument_name, data in audio_files.items():
        logger.info(
            f"- {instrument_name} ({data['samplerate']} Hz - {data['channels']} channels)",
            write_log=False,
        )

    run_data.audio_sources = audio_files


def copy_additional_files(run_data: RunData) -> None:
    """
    Copy logo and additional files to the target directory.

    Args:
        run_data: RunData instance containing at least 'config' and 'target_dir' keys

    Raises:
        DirectoryError: If copying additional files fails
    """
    try:
        # Copy logo if specified
        if run_data.config.get("logo"):
            logger.section("Copying Logo")
            logo_path = os.path.join(run_data.source_dir, run_data.config["logo"])
            if os.path.isfile(logo_path):
                logger.print_action_start(f"Copying logo file '{run_data.config['logo']}'")
                shutil.copy2(logo_path, run_data.target_dir)
                logger.print_action_end()
            else:
                logger.warning(f"Logo file not found: {logo_path}")

        # Copy extra files if specified
        if run_data.config.get("extra_files"):
            logger.section("Copying Additional Files")
            extra_files = run_data.config.get("extra_files")
            # If extra_files is already a list, use it directly
            if not isinstance(extra_files, list):
                extra_files = extra_files.split(",")
            for extra_file in extra_files:
                extra_file = extra_file.strip()
                extra_file_path = os.path.join(run_data.source_dir, extra_file)
                if os.path.isfile(extra_file_path):
                    logger.print_action_start(f"Copying extra file '{extra_file}'")
                    shutil.copy2(extra_file_path, run_data.target_dir)
                    logger.print_action_end()
                else:
                    logger.warning(f"Extra file not found: {extra_file_path}")

    except FileNotFoundError as e:
        # Handle file not found errors specifically
        error_context = {
            "file": e.filename if hasattr(e, "filename") else "unknown",
            "source_dir": run_data.source_dir,
            "target_dir": run_data.target_dir,
        }
        raise DirectoryError(
            f"File not found when copying additional files: {e}", error_context
        ) from e
    except PermissionError as e:
        # Handle permission errors specifically
        error_context = {
            "file": e.filename if hasattr(e, "filename") else "unknown",
            "error_code": e.errno if hasattr(e, "errno") else "unknown",
        }
        raise DirectoryError(
            f"Permission error when copying additional files: {e}", error_context
        ) from e
    except OSError as e:
        # Handle file system errors specifically
        error_context = {
            "file": e.filename if hasattr(e, "filename") else "unknown",
            "error_code": e.errno if hasattr(e, "errno") else "unknown",
        }
        raise DirectoryError(
            f"System error when copying additional files: {e}", error_context
        ) from e
    except Exception as e:
        # Capture other unexpected exceptions
        error_context = {
            "exception_type": type(e).__name__,
            "source_dir": run_data.source_dir,
            "target_dir": run_data.target_dir,
        }
        raise DirectoryError(
            f"Unexpected error when copying additional files: {e}", error_context
        ) from e


def validate_directories(run_data: RunData) -> None:
    """
    Validate source and target directories.

    Args:
        run_data: RunData instance containing at least 'source_dir' and 'target_dir' keys

    Raises:
        ValidationError: If source directory doesn't exist
        ValidationError: If target's parent directory doesn't exist
    """
    logger.log("INFO", "Analyzing sources directory...")

    # Check if source directory exists
    if not os.path.isdir(run_data.source_dir):
        raise ValidationError(f"Source directory '{run_data.source_dir}' does not exist")

    # Validate target directory
    target_parent = os.path.dirname(os.path.abspath(run_data.target_dir))
    if not os.path.exists(run_data.target_dir) and not os.path.isdir(target_parent):
        raise ValidationError(f"Parent directory of target '{target_parent}' does not exist")
