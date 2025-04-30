#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validation utilities for DrumGizmo kit generation.
"""
import argparse
import sys
from typing import Any, Dict, Tuple

from drumgizmo_kits_generator.constants import (
    DEFAULT_EXTENSIONS,
    DEFAULT_MIDI_NOTE_MAX,
    DEFAULT_MIDI_NOTE_MEDIAN,
    DEFAULT_MIDI_NOTE_MIN,
    DEFAULT_VELOCITY_LEVELS,
)


def validate_metadata_numeric_value(metadata: Dict[str, Any], key: str) -> None:
    """
    Validate a numeric metadata value and convert it to int if possible.
    If the value is invalid, remove it from the metadata.

    Args:
        metadata (Dict[str, Any]): Metadata dictionary
        key (str): Key to validate
    """
    if key in metadata:
        try:
            metadata[key] = int(metadata[key])

            # Validate that samplerate is greater than 0
            if key == "samplerate" and metadata[key] <= 0:
                print(
                    f"Warning: {key} must be greater than 0, using default",
                    file=sys.stderr,
                )
                metadata.pop(key)
        except ValueError:
            print(
                f"Warning: Invalid {key} value in config file: {metadata[key]}",
                file=sys.stderr,
            )
            metadata.pop(key)


def validate_midi_and_velocity_params(
    metadata: Dict[str, Any], args: argparse.Namespace
) -> Dict[str, Any]:
    """
    Validate MIDI and velocity parameters from metadata.

    Args:
        metadata (Dict[str, Any]): Metadata dictionary
        args (argparse.Namespace): Command line arguments

    Returns:
        Dict[str, Any]: Updated metadata dictionary
    """
    # Extract MIDI and velocity parameters from config file
    # These are stored in the metadata dictionary but will be extracted by the main function
    if "midi_note_min" in metadata and args.midi_note_min == DEFAULT_MIDI_NOTE_MIN:
        validate_metadata_numeric_value(metadata, "midi_note_min")

    if "midi_note_max" in metadata and args.midi_note_max == DEFAULT_MIDI_NOTE_MAX:
        validate_metadata_numeric_value(metadata, "midi_note_max")

    if "midi_note_median" in metadata and args.midi_note_median == DEFAULT_MIDI_NOTE_MEDIAN:
        validate_metadata_numeric_value(metadata, "midi_note_median")

    if "velocity_levels" in metadata and args.velocity_levels == DEFAULT_VELOCITY_LEVELS:
        validate_metadata_numeric_value(metadata, "velocity_levels")

    # Handle extensions from config file
    if "extensions" in metadata and args.extensions == DEFAULT_EXTENSIONS:
        extensions_value = metadata["extensions"]
        if not extensions_value:
            print(
                f"Warning: Invalid extensions value in config file: {metadata['extensions']}",
                file=sys.stderr,
            )
            metadata.pop("extensions")

    return metadata


def validate_midi_parameters(
    args: argparse.Namespace, metadata: Dict[str, Any]
) -> Tuple[int, int, int]:
    """
    Validate MIDI parameters and return corrected values if needed.

    Args:
        args: Command line arguments
        metadata: Metadata dictionary

    Returns:
        Tuple containing validated (midi_note_min, midi_note_max, midi_note_median)
    """
    # Get MIDI parameters from metadata or args
    # Note: metadata values come from the config file or command line arguments
    # that have already been processed in update_metadata_from_args
    midi_note_min = metadata.get("midi_note_min", args.midi_note_min)
    midi_note_max = metadata.get("midi_note_max", args.midi_note_max)
    midi_note_median = metadata.get("midi_note_median", args.midi_note_median)

    # Validate MIDI note min
    if not isinstance(midi_note_min, int) or midi_note_min < 0 or midi_note_min > 127:
        print(
            f"Warning: Invalid midi_note_min value: {midi_note_min}, using default {DEFAULT_MIDI_NOTE_MIN}",
            file=sys.stderr,
        )
        midi_note_min = DEFAULT_MIDI_NOTE_MIN

    # Validate MIDI note max
    if not isinstance(midi_note_max, int) or midi_note_max < 0 or midi_note_max > 127:
        print(
            f"Warning: Invalid midi_note_max value: {midi_note_max}, using default {DEFAULT_MIDI_NOTE_MAX}",
            file=sys.stderr,
        )
        midi_note_max = DEFAULT_MIDI_NOTE_MAX

    # Validate MIDI note median
    if not isinstance(midi_note_median, int) or midi_note_median < 0 or midi_note_median > 127:
        print(
            f"Warning: Invalid midi_note_median value: {midi_note_median}, using default {DEFAULT_MIDI_NOTE_MEDIAN}",
            file=sys.stderr,
        )
        midi_note_median = DEFAULT_MIDI_NOTE_MEDIAN

    # Validate relational constraints
    if midi_note_min > midi_note_max:
        print(
            f"Warning: midi_note_min ({midi_note_min}) is greater than midi_note_max ({midi_note_max}), adjusting to defaults",
            file=sys.stderr,
        )
        midi_note_min = DEFAULT_MIDI_NOTE_MIN
        midi_note_max = DEFAULT_MIDI_NOTE_MAX

    if midi_note_min > midi_note_median:
        print(
            f"Warning: midi_note_min ({midi_note_min}) is greater than midi_note_median ({midi_note_median}), adjusting midi_note_min to default",
            file=sys.stderr,
        )
        midi_note_min = DEFAULT_MIDI_NOTE_MIN

    if midi_note_max < midi_note_median:
        print(
            f"Warning: midi_note_max ({midi_note_max}) is less than midi_note_median ({midi_note_median}), adjusting midi_note_max to default",
            file=sys.stderr,
        )
        midi_note_max = DEFAULT_MIDI_NOTE_MAX

    return midi_note_min, midi_note_max, midi_note_median


def validate_velocity_levels(args: argparse.Namespace, metadata: Dict[str, Any]) -> int:
    """
    Validate velocity levels and return corrected value if needed.

    Args:
        args: Command line arguments
        metadata: Metadata dictionary

    Returns:
        Validated velocity_levels
    """
    # Get velocity levels from metadata or args
    # Note: metadata values come from the config file or command line arguments
    # that have already been processed in update_metadata_from_args
    try:
        velocity_levels = int(metadata.get("velocity_levels", args.velocity_levels))
    except (ValueError, TypeError):
        print(
            "Warning: Invalid velocity_levels value in metadata, using default",
            file=sys.stderr,
        )
        velocity_levels = args.velocity_levels

    # Validate velocity levels
    if velocity_levels < 1:
        print(
            f"Warning: Invalid velocity_levels value: {velocity_levels}, using default {DEFAULT_VELOCITY_LEVELS}",
            file=sys.stderr,
        )
        velocity_levels = DEFAULT_VELOCITY_LEVELS

    return velocity_levels
