#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XML generator module for DrumGizmo kit generator.

This module contains functions for generating XML files for DrumGizmo kits.
"""

import datetime
import os
import sys
import xml.dom.minidom
import xml.etree.ElementTree as ET

from drumgizmo_kits_generator.config import CHANNELS, MAIN_CHANNELS
from drumgizmo_kits_generator.constants import APP_LINK, APP_NAME, APP_VERSION


def write_pretty_xml(tree, file_path):
    """
    Write an ElementTree to a file with pretty formatting.

    Args:
        tree (ElementTree): The ElementTree to write
        file_path (str): Path to the output file
    """
    # Convert to string
    xml_string = ET.tostring(tree.getroot(), encoding="UTF-8", xml_declaration=True)

    # Parse with minidom
    dom = xml.dom.minidom.parseString(xml_string)

    # Write pretty XML to file
    with open(file_path, "w", encoding="UTF-8") as f:
        f.write(dom.toprettyxml(indent="  "))


def create_xml_file(instrument, kit_dir, extension, velocity_levels=10):
    """
    Creates the XML file for an instrument.

    Args:
        instrument (str): Name of the instrument
        kit_dir (str): Target directory for the kit
        extension (str): Audio file extension (with the dot)
        velocity_levels (int): Number of velocity levels to generate (default: 10)
    """
    xml_file = os.path.join(kit_dir, instrument, f"{instrument}.xml")

    print(f"Creating XML file: {xml_file}", file=sys.stderr)

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

        sample = ET.SubElement(samples, "sample", name=f"{instrument}-{i}", power=f"{power:.6f}")

        # Add audiofiles for each channel
        # Alternate filechannel between channels to use both stereo channels
        for index, channel in enumerate(CHANNELS):
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

    # Create instrument directory if it doesn't exist
    os.makedirs(os.path.dirname(xml_file), exist_ok=True)

    # Write the XML file with pretty formatting
    write_pretty_xml(tree, xml_file)

    print(f"XML file successfully created: {xml_file}", file=sys.stderr)
    return xml_file


# pylint: disable-next=too-many-locals
def create_drumkit_xml(instruments, kit_dir, metadata):
    """
    Creates the drumkit.xml file for the kit.

    Args:
        instruments (list): List of instrument names
        kit_dir (str): Target directory for the kit
        metadata (dict): Kit metadata

    Returns:
        str: Path to the created XML file
    """
    xml_file = os.path.join(kit_dir, "drumkit.xml")

    print("Creating drumkit.xml file", file=sys.stderr)

    # Create root element with attributes expected by tests
    root = ET.Element(
        "drumkit",
        version=metadata.get("version", "1.0"),
        name=metadata.get("name", "DrumGizmo Kit"),
        samplerate=metadata.get("samplerate", "44100"),
    )

    # Add metadata section as expected by tests
    metadata_elem = ET.SubElement(root, "metadata")

    title = ET.SubElement(metadata_elem, "title")
    title.text = metadata.get("name", "DrumGizmo Kit")

    description = ET.SubElement(metadata_elem, "description")
    description.text = metadata.get("description", "DrumGizmo kit")

    if "notes" in metadata:
        notes = ET.SubElement(metadata_elem, "notes")
        notes.text = metadata["notes"]

    license_elem = ET.SubElement(metadata_elem, "license")
    license_elem.text = metadata.get("license", "Private license")

    author = ET.SubElement(metadata_elem, "author")
    author.text = metadata.get("author", "Unknown")

    samplerate = ET.SubElement(metadata_elem, "samplerate")
    samplerate.text = metadata.get("samplerate", "44100")

    if "website" in metadata:
        website = ET.SubElement(metadata_elem, "website")
        website.text = metadata["website"]

    if "logo" in metadata:
        # pylint: disable-next=unused-variable
        logo = ET.SubElement(metadata_elem, "logo", src=metadata["logo"])

    # Add generation timestamp with app information
    created = ET.SubElement(metadata_elem, "created")
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    created.text = f"Generated on {current_time} with {APP_NAME} v{APP_VERSION} ({APP_LINK})"

    # Add channels
    channels_elem = ET.SubElement(root, "channels")

    for channel in CHANNELS:
        ET.SubElement(channels_elem, "channel", name=channel)

    # Add instruments
    instruments_elem = ET.SubElement(root, "instruments")

    # Add each instrument from the provided list
    for instrument in instruments:
        instrument_elem = ET.SubElement(
            instruments_elem, "instrument", name=instrument, file=f"{instrument}/{instrument}.xml"
        )

        # Add channelmaps for each channel
        for channel in CHANNELS:
            if channel in MAIN_CHANNELS:
                ET.SubElement(
                    instrument_elem, "channelmap", **{"in": channel, "out": channel, "main": "true"}
                )
            else:
                ET.SubElement(instrument_elem, "channelmap", **{"in": channel, "out": channel})

    # Create XML tree
    tree = ET.ElementTree(root)

    # Write the XML file with pretty formatting
    write_pretty_xml(tree, xml_file)

    print(f"drumkit.xml file successfully created: {xml_file}", file=sys.stderr)
    return xml_file


def create_midimap_xml(instruments, kit_dir):
    """
    Creates the midimap.xml file for the kit.

    Args:
        instruments (list): List of instrument names
        kit_dir (str): Target directory for the kit

    Returns:
        str: Path to the created XML file
    """
    xml_file = os.path.join(kit_dir, "midimap.xml")

    print("Creating midimap.xml file", file=sys.stderr)

    # Create root element
    root = ET.Element("midimap")

    # Sort instruments alphabetically
    sorted_instruments = sorted(instruments, key=lambda x: x.lower())

    # Print the MIDI mapping
    print("\nMIDI mapping (alphabetical order):", file=sys.stderr)

    # Add instruments to midimap, starting from MIDI note 35
    for i, instrument in enumerate(sorted_instruments):
        midi_note = 35 + i
        print(f"  MIDI Note {midi_note}: {instrument}", file=sys.stderr)

        # Add instrument to midimap using the format expected by tests
        ET.SubElement(root, "map", note=str(midi_note), instr=instrument, velmin="0", velmax="127")

    # Create XML tree
    tree = ET.ElementTree(root)

    # Write the XML file with pretty formatting
    write_pretty_xml(tree, xml_file)

    print(f"midimap.xml file successfully created: {xml_file}", file=sys.stderr)
    return xml_file
