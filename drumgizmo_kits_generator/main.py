#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main script for DrumGizmo kit generation.
Uses the config, audio, xml_generator and utils modules to create a complete kit.
"""
import argparse
import datetime
import os
import shutil
import sys
from typing import Any, Dict, List, Optional, Tuple

# Import local modules
from drumgizmo_kits_generator.audio import (
    copy_sample_file,
    create_volume_variations,
    find_audio_files,
)
from drumgizmo_kits_generator.config import process_channels_config, read_config_file
from drumgizmo_kits_generator.constants import (
    DEFAULT_EXTENSIONS,
    DEFAULT_LICENSE,
    DEFAULT_MIDI_NOTE_MAX,
    DEFAULT_MIDI_NOTE_MEDIAN,
    DEFAULT_MIDI_NOTE_MIN,
    DEFAULT_NAME,
    DEFAULT_SAMPLERATE,
    DEFAULT_VELOCITY_LEVELS,
    DEFAULT_VERSION,
)
from drumgizmo_kits_generator.utils import (
    extract_instrument_name,
    get_file_extension,
    prepare_instrument_directory,
    prepare_target_directory,
    print_summary,
    print_verbose,
)
from drumgizmo_kits_generator.validators import validate_midi_and_velocity_params
from drumgizmo_kits_generator.xml_generator import (
    create_drumkit_xml,
    create_instrument_xml,
    create_midimap_xml,
)

# Default values for command line arguments
# These are now imported from config.py


def parse_arguments() -> argparse.Namespace:
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
    kit_channels           Comma-separated list of audio channels to use
    kit_main_channels      Comma-separated list of main audio channels
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "-s",
        "--source",
        required=True,
        help="REQUIRED - Source directory containing audio samples",
    )
    parser.add_argument(
        "-t", "--target", required=True, help="REQUIRED - Target directory for the DrumGizmo kit"
    )
    parser.add_argument("-c", "--config", help="Configuration file path (INI format)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Increase process verbosity")
    parser.add_argument(
        "-x",
        "--dry-run",
        action="store_true",
        help="Enable the DEBUG or 'dry run' mode: metadata and samples list are printed instead of generating the kit",
    )
    parser.add_argument(
        "--extensions",
        help=f"Comma-separated list of audio file extensions to process (default: {DEFAULT_EXTENSIONS})",
    )

    parser.add_argument(
        "--velocity-levels",
        type=int,
        help=f"Number of velocity levels to generate (default: {DEFAULT_VELOCITY_LEVELS})",
    )

    # MIDI mapping arguments
    parser.add_argument(
        "--midi-note-min",
        type=int,
        help=f"Minimum MIDI note number allowed (default: {DEFAULT_MIDI_NOTE_MIN})",
    )
    parser.add_argument(
        "--midi-note-max",
        type=int,
        help=f"Maximum MIDI note number allowed (default: {DEFAULT_MIDI_NOTE_MAX})",
    )
    parser.add_argument(
        "--midi-note-median",
        type=int,
        help=f"Median MIDI note for distributing instruments around (default: {DEFAULT_MIDI_NOTE_MEDIAN})",
    )

    # Arguments for metadata (can be overridden by the configuration file)
    parser.add_argument(
        "--name",
        help=f"Kit name (default: {DEFAULT_NAME})",
    )
    parser.add_argument(
        "--version",
        help=f"Kit version (default: {DEFAULT_VERSION})",
    )
    parser.add_argument("--description", help="Kit description")
    parser.add_argument("--notes", help="Additional notes about the kit")
    parser.add_argument("--author", help="Kit author")
    parser.add_argument(
        "--license",
        help=f"Kit license (default: {DEFAULT_LICENSE})",
    )
    parser.add_argument("--website", help="Kit website")
    parser.add_argument(
        "--samplerate",
        help=f"Sample rate in Hz (default: {DEFAULT_SAMPLERATE})",
    )
    parser.add_argument("--logo", help="Logo file to include in the kit")
    parser.add_argument(
        "--extra-files",
        help="Comma-separated list of additional files to include in the kit",
    )

    # Channel configuration arguments
    parser.add_argument(
        "--channels",
        help="Comma-separated list of audio channels to use in the kit",
    )
    parser.add_argument(
        "--main-channels",
        help="Comma-separated list of main audio channels (with main='true' attribute)",
    )

    return parser.parse_args()


def _process_basic_metadata(metadata: Dict[str, Any], args: argparse.Namespace) -> Dict[str, Any]:
    """
    Process basic metadata fields from command line arguments.

    Args:
        metadata (Dict[str, Any]): Existing metadata dictionary
        args (argparse.Namespace): Command line arguments

    Returns:
        Dict[str, Any]: Updated metadata dictionary
    """
    # Simple string arguments
    for arg_name in [
        "name",
        "version",
        "author",
        "license",
        "website",
        "samplerate",
        "logo",
    ]:
        # Vérifier si l'argument a été explicitement fourni en ligne de commande
        # en vérifiant s'il est différent de la valeur par défaut ou s'il n'a pas de valeur par défaut
        arg_value = getattr(args, arg_name, None)

        # Déterminer si l'argument a été explicitement fourni par l'utilisateur
        # Pour les arguments qui ont une valeur par défaut, nous devons vérifier si l'utilisateur a fourni une valeur
        if arg_value is not None:
            # Vérifier si l'argument a une valeur par défaut
            default_value = None
            for action in args.__dict__.get("_actions", []):
                if action.dest == arg_name and hasattr(action, "default"):
                    default_value = action.default
                    break

            # Si l'argument n'a pas de valeur par défaut ou si la valeur est différente de la valeur par défaut,
            # alors l'utilisateur a explicitement fourni cette valeur
            if default_value is None or arg_value != default_value:
                metadata[arg_name] = arg_value

    # Traiter extra_files comme une liste
    if args.extra_files is not None:
        # Convertir en liste si c'est une chaîne de caractères
        if isinstance(args.extra_files, str):
            metadata["extra_files"] = [
                file.strip() for file in args.extra_files.split(",") if file.strip()
            ]
        else:
            metadata["extra_files"] = args.extra_files

    return metadata


def _process_description_and_notes(
    metadata: Dict[str, Any], args: argparse.Namespace
) -> Dict[str, Any]:
    """
    Process description and notes metadata from command line arguments.

    Args:
        metadata (Dict[str, Any]): Existing metadata dictionary
        args (argparse.Namespace): Command line arguments

    Returns:
        Dict[str, Any]: Updated metadata dictionary
    """
    # Special handling for description
    if args.description:
        metadata["description"] = args.description
    elif "description" not in metadata:
        # Only set default description if not provided in config or command line
        metadata[
            "description"
        ] = f"Kit automatically created with {args.velocity_levels} velocity levels"

    # Special handling for notes
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

    return metadata


def _process_command_line_overrides(
    metadata: Dict[str, Any], args: argparse.Namespace
) -> Dict[str, Any]:
    """
    Process command line overrides for MIDI parameters, velocity levels, and extensions.

    Args:
        metadata (Dict[str, Any]): Existing metadata dictionary
        args (argparse.Namespace): Command line arguments

    Returns:
        Dict[str, Any]: Updated metadata dictionary
    """
    # Process channels options
    if args.channels:
        # Store channels as a comma-separated string, not as a list representation
        metadata["channels"] = args.channels
    if args.main_channels:
        # Store main_channels as a comma-separated string, not as a list representation
        metadata["main_channels"] = args.main_channels

    # Check if these arguments were explicitly provided on the command line
    argv_str = " ".join(sys.argv)

    # Process MIDI parameters - command line arguments should override config values
    if "--midi-note-min" in argv_str:
        metadata["midi_note_min"] = args.midi_note_min
    if "--midi-note-max" in argv_str:
        metadata["midi_note_max"] = args.midi_note_max
    if "--midi-note-median" in argv_str:
        metadata["midi_note_median"] = args.midi_note_median

    # Process velocity levels - command line arguments should override config values
    if "--velocity-levels" in argv_str:
        metadata["velocity_levels"] = args.velocity_levels

    # Process extensions - command line arguments should override config values
    if "--extensions" in argv_str:
        # Convertir en liste si c'est une chaîne de caractères
        if isinstance(args.extensions, str):
            metadata["extensions"] = [
                ext.strip() for ext in args.extensions.split(",") if ext.strip()
            ]
        else:
            metadata["extensions"] = args.extensions

    return metadata


def update_metadata_from_args(metadata: Dict[str, Any], args: argparse.Namespace) -> Dict[str, Any]:
    """
    Update metadata with values from command line arguments.

    Args:
        metadata (Dict[str, Any]): Existing metadata dictionary
        args (argparse.Namespace): Command line arguments

    Returns:
        Dict[str, Any]: Updated metadata dictionary
    """
    # Process basic metadata fields
    metadata = _process_basic_metadata(metadata, args)

    # Process description and notes
    metadata = _process_description_and_notes(metadata, args)

    # Process command line overrides
    metadata = _process_command_line_overrides(metadata, args)

    return metadata


def set_default_metadata_values(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Set default values for metadata if not provided.

    Args:
        metadata (Dict[str, Any]): Existing metadata dictionary

    Returns:
        Dict[str, Any]: Updated metadata dictionary
    """
    # Set default values for required metadata
    if "name" not in metadata:
        metadata["name"] = DEFAULT_NAME
    if "version" not in metadata:
        metadata["version"] = DEFAULT_VERSION
    if "license" not in metadata:
        metadata["license"] = DEFAULT_LICENSE
    if "samplerate" not in metadata:
        metadata["samplerate"] = DEFAULT_SAMPLERATE
    if "extensions" not in metadata:
        # Convertir la chaîne DEFAULT_EXTENSIONS en liste
        metadata["extensions"] = [
            ext.strip() for ext in DEFAULT_EXTENSIONS.split(",") if ext.strip()
        ]

    # Set default values for optional metadata
    if "velocity_levels" not in metadata:
        metadata["velocity_levels"] = DEFAULT_VELOCITY_LEVELS
    if "midi_note_min" not in metadata:
        metadata["midi_note_min"] = DEFAULT_MIDI_NOTE_MIN
    if "midi_note_max" not in metadata:
        metadata["midi_note_max"] = DEFAULT_MIDI_NOTE_MAX
    if "midi_note_median" not in metadata:
        metadata["midi_note_median"] = DEFAULT_MIDI_NOTE_MEDIAN

    # Process channels configuration
    process_channels_config(metadata)

    return metadata


def prepare_metadata(args: argparse.Namespace) -> Dict[str, Any]:
    """
    Prepare kit metadata by combining command line arguments and configuration file.
    Order of precedence:
    1. Default values (lowest priority)
    2. Configuration file values
    3. Command line arguments (highest priority)

    Args:
        args (argparse.Namespace): Command line arguments

    Returns:
        dict: Kit metadata
    """
    # 1. Start with an empty metadata dictionary
    metadata = {}

    # 2. Set default values first (lowest priority)
    metadata = set_default_metadata_values(metadata)

    # 3. Read configuration file if specified (medium priority)
    if args.config:
        config_metadata = read_config_file(args.config)
        metadata.update(config_metadata)

    # 4. Update metadata with command line arguments (highest priority)
    metadata = update_metadata_from_args(metadata, args)

    # 5. Validate MIDI and velocity parameters
    metadata = validate_midi_and_velocity_params(metadata, args)

    # 6. Ensure channels and main_channels are properly processed
    process_channels_config(metadata)

    return metadata


def copy_extra_files(source_dir: str, target_dir: str, extra_files_str: str) -> List[str]:
    """
    Copy additional files specified in extra_files to the target directory.

    Args:
        source_dir (str): Source directory containing the files
        target_dir (str): Target directory to copy the files to
        extra_files_str (str): Comma-separated list of files to copy

    Returns:
        list: List of successfully copied files
    """
    copied_files = []

    # Handle both string and list inputs
    if isinstance(extra_files_str, list):
        extra_files = extra_files_str
    else:
        # Split by comma and trim whitespace
        extra_files = [file.strip() for file in extra_files_str.split(",") if file.strip()]

    for file in extra_files:
        source_file = os.path.join(source_dir, file)
        target_file = os.path.join(target_dir, file)

        # Check if source file exists
        if not os.path.exists(source_file):
            print(f"Warning: Extra file not found: {source_file}", file=sys.stderr)
            continue

        # Create target directory if it doesn't exist
        target_dir_path = os.path.dirname(target_file)
        if not os.path.exists(target_dir_path):
            os.makedirs(target_dir_path)

        # Copy file
        try:
            shutil.copy2(source_file, target_file)
            print(f"Copied extra file: {file}", file=sys.stderr)
            copied_files.append(file)
        except (IOError, OSError) as e:
            print(f"Error copying extra file {file}: {e}", file=sys.stderr)

    return copied_files


def copy_logo_file(source_dir: str, target_dir: str, logo_filename: str) -> bool:
    """
    Copy logo file from source to target directory.

    Args:
        source_dir: Source directory
        target_dir: Target directory
        logo_filename: Logo filename

    Returns:
        bool: True if successful, False otherwise
    """
    success = False

    if not logo_filename:
        return False

    logo_source = os.path.join(source_dir, logo_filename)
    logo_dest = os.path.join(target_dir, logo_filename)

    if not os.path.exists(logo_source):
        print(f"Warning: Logo file not found: {logo_filename}", file=sys.stderr)
        return False

    try:
        shutil.copy2(logo_source, logo_dest)
        print(f"Logo file copied: {logo_filename}", file=sys.stderr)
        success = True
    except PermissionError as e:
        print(f"Warning: Could not copy logo file: Permission denied: {e}", file=sys.stderr)
    except shutil.Error as e:
        print(f"Warning: Could not copy logo file: Shutil error: {e}", file=sys.stderr)
    except (OSError, IOError) as e:
        print(f"Warning: Could not copy logo file: File system error: {e}", file=sys.stderr)
    except Exception as e:  # pylint: disable=broad-exception-caught
        # Gardé pour la compatibilité avec les tests existants
        print(f"Warning: Could not copy logo file: {e}", file=sys.stderr)

    return success


def print_instrument_mapping(instrument_to_sample: Dict[str, str]) -> None:
    """
    Print mapping of instruments to original sample files.

    Args:
        instrument_to_sample (dict): Dictionary mapping instrument names to sample filenames
    """
    print("\nInstrument to sample mapping:", file=sys.stderr)
    for instrument, sample in instrument_to_sample.items():
        print(f"  {instrument}: {sample}", file=sys.stderr)


def print_extra_files(extra_files_copied: List[str]) -> None:
    """
    Print list of extra files copied.

    Args:
        extra_files_copied (list): List of extra files copied
    """
    if extra_files_copied:
        print("\nExtra files copied:", file=sys.stderr)
        for file in extra_files_copied:
            print(f"  {file}", file=sys.stderr)


def process_instruments(
    samples: List[str],
    args: argparse.Namespace,
    velocity_levels: int,
    target_samplerate: Optional[str],
    metadata: Dict[str, Any],
) -> Tuple[List[str], Dict[str, str]]:
    """
    Process each sample to create instruments.

    Args:
        samples: List of audio sample paths
        args: Command line arguments
        velocity_levels: Number of velocity levels to generate
        target_samplerate: Target sample rate for conversion, or None to keep original
        metadata: Metadata dictionary

    Returns:
        Tuple of (list of instrument names, dictionary mapping instrument to sample file)
    """
    instruments = []
    instrument_to_sample = {}  # Map to keep track of which sample was used for each instrument

    for sample in samples:
        # Extract instrument name
        instrument = extract_instrument_name(sample)
        instruments.append(instrument)
        instrument_to_sample[instrument] = os.path.basename(sample)

        print_verbose(f"Processing instrument: {instrument} from sample: {sample}", args)

        # Get file extension
        extension = get_file_extension(sample)

        # Prepare directory for the instrument
        if not prepare_instrument_directory(instrument, args.target):
            print_verbose(f"Failed to prepare directory for instrument: {instrument}", args)
            continue

        # Copy original sample
        samples_dir = os.path.join(args.target, instrument, "samples")
        dest_file = os.path.join(samples_dir, f"1-{instrument}{extension}")

        # Copy the sample file, converting the sample rate if needed
        if not copy_sample_file(sample, dest_file, target_samplerate, args):
            print_verbose(f"Failed to copy sample file: {sample}", args)
            continue

        # Create volume variations
        create_volume_variations(
            instrument, args.target, extension, velocity_levels, target_samplerate, args
        )

        # Create XML file for the instrument
        print_verbose(f"Creating XML file for instrument: {instrument}", args)
        create_instrument_xml(
            instrument,
            args.target,
            extension,
            velocity_levels,
            metadata,
        )

    return instruments, instrument_to_sample


def create_xml_files(
    instruments: List[str],
    args: argparse.Namespace,
    metadata: Dict[str, Any],
    midi_note_min: int,
    midi_note_max: int,
    midi_note_median: int,
) -> None:
    """
    Create XML files for the drumkit.

    Args:
        instruments: List of instrument names
        args: Command line arguments
        metadata: Metadata dictionary
        midi_note_min: Minimum MIDI note
        midi_note_max: Maximum MIDI note
        midi_note_median: Median MIDI note
    """
    # Create drumkit.xml file
    create_drumkit_xml(instruments, args.target, metadata)

    # Create midimap.xml file
    create_midimap_xml(
        instruments,
        args.target,
        midi_note_min=midi_note_min,
        midi_note_max=midi_note_max,
        midi_note_median=midi_note_median,
        metadata=metadata,
    )


def print_metadata(metadata: Dict[str, Any]) -> None:
    """
    Print metadata information.

    Args:
        metadata: Dictionary containing metadata
    """
    print("\n=== Kit metadata ===", file=sys.stderr)
    for key, value in metadata.items():
        print(f"  {key}: {value}", file=sys.stderr)


def print_samples_info(samples: List[str], source_dir: str) -> None:
    """
    Print information about the source samples.

    Args:
        samples: List of audio sample paths
        source_dir: Source directory
    """
    print("\n=== Source samples ===", file=sys.stderr)
    print(f"Searching for samples in: {source_dir}", file=sys.stderr)
    print(f"Number of samples found: {len(samples)}", file=sys.stderr)

    if not samples:
        print("Error: No audio samples found in the source directory", file=sys.stderr)
        sys.exit(1)

    # Sort samples alphabetically by filename
    samples.sort(key=lambda x: os.path.basename(x).lower())
    print("Samples sorted alphabetically", file=sys.stderr)

    # Print source samples list
    print("\nSamples list:", file=sys.stderr)
    for sample in samples:
        print(f"  {os.path.basename(sample)}", file=sys.stderr)


def copy_additional_files(args: argparse.Namespace, metadata: Dict[str, Any]) -> List[str]:
    """
    Copy logo and extra files.

    Args:
        args: Command line arguments
        metadata: Metadata dictionary

    Returns:
        List of copied files
    """
    extra_files_copied = []

    # Copy logo if specified
    if "logo" in metadata and metadata["logo"]:
        print("\n=== Copying logo file ===", file=sys.stderr)
        logo_copied = copy_logo_file(args.source, args.target, metadata["logo"])
        if logo_copied:
            extra_files_copied.append(metadata["logo"])

    # Copy extra files if specified
    if "extra_files" in metadata and metadata["extra_files"]:
        print("\n=== Copying extra files ===", file=sys.stderr)
        extra_files = copy_extra_files(args.source, args.target, metadata["extra_files"])
        if extra_files:
            extra_files_copied.extend(extra_files)

    return extra_files_copied


def main() -> None:
    """
    Main function for the DrumGizmo kit generator.
    Parses arguments, prepares metadata, searches for samples, processes each sample,
    creates XML files, copies logo and extra files, and displays a summary.
    """
    # Parse command line arguments
    args = parse_arguments()

    # Print verbose mode status
    if args.verbose:
        print("Verbose mode enabled", file=sys.stderr)

    # Validate source directory
    if not os.path.isdir(args.source):
        print(f"Error: Source directory does not exist: {args.source}", file=sys.stderr)
        sys.exit(1)

    # Validate target directory
    target_parent = os.path.dirname(os.path.abspath(args.target))
    if not os.path.exists(target_parent):
        print(f"Error: Target parent directory does not exist: {target_parent}", file=sys.stderr)
        sys.exit(1)

    # Print source and target directories
    print(f"Source directory: {args.source}", file=sys.stderr)
    print(f"Target directory: {args.target}", file=sys.stderr)

    # Prepare metadata
    metadata = prepare_metadata(args)

    # Get validated MIDI parameters and update metadata
    metadata["midi_note_min"] = int(metadata.get("midi_note_min", DEFAULT_MIDI_NOTE_MIN))
    metadata["midi_note_max"] = int(metadata.get("midi_note_max", DEFAULT_MIDI_NOTE_MAX))
    metadata["midi_note_median"] = int(metadata.get("midi_note_median", DEFAULT_MIDI_NOTE_MEDIAN))

    # Get validated velocity levels and update metadata
    metadata["velocity_levels"] = int(metadata.get("velocity_levels", DEFAULT_VELOCITY_LEVELS))

    # Print metadata
    print_metadata(metadata)

    # Use metadata values directly
    midi_note_min = metadata["midi_note_min"]
    midi_note_max = metadata["midi_note_max"]
    midi_note_median = metadata["midi_note_median"]
    velocity_levels = metadata["velocity_levels"]

    # Find audio samples
    print_verbose("Searching for audio samples...", args)
    # Convertir extensions en chaîne de caractères si c'est une liste
    extensions = metadata.get("extensions", DEFAULT_EXTENSIONS)
    if isinstance(extensions, list):
        extensions = ",".join(extensions)
    samples = find_audio_files(args.source, extensions, args)

    # Print samples information
    print_samples_info(samples, args.source)

    # Exit if dry-run mode is enabled
    if args.dry_run:
        print("Dry run mode enabled. Exiting without generating the kit.", file=sys.stderr)
        sys.exit(0)

    # Prepare target directory (clean it after scanning source files)
    print("\n=== Preparing target directory ===", file=sys.stderr)
    prepare_target_directory(args.target)

    # Process each sample to create instruments
    print("\n=== Processing samples ===", file=sys.stderr)
    print_verbose("Starting sample processing...", args)
    instruments, instrument_to_sample = process_instruments(
        samples, args, velocity_levels, metadata.get("samplerate"), metadata
    )

    # Create XML files
    print("\n=== Creating XML files ===", file=sys.stderr)
    create_xml_files(instruments, args, metadata, midi_note_min, midi_note_max, midi_note_median)

    # Copy logo and extra files
    extra_files_copied = copy_additional_files(args, metadata)

    # Display summary
    print("\n=== Summary ===", file=sys.stderr)
    print_summary(metadata, instruments, args.target)

    # Print mapping of instruments to original sample files
    print_instrument_mapping(instrument_to_sample)

    # Print extra files copied
    if extra_files_copied:
        print_extra_files(extra_files_copied)

    # Print success message
    print("\nKit generation completed successfully!", file=sys.stderr)


if __name__ == "__main__":
    main()
