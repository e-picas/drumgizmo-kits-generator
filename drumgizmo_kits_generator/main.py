#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=broad-exception-caught
"""
Main script for DrumGizmo kit generation.
Uses the config, audio, xml_generator and utils modules to create a complete kit.
"""

import argparse
import os
import shutil
import sys

# Import local modules
from drumgizmo_kits_generator.audio import (
    copy_sample_file,
    create_volume_variations,
    find_audio_files,
)
from drumgizmo_kits_generator.config import read_config_file
from drumgizmo_kits_generator.utils import (
    extract_instrument_name,
    get_file_extension,
    get_timestamp,
    prepare_instrument_directory,
    prepare_target_directory,
    print_summary,
)
from drumgizmo_kits_generator.xml_generator import (
    create_drumkit_xml,
    create_midimap_xml,
    create_xml_file,
)


def parse_arguments():
    """
    Parse command line arguments.

    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(description="Create a DrumGizmo kit from audio samples")

    parser.add_argument(
        "-s", "--source", required=True, help="Source directory containing audio samples"
    )
    parser.add_argument(
        "-t", "--target", required=True, help="Target directory for the DrumGizmo kit"
    )
    parser.add_argument("-c", "--config", help="Configuration file path")
    parser.add_argument(
        "--extensions",
        default="wav,WAV,flac,FLAC,ogg,OGG",
        help="Comma-separated list of audio file extensions to process (default: wav,WAV,flac,FLAC,ogg,OGG)",
    )

    # Arguments for metadata (can be overridden by the configuration file)
    parser.add_argument("--name", help="Kit name")
    parser.add_argument("--version", default="1.0", help="Kit version (default: 1.0)")
    parser.add_argument(
        "--description",
        default="Kit automatically created with 10 velocity levels",
        help="Kit description (default: Kit automatically created with 10 velocity levels)",
    )
    parser.add_argument("--notes", help="Additional notes about the kit")
    parser.add_argument("--author", help="Kit author")
    parser.add_argument(
        "--license", default="Private license", help="Kit license (default: Private license)"
    )
    parser.add_argument("--website", help="Kit website")
    parser.add_argument("--logo", help="Kit logo filename")
    parser.add_argument("--samplerate", default="44100", help="Sample rate in Hz (default: 44100)")
    parser.add_argument("--instrument-prefix", help="Prefix for instrument names")
    parser.add_argument(
        "--extra-files",
        help="Comma-separated list of additional files to copy to the target directory",
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

    # Override with command line arguments ONLY if they are explicitly specified
    # (not using default values)
    if args.name:
        metadata["name"] = args.name
    elif "name" not in metadata:
        metadata["name"] = "DrumGizmoKit"

    # For version, only use command line value if it's not the default or if no config value exists
    if args.version and (args.version != "1.0" or "version" not in metadata):
        metadata["version"] = args.version
    elif "version" not in metadata:
        metadata["version"] = "1.0"

    # For description, only use command line value if it's not the default or if no config value exists
    default_desc = "Kit automatically created with 10 velocity levels"
    if args.description and (args.description != default_desc or "description" not in metadata):
        metadata["description"] = args.description
    elif "description" not in metadata:
        metadata["description"] = default_desc

    if args.notes:
        metadata["notes"] = args.notes
    elif "notes" not in metadata:
        # Use source directory name as sample information
        source_name = os.path.basename(os.path.abspath(args.source))
        metadata["notes"] = f"DrumGizmo kit generated from royalty free samples '{source_name}'"

    if args.author:
        metadata["author"] = args.author
    elif "author" not in metadata:
        metadata["author"] = os.environ.get("USER", "Unknown")

    # For license, only use command line value if it's not the default or if no config value exists
    if args.license and (args.license != "Private license" or "license" not in metadata):
        metadata["license"] = args.license
    elif "license" not in metadata:
        metadata["license"] = "Private license"

    if args.website:
        metadata["website"] = args.website

    if args.logo:
        metadata["logo"] = args.logo

    # For samplerate, only use command line value if it's not the default or if no config value exists
    if args.samplerate and (args.samplerate != "44100" or "samplerate" not in metadata):
        metadata["samplerate"] = args.samplerate
    elif "samplerate" not in metadata:
        metadata["samplerate"] = "44100"

    if args.instrument_prefix:
        metadata["instrument_prefix"] = args.instrument_prefix

    # For extra files, use command line value if specified, otherwise use config value
    if args.extra_files:
        metadata["extra_files"] = args.extra_files

    # Add date and script name to the description
    timestamp = get_timestamp()
    if "notes" in metadata and metadata["notes"]:
        # Don't modify notes if they already exist, except to add the date
        if " - Generated with create_drumgizmo_kit.py at " not in metadata["notes"]:
            metadata[
                "notes"
            ] = f"{metadata['notes']} - Generated with create_drumgizmo_kit.py at {timestamp}"
    else:
        metadata["notes"] = f"Generated with create_drumgizmo_kit.py at {timestamp}"

    # Display final metadata for debugging
    print("\nFinal metadata after processing:", file=sys.stderr)
    for key, value in metadata.items():
        print(f"  {key}: {value}", file=sys.stderr)
    print("", file=sys.stderr)

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


# pylint: disable-next=too-many-locals
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

        if not copy_sample_file(sample, dest_file):
            continue

        # Create volume variations
        create_volume_variations(instrument, args.target, extension)

        # Create XML file for the instrument
        create_xml_file(instrument, args.target, extension)

    # Create drumkit.xml file
    create_drumkit_xml(instruments, args.target, metadata)

    # Create midimap.xml file
    create_midimap_xml(instruments, args.target)

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
