#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=broad-exception-caught
"""
Main script for DrumGizmo kit generation.
Uses the config, audio, xml_generator and utils modules to create a complete kit.
"""

import argparse
import datetime
import os
import shutil
import sys

# Import local modules
from drumgizmo_kits_generator.audio import (
    copy_sample_file,
    create_volume_variations,
    find_audio_files,
)
from drumgizmo_kits_generator.config import (
    DEFAULT_EXTENSIONS,
    DEFAULT_LICENSE,
    DEFAULT_MIDI_NOTE_MAX,
    DEFAULT_MIDI_NOTE_MEDIAN,
    DEFAULT_MIDI_NOTE_MIN,
    DEFAULT_NAME,
    DEFAULT_SAMPLERATE,
    DEFAULT_VELOCITY_LEVELS,
    DEFAULT_VERSION,
    read_config_file,
)
from drumgizmo_kits_generator.utils import (
    extract_instrument_name,
    get_file_extension,
    prepare_instrument_directory,
    prepare_target_directory,
    print_summary,
)
from drumgizmo_kits_generator.xml_generator import (
    create_drumkit_xml,
    create_instrument_xml,
    create_midimap_xml,
)

# Default values for command line arguments
# These are now imported from config.py


def parse_arguments():
    """
    Parse command line arguments.

    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Create a DrumGizmo kit from a set of audio samples",
        epilog="""
Configuration file options:
  All command-line options can be specified in a configuration file (INI format).
  The configuration file takes precedence over default values, but command-line
  arguments override configuration file settings.

  Examples of configuration file variables:
    kit_name               Kit name
    kit_version            Kit version
    kit_description        Kit description
    kit_notes              Additional notes about the kit
    kit_author             Kit author
    kit_license            Kit license
    kit_website            Kit website
    kit_logo               Kit logo filename
    kit_samplerate         Sample rate in Hz
    kit_extra_files        Additional files to copy
    kit_velocity_levels    Number of velocity levels to generate
    kit_midi_note_min      Minimum MIDI note number allowed
    kit_midi_note_max      Maximum MIDI note number allowed
    kit_midi_note_median   Median MIDI note for distributing instruments
    kit_extensions         Audio file extensions to process
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-s", "--source", required=True, help="REQUIRED - Source directory containing audio samples"
    )
    parser.add_argument(
        "-t", "--target", required=True, help="REQUIRED - Target directory for the DrumGizmo kit"
    )
    parser.add_argument("-c", "--config", help="Configuration file path (INI format)")
    parser.add_argument(
        "--extensions",
        default=DEFAULT_EXTENSIONS,
        help=f"Comma-separated list of audio file extensions to process (default: {DEFAULT_EXTENSIONS})",
    )

    parser.add_argument(
        "--velocity-levels",
        type=int,
        default=DEFAULT_VELOCITY_LEVELS,
        help=f"Number of velocity levels to generate (default: {DEFAULT_VELOCITY_LEVELS})",
    )

    # MIDI mapping arguments
    parser.add_argument(
        "--midi-note-min",
        type=int,
        default=DEFAULT_MIDI_NOTE_MIN,
        help=f"Minimum MIDI note number allowed (default: {DEFAULT_MIDI_NOTE_MIN})",
    )
    parser.add_argument(
        "--midi-note-max",
        type=int,
        default=DEFAULT_MIDI_NOTE_MAX,
        help=f"Maximum MIDI note number allowed (default: {DEFAULT_MIDI_NOTE_MAX})",
    )
    parser.add_argument(
        "--midi-note-median",
        type=int,
        default=DEFAULT_MIDI_NOTE_MEDIAN,
        help=f"Median MIDI note for distributing instruments around (default: {DEFAULT_MIDI_NOTE_MEDIAN})",
    )

    # Arguments for metadata (can be overridden by the configuration file)
    parser.add_argument("--name", help="Kit name")
    parser.add_argument(
        "--version",
        default=DEFAULT_VERSION,
        help=f"Kit version (default: {DEFAULT_VERSION})",
    )
    parser.add_argument("--description", help="Kit description")
    parser.add_argument("--notes", help="Additional notes about the kit")
    parser.add_argument("--author", help="Kit author")
    parser.add_argument(
        "--license",
        default=DEFAULT_LICENSE,
        help=f"Kit license (default: {DEFAULT_LICENSE})",
    )
    parser.add_argument("--website", help="Kit website")
    parser.add_argument(
        "--samplerate",
        default=DEFAULT_SAMPLERATE,
        help=f"Sample rate in Hz (default: {DEFAULT_SAMPLERATE})",
    )
    parser.add_argument("--logo", help="Logo file to include in the kit")
    parser.add_argument(
        "--extra-files", help="Comma-separated list of additional files to include in the kit"
    )

    return parser.parse_args()


# pylint: disable-next=too-many-branches,too-many-statements
def prepare_metadata(args):
    """
    Prepare kit metadata by combining command line arguments and configuration file.

    Args:
        args (argparse.Namespace): Command line arguments

    Returns:
        dict: Kit metadata
    """
    metadata = {}

    # Read configuration file if specified
    if args.config:
        config_metadata = read_config_file(args.config)
        metadata.update(config_metadata)
        print(f"Metadata loaded from config file: {config_metadata}", file=sys.stderr)

    # Update metadata with command line arguments
    if args.name:
        metadata["name"] = args.name
    if args.version:
        metadata["version"] = args.version
    if args.description:
        metadata["description"] = args.description
    elif "description" not in metadata:
        # Only set default description if not provided in config or command line
        metadata[
            "description"
        ] = f"Kit automatically created with {args.velocity_levels} velocity levels"
    if args.notes:
        metadata["notes"] = args.notes
    elif "notes" in metadata:
        # Append generation timestamp to existing notes
        metadata[
            "notes"
        ] += f" - Generated with create_drumgizmo_kit.py at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"
    else:
        # Create new notes with generation timestamp
        metadata[
            "notes"
        ] = f"Generated with create_drumgizmo_kit.py at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}"
    if args.author:
        metadata["author"] = args.author
    if args.license:
        metadata["license"] = args.license
    if args.website:
        metadata["website"] = args.website
    if args.samplerate:
        metadata["samplerate"] = args.samplerate
    if args.logo:
        metadata["logo"] = args.logo
    if args.extra_files:
        metadata["extra_files"] = args.extra_files

    # Set default values for metadata if not provided
    if "name" not in metadata:
        metadata["name"] = DEFAULT_NAME
    if "version" not in metadata:
        metadata["version"] = DEFAULT_VERSION
    if "description" not in metadata:
        metadata[
            "description"
        ] = f"Kit automatically created with {args.velocity_levels} velocity levels"
    if "author" not in metadata:
        metadata["author"] = ""
    if "license" not in metadata:
        metadata["license"] = DEFAULT_LICENSE
    if "website" not in metadata:
        metadata["website"] = ""
    if "samplerate" not in metadata:
        metadata["samplerate"] = DEFAULT_SAMPLERATE
    if "logo" not in metadata:
        metadata["logo"] = ""
    if "extra_files" not in metadata:
        metadata["extra_files"] = ""

    # Extract MIDI and velocity parameters from config file
    # These are stored in the metadata dictionary but will be extracted by the main function
    if "midi_note_min" in metadata and args.midi_note_min == DEFAULT_MIDI_NOTE_MIN:
        try:
            metadata["midi_note_min"] = int(metadata["midi_note_min"])
        except ValueError:
            print(
                f"Warning: Invalid midi_note_min value in config file: {metadata['midi_note_min']}",
                file=sys.stderr,
            )
            metadata.pop("midi_note_min")

    if "midi_note_max" in metadata and args.midi_note_max == DEFAULT_MIDI_NOTE_MAX:
        try:
            metadata["midi_note_max"] = int(metadata["midi_note_max"])
        except ValueError:
            print(
                f"Warning: Invalid midi_note_max value in config file: {metadata['midi_note_max']}",
                file=sys.stderr,
            )
            metadata.pop("midi_note_max")

    if "midi_note_median" in metadata and args.midi_note_median == DEFAULT_MIDI_NOTE_MEDIAN:
        try:
            metadata["midi_note_median"] = int(metadata["midi_note_median"])
        except ValueError:
            print(
                f"Warning: Invalid midi_note_median value in config file: {metadata['midi_note_median']}",
                file=sys.stderr,
            )
            metadata.pop("midi_note_median")

    if "velocity_levels" in metadata and args.velocity_levels == DEFAULT_VELOCITY_LEVELS:
        try:
            metadata["velocity_levels"] = int(metadata["velocity_levels"])
        except ValueError:
            print(
                f"Warning: Invalid velocity_levels value in config file: {metadata['velocity_levels']}",
                file=sys.stderr,
            )
            metadata.pop("velocity_levels")

    # Handle extensions from config file
    if "extensions" in metadata and args.extensions == DEFAULT_EXTENSIONS:
        extensions_value = metadata["extensions"]
        if extensions_value:
            metadata["extensions"] = extensions_value
        else:
            print(
                f"Warning: Invalid extensions value in config file: {metadata['extensions']}",
                file=sys.stderr,
            )
            metadata.pop("extensions")

    print("\nFinal metadata after processing:", file=sys.stderr)
    for key, value in metadata.items():
        print(f"  {key}: {value}", file=sys.stderr)
    print("\n", file=sys.stderr)

    return metadata


def copy_extra_files(source_dir, target_dir, extra_files_str):
    """
    Copy additional files specified in extra_files to the target directory.

    Args:
        source_dir (str): Source directory containing the files
        target_dir (str): Target directory to copy the files to
        extra_files_str (str): Comma-separated list of files to copy

    Returns:
        list: List of successfully copied files
    """
    if not extra_files_str:
        return []

    # Split the comma-separated list
    extra_files = [f.strip() for f in extra_files_str.split(",")]
    copied_files = []

    print(f"\nCopying extra files to {target_dir}:", file=sys.stderr)

    for file in extra_files:
        source_file = os.path.join(source_dir, file)
        target_file = os.path.join(target_dir, file)

        # Check if source file exists
        if not os.path.exists(source_file):
            print(f"  Warning: Extra file not found: {source_file}", file=sys.stderr)
            continue

        try:
            # Create target directory if it doesn't exist (for files in subdirectories)
            target_dir_path = os.path.dirname(target_file)
            if not os.path.exists(target_dir_path):
                os.makedirs(target_dir_path)

            # Copy the file
            shutil.copy2(source_file, target_file)
            print(f"  Copied: {file}", file=sys.stderr)
            copied_files.append(file)
        except Exception as e:
            print(f"  Error copying {file}: {e}", file=sys.stderr)

    return copied_files


# pylint: disable-next=too-many-locals,too-many-branches,too-many-statements
def main():
    """
    Main function of the script.
    """
    # Parse arguments
    args = parse_arguments()

    # Prepare metadata
    metadata = prepare_metadata(args)

    # Prepare target directory
    if not prepare_target_directory(args.target):
        sys.exit(1)

    # Search for samples in the source directory
    if "extensions" in metadata:
        extensions = metadata["extensions"].split(",")
    else:
        extensions = args.extensions.split(",")
    samples = find_audio_files(args.source, extensions)

    print(f"Searching for samples in: {args.source}", file=sys.stderr)
    print(f"Number of samples found: {len(samples)}", file=sys.stderr)

    if not samples:
        print("Error: No audio samples found in the source directory", file=sys.stderr)
        sys.exit(1)

    # Sort samples alphabetically by filename
    samples.sort(key=lambda x: os.path.basename(x).lower())
    print("Samples sorted alphabetically", file=sys.stderr)

    # Initialize MIDI and velocity parameters from command line arguments
    midi_note_min = args.midi_note_min
    midi_note_max = args.midi_note_max
    midi_note_median = args.midi_note_median

    # Process velocity levels
    if "velocity_levels" in metadata:
        velocity_levels = int(metadata["velocity_levels"])
    else:
        velocity_levels = args.velocity_levels

    # Override with values from config file if available
    # pylint: disable-next=consider-using-get
    if "midi_note_min" in metadata:
        midi_note_min = metadata["midi_note_min"]
    # pylint: disable-next=consider-using-get
    if "midi_note_max" in metadata:
        midi_note_max = metadata["midi_note_max"]
    # pylint: disable-next=consider-using-get
    if "midi_note_median" in metadata:
        midi_note_median = metadata["midi_note_median"]

    # Validate parameters
    if midi_note_min < 0 or midi_note_min > 127:
        print(
            f"Warning: Invalid midi_note_min value: {midi_note_min}, using default {DEFAULT_MIDI_NOTE_MIN}",
            file=sys.stderr,
        )
        midi_note_min = DEFAULT_MIDI_NOTE_MIN
    if midi_note_max < 0 or midi_note_max > 127:
        print(
            f"Warning: Invalid midi_note_max value: {midi_note_max}, using default {DEFAULT_MIDI_NOTE_MAX}",
            file=sys.stderr,
        )
        midi_note_max = DEFAULT_MIDI_NOTE_MAX
    if midi_note_median < 0 or midi_note_median > 127:
        print(
            f"Warning: Invalid midi_note_median value: {midi_note_median}, using default {DEFAULT_MIDI_NOTE_MEDIAN}",
            file=sys.stderr,
        )
        midi_note_median = DEFAULT_MIDI_NOTE_MEDIAN
    if velocity_levels < 1:
        print(
            f"Warning: Invalid velocity_levels value: {velocity_levels}, using default {DEFAULT_VELOCITY_LEVELS}",
            file=sys.stderr,
        )
        velocity_levels = DEFAULT_VELOCITY_LEVELS

    # Process each sample
    instruments = []
    instrument_to_sample = {}  # Map to keep track of which sample was used for each instrument

    for sample in samples:
        # Extract instrument name
        instrument = extract_instrument_name(sample)
        instruments.append(instrument)
        instrument_to_sample[instrument] = os.path.basename(sample)

        # Get file extension
        extension = get_file_extension(sample)

        # Prepare directory for the instrument
        if not prepare_instrument_directory(instrument, args.target):
            continue

        # Copy original sample
        samples_dir = os.path.join(args.target, instrument, "samples")
        dest_file = os.path.join(samples_dir, f"1-{instrument}{extension}")

        # Get the target sample rate from metadata if available
        target_samplerate = metadata.get("samplerate", None)

        # Copy the sample file, converting the sample rate if needed
        if not copy_sample_file(sample, dest_file, target_samplerate):
            continue

        # Create volume variations
        create_volume_variations(
            instrument, args.target, extension, velocity_levels, target_samplerate
        )

        # Create XML file for the instrument
        create_instrument_xml(
            instrument,
            args.target,
            extension,
            velocity_levels,
        )

    # Create drumkit.xml file
    create_drumkit_xml(instruments, args.target, metadata)

    # Create midimap.xml file
    create_midimap_xml(
        instruments,
        args.target,
        midi_note_min=midi_note_min,
        midi_note_max=midi_note_max,
        midi_note_median=midi_note_median,
    )

    # Copy logo if specified
    if "logo" in metadata and metadata["logo"]:
        logo_source = os.path.join(args.source, metadata["logo"])
        logo_dest = os.path.join(args.target, metadata["logo"])

        if os.path.exists(logo_source):
            try:
                shutil.copy2(logo_source, logo_dest)
                print(f"Logo file copied: {metadata['logo']}", file=sys.stderr)
            except Exception as e:
                print(f"Warning: Could not copy logo file: {e}", file=sys.stderr)

    # Copy extra files if specified
    extra_files_copied = []
    if "extra_files" in metadata and metadata["extra_files"]:
        extra_files_copied = copy_extra_files(args.source, args.target, metadata["extra_files"])

    # Display summary
    print_summary(metadata, instruments, args.target)

    # Print mapping of instruments to original sample files
    print("\nInstrument to sample mapping:", file=sys.stderr)
    for instrument, sample in instrument_to_sample.items():
        print(f"  {instrument}: {sample}", file=sys.stderr)

    # Print extra files copied
    if extra_files_copied:
        print("\nExtra files copied:", file=sys.stderr)
        for file in extra_files_copied:
            print(f"  {file}", file=sys.stderr)


if __name__ == "__main__":
    main()
