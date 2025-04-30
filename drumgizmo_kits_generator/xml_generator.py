#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XML generation utilities for DrumGizmo kits.
"""
import datetime
import os
import sys
import xml.dom.minidom
import xml.etree.ElementTree as ET
import xml.parsers.expat
from typing import Any, Dict, List, Optional

from drumgizmo_kits_generator.config import get_channels, get_main_channels
from drumgizmo_kits_generator.constants import (
    APP_LINK,
    APP_NAME,
    APP_VERSION,
    DEFAULT_LICENSE,
    DEFAULT_MIDI_NOTE_MAX,
    DEFAULT_MIDI_NOTE_MEDIAN,
    DEFAULT_MIDI_NOTE_MIN,
    DEFAULT_NAME,
    DEFAULT_SAMPLERATE,
    DEFAULT_VELOCITY_LEVELS,
    DEFAULT_VERSION,
)


def write_pretty_xml(tree: ET.ElementTree, file_path: str) -> bool:
    """
    Write an ElementTree to a file with pretty formatting.

    Args:
        tree: The ElementTree to write
        file_path: Path to the output file

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Convert to string
        xml_string = ET.tostring(tree.getroot(), encoding="UTF-8", xml_declaration=True)

        # Parse with minidom
        dom = xml.dom.minidom.parseString(xml_string)

        # Write pretty XML to file
        with open(file_path, "w", encoding="UTF-8") as f:
            f.write(dom.toprettyxml(indent="  "))

        return True
    except (OSError, IOError) as e:
        print(f"Error writing XML file {file_path}: File system error: {e}", file=sys.stderr)
        return False
    except xml.parsers.expat.ExpatError as e:
        print(f"Error writing XML file {file_path}: XML parsing error: {e}", file=sys.stderr)
        return False
    except ET.ParseError as e:
        print(
            f"Error writing XML file {file_path}: ElementTree parsing error: {e}", file=sys.stderr
        )
        return False


def create_instrument_xml(
    instrument: str, kit_dir: str, extension: str, velocity_levels: int = DEFAULT_VELOCITY_LEVELS
) -> Optional[str]:
    """
    Creates the XML file for an instrument.

    Args:
        instrument: Name of the instrument
        kit_dir: Target directory for the kit
        extension: Audio file extension (with the dot)
        velocity_levels: Number of velocity levels to generate

    Returns:
        Path to the created XML file or None if creation failed
    """
    xml_file = os.path.join(kit_dir, instrument, f"{instrument}.xml")

    print(f"Creating XML file: {xml_file}", file=sys.stderr)

    try:
        # Create the root element
        root = ET.Element("instrument", version="2.0", name=instrument)

        # Create samples element
        samples = ET.SubElement(root, "samples")

        # Add velocity_levels samples with power values from 0 to 1
        for i in range(1, velocity_levels + 1):
            # Calculate power value (0-1) based on volume
            # Sample 1 (100% volume) -> power=1.0
            # Last sample (lowest volume) -> power=1/velocity_levels
            power = 1.0 - ((i - 1) / velocity_levels)

            sample = ET.SubElement(
                samples, "sample", name=f"{instrument}-{i}", power=f"{power:.6f}"
            )

            # Add audiofiles for each channel
            # Alternate filechannel between channels to use both stereo channels
            for index, channel in enumerate(get_channels()):
                # Alternate between filechannel 1 and 2 based on channel index
                filechannel = "1" if index % 2 == 0 else "2"

                ET.SubElement(
                    sample,
                    "audiofile",
                    channel=channel,
                    file=f"samples/{i}-{instrument}{extension}",
                    filechannel=filechannel,
                )

        # Create XML tree
        tree = ET.ElementTree(root)

        # Write the XML file with pretty formatting
        if write_pretty_xml(tree, xml_file):
            print(f"XML file successfully created: {xml_file}", file=sys.stderr)
            return xml_file
        return None
    except ET.ParseError as e:
        print(
            f"Error creating instrument XML file for {instrument}: XML parsing error: {e}",
            file=sys.stderr,
        )
        return None
    except (OSError, IOError) as e:
        print(
            f"Error creating instrument XML file for {instrument}: File system error: {e}",
            file=sys.stderr,
        )
        return None
    except ValueError as e:
        print(
            f"Error creating instrument XML file for {instrument}: Value error: {e}",
            file=sys.stderr,
        )
        return None
    except TypeError as e:
        print(
            f"Error creating instrument XML file for {instrument}: Type error: {e}", file=sys.stderr
        )
        return None


def add_metadata_elements(metadata_elem: ET.Element, metadata: Dict[str, Any]) -> None:
    """
    Add metadata elements to the provided metadata XML element.

    Args:
        metadata_elem: The XML metadata element to add to
        metadata: Dictionary of metadata values
    """
    # Add title (required by tests)
    title = ET.SubElement(metadata_elem, "title")
    title.text = metadata.get("name", DEFAULT_NAME)

    # Add description if available
    description = ET.SubElement(metadata_elem, "description")
    description.text = metadata.get("description", "")

    # Add notes if available
    notes = ET.SubElement(metadata_elem, "notes")
    notes.text = metadata.get("notes", "")

    # Add author information
    author = ET.SubElement(metadata_elem, "author")
    author.text = metadata.get("author", "")

    # Add license information
    license_elem = ET.SubElement(metadata_elem, "license")
    license_elem.text = metadata.get("license", DEFAULT_LICENSE)

    # Add samplerate information (required by tests)
    samplerate_elem = ET.SubElement(metadata_elem, "samplerate")
    samplerate_elem.text = metadata.get("samplerate", DEFAULT_SAMPLERATE)

    # Add website information if available
    if "website" in metadata:
        website = ET.SubElement(metadata_elem, "website")
        website.text = metadata["website"]

    # Add logo information if available
    if "logo" in metadata:
        logo = ET.SubElement(metadata_elem, "logo")
        logo.text = metadata["logo"]

    # Add creation timestamp with app information (required by tests)
    created = ET.SubElement(metadata_elem, "created")
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    created.text = f"Generated on {current_time} with {APP_NAME} v{APP_VERSION} ({APP_LINK})"


def add_channels_element(root: ET.Element) -> None:
    """
    Add channels element to the root XML element.

    Args:
        root: The root XML element to add channels to
    """
    # Add channels section
    channels_elem = ET.SubElement(root, "channels")

    # Add each channel
    for channel in get_channels():
        if channel in get_main_channels():
            ET.SubElement(channels_elem, "channel", name=channel, main="true")
        else:
            ET.SubElement(channels_elem, "channel", name=channel)


def add_instruments_element(root: ET.Element, instruments: List[str]) -> None:
    """
    Add instruments element to the root XML element.

    Args:
        root: The root XML element to add instruments to
        instruments: List of instrument names
    """
    # Add instruments section
    instruments_elem = ET.SubElement(root, "instruments")

    # Add each instrument from the provided list
    for instrument in instruments:
        instrument_elem = ET.SubElement(
            instruments_elem, "instrument", name=instrument, file=f"{instrument}/{instrument}.xml"
        )

        # Add channelmaps for each channel
        for channel in get_channels():
            if channel in get_main_channels():
                ET.SubElement(
                    instrument_elem, "channelmap", **{"in": channel, "out": channel, "main": "true"}
                )
            else:
                ET.SubElement(instrument_elem, "channelmap", **{"in": channel, "out": channel})


def create_drumkit_xml(
    instruments: List[str], kit_dir: str, metadata: Dict[str, Any]
) -> Optional[str]:
    """
    Creates the drumkit.xml file for the kit.

    Args:
        instruments: List of instrument names
        kit_dir: Target directory for the kit
        metadata: Kit metadata

    Returns:
        Path to the created XML file or None if creation failed
    """
    xml_file = os.path.join(kit_dir, "drumkit.xml")
    result = None

    print("Creating drumkit.xml file", file=sys.stderr)

    try:
        # Create root element with attributes expected by tests
        root = ET.Element(
            "drumkit",
            version=metadata.get("version", DEFAULT_VERSION),
            name=metadata.get("name", DEFAULT_NAME),
            samplerate=metadata.get("samplerate", DEFAULT_SAMPLERATE),
        )

        # Add metadata section
        metadata_elem = ET.SubElement(root, "metadata")
        add_metadata_elements(metadata_elem, metadata)

        # Add channels section
        add_channels_element(root)

        # Add instruments section
        add_instruments_element(root, instruments)

        # Create XML tree
        tree = ET.ElementTree(root)

        # Write the XML file with pretty formatting
        if write_pretty_xml(tree, xml_file):
            print(f"drumkit.xml file successfully created: {xml_file}", file=sys.stderr)
            result = xml_file
    except ET.ParseError as e:
        print(f"Error creating drumkit XML file: XML parsing error: {e}", file=sys.stderr)
    except (OSError, IOError) as e:
        print(f"Error creating drumkit XML file: File system error: {e}", file=sys.stderr)
    except KeyError as e:
        print(f"Error creating drumkit XML file: Missing key in metadata: {e}", file=sys.stderr)
    except ValueError as e:
        print(f"Error creating drumkit XML file: Value error: {e}", file=sys.stderr)
    except TypeError as e:
        print(f"Error creating drumkit XML file: Type error: {e}", file=sys.stderr)

    return result


def calculate_midi_start_note(
    num_instruments: int, midi_note_median: int, midi_note_min: int, midi_note_max: int
) -> int:
    """
    Calculate the starting MIDI note for instrument distribution.

    Args:
        num_instruments: Number of instruments to distribute
        midi_note_median: Median MIDI note to distribute around
        midi_note_min: Minimum allowed MIDI note
        midi_note_max: Maximum allowed MIDI note

    Returns:
        Starting MIDI note for instrument distribution
    """
    # If we have an even number of instruments, we'll place half before the median and half after
    # If we have an odd number, we'll place the middle instrument at the median
    if num_instruments % 2 == 0:  # Even number of instruments
        start_note = midi_note_median - (num_instruments // 2)
    else:  # Odd number of instruments
        start_note = midi_note_median - (num_instruments // 2)

    # Ensure we don't go below the minimum note
    start_note = max(start_note, midi_note_min)

    # Ensure we don't go above the maximum note
    end_note = start_note + num_instruments - 1
    if end_note > midi_note_max:
        # If we would exceed the maximum, shift the start note down
        shift = end_note - midi_note_max
        start_note = max(midi_note_min, start_note - shift)

        # If we still can't fit all instruments, we'll need to warn the user
        if start_note + num_instruments - 1 > midi_note_max:
            print(
                f"Warning: Cannot fit all {num_instruments} instruments within the MIDI note range "
                f"{midi_note_min}-{midi_note_max}. Some instruments will not be mapped.",
                file=sys.stderr,
            )

    return start_note


def create_midimap_xml(
    instruments: List[str],
    kit_dir: str,
    midi_note_min: int = DEFAULT_MIDI_NOTE_MIN,
    midi_note_max: int = DEFAULT_MIDI_NOTE_MAX,
    midi_note_median: int = DEFAULT_MIDI_NOTE_MEDIAN,
) -> Optional[str]:
    """
    Creates the midimap.xml file for the kit.

    Args:
        instruments: List of instrument names
        kit_dir: Target directory for the kit
        midi_note_min: Minimum MIDI note number allowed
        midi_note_max: Maximum MIDI note number allowed
        midi_note_median: Median MIDI note for distributing instruments around

    Returns:
        Path to the created XML file or None if creation failed
    """
    xml_file = os.path.join(kit_dir, "midimap.xml")

    print("Creating midimap.xml file", file=sys.stderr)

    try:
        # Create root element
        root = ET.Element("midimap")

        # Sort instruments alphabetically
        sorted_instruments = sorted(instruments, key=lambda x: x.lower())

        # Calculate MIDI note distribution
        num_instruments = len(sorted_instruments)

        # Calculate start note based on number of instruments and median
        start_note = calculate_midi_start_note(
            num_instruments, midi_note_median, midi_note_min, midi_note_max
        )

        # Print the MIDI mapping
        print("\nMIDI mapping (alphabetical order):", file=sys.stderr)

        # Add instruments to midimap
        for i, instrument in enumerate(sorted_instruments):
            midi_note = start_note + i

            # Skip if outside the allowed range
            if midi_note < midi_note_min or midi_note > midi_note_max:
                print(
                    f"  Warning: Skipping {instrument} (would be assigned to note {midi_note})",
                    file=sys.stderr,
                )
                continue

            print(f"  MIDI Note {midi_note}: {instrument}", file=sys.stderr)

            # Add instrument to midimap
            ET.SubElement(
                root, "map", note=str(midi_note), instr=instrument, velmin="0", velmax="127"
            )

        # Create XML tree
        tree = ET.ElementTree(root)

        # Write the XML file with pretty formatting
        if write_pretty_xml(tree, xml_file):
            print(f"midimap.xml file successfully created: {xml_file}", file=sys.stderr)
            return xml_file
        return None
    except ET.ParseError as e:
        print(f"Error creating midimap XML file: XML parsing error: {e}", file=sys.stderr)
        return None
    except (OSError, IOError) as e:
        print(f"Error creating midimap XML file: File system error: {e}", file=sys.stderr)
        return None
    except ValueError as e:
        print(f"Error creating midimap XML file: Value error: {e}", file=sys.stderr)
        return None
    except TypeError as e:
        print(f"Error creating midimap XML file: Type error: {e}", file=sys.stderr)
        return None
