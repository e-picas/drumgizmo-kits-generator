#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SPDX-License-Identifier: MIT
SPDX-PackageName: DrumGizmo kits generator
SPDX-PackageHomePage: https://github.com/e-picas/drumgizmo-kits-generator
SPDX-FileCopyrightText: 2025 Pierre Cassat (Picas)

Command-line interface for the DrumGizmo Kit Generator.
"""

import argparse
import sys

from drumgizmo_kits_generator import constants


def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments.

    Returns:
        argparse.Namespace: Parsed command line arguments

    Notes:
    * we should not define a default value as cli parameters have the top precedence (they are loaded last)
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
        "-r",
        "--raw-output",
        action="store_true",
        help="Do not include ANSI characters in output (for automatic processing)",
    )
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
    parser.add_argument(
        "--variations-method",
        choices=constants.ALLOWED_VARIATIONS_METHOD,
        help=f"Mathematical formula to use to generate volume variations (default: `{constants.DEFAULT_VARIATIONS_METHOD}`)",
    )

    return parser.parse_args()
