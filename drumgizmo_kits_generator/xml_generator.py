#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SPDX-License-Identifier: MIT
SPDX-PackageName: DrumGizmo kits generator
SPDX-PackageHomePage: https://github.com/e-picas/drumgizmo-kits-generator
SPDX-FileCopyrightText: 2025 Pierre Cassat (Picas)

XML generation utilities for DrumGizmo kits.
"""

import datetime
import os
import xml.dom.minidom
import xml.etree.ElementTree as ET
from typing import Any, Dict, List

from drumgizmo_kits_generator import constants, logger


def _add_metadata_elements(metadata_elem: ET.Element, metadata: Dict[str, Any]) -> None:
    """
    Add metadata elements to the metadata element of a drumkit XML.
    Args:
        metadata_elem: The metadata XML element
        metadata: Metadata dictionary
    """
    # Add title (same as name)
    title_elem = ET.SubElement(metadata_elem, "title")
    title_elem.text = metadata["name"]

    # Add version
    version_elem = ET.SubElement(metadata_elem, "version")
    version_elem.text = metadata.get("version")

    # Add description
    if metadata.get("description"):
        description_elem = ET.SubElement(metadata_elem, "description")
        description_elem.text = metadata["description"]

    # Add notes
    notes_elem = ET.SubElement(metadata_elem, "notes")
    if metadata.get("notes"):
        notes_text = metadata["notes"]
    else:
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        notes_text = (
            f"DrumGizmo kit generated with drumgizmo-kits-generator - Generated at {current_time}"
        )
    notes_elem.text = notes_text

    # Add author
    if metadata.get("author"):
        author_elem = ET.SubElement(metadata_elem, "author")
        author_elem.text = metadata["author"]

    # Add license
    license_elem = ET.SubElement(metadata_elem, "license")
    license_elem.text = metadata.get("license")

    # Add samplerate
    samplerate_elem = ET.SubElement(metadata_elem, "samplerate")
    samplerate_elem.text = str(metadata["samplerate"])

    # Add website
    if metadata.get("website"):
        website_elem = ET.SubElement(metadata_elem, "website")
        website_elem.text = metadata["website"]

    # Add logo
    if metadata.get("logo"):
        logo_elem = ET.SubElement(metadata_elem, "logo")
        logo_elem.set("src", metadata["logo"])

    # Add created timestamp
    created_elem = ET.SubElement(metadata_elem, "created")
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    created_elem.text = (
        f"Generated on {current_time} with {constants.APP_NAME} "
        f"v{constants.APP_VERSION} ({constants.APP_LINK})"
    )


# pylint: disable=too-many-locals
def generate_drumkit_xml(
    target_dir: str, instrument_names: List[str], metadata: Dict[str, Any]
) -> None:
    """
    Generate the drumkit.xml file for a DrumGizmo kit.

    Args:
        target_dir: Path to the target directory
        metadata: Metadata for the drumkit
    """
    xml_path = os.path.join(target_dir, "drumkit.xml")
    logger.debug(f"Generating drumkit XML at '{xml_path}'")

    # Create the root element
    root = ET.Element("drumkit")
    root.set("version", "1.0")
    root.set("name", metadata["name"])
    root.set("samplerate", str(metadata["samplerate"]))

    # Add metadata
    metadata_elem = ET.SubElement(root, "metadata")
    _add_metadata_elements(metadata_elem, metadata)

    # Add channels
    channels_elem = ET.SubElement(root, "channels")
    for channel in metadata["channels"]:
        channel_elem = ET.SubElement(channels_elem, "channel")
        channel_elem.set("name", channel)

    # Add instruments section
    instruments_elem = ET.SubElement(root, "instruments")

    # Add each instrument
    for instrument_name in instrument_names:
        instrument_elem = ET.SubElement(instruments_elem, "instrument")
        instrument_elem.set("name", instrument_name)
        instrument_elem.set("file", f"{instrument_name}/{instrument_name}.xml")

        # Add channel mappings
        for channel in metadata["channels"]:
            channelmap_elem = ET.SubElement(instrument_elem, "channelmap")
            channelmap_elem.set("in", channel)
            channelmap_elem.set("out", channel)

            # Mark main channels
            if channel in metadata["main_channels"]:
                channelmap_elem.set("main", "true")

    # Pretty print the XML
    xml_string = ET.tostring(root, encoding="utf-8")
    pretty_xml = xml.dom.minidom.parseString(xml_string).toprettyxml(indent="  ")

    with open(xml_path, "w", encoding="utf-8") as f:
        f.write(pretty_xml)


def _add_instrument_samples(
    samples_elem: ET.Element,
    metadata: Dict[str, Any],
    instrument_name: str,
    original_ext: str,
    instrument_channels: int = 1,
) -> None:
    """
    Add sample elements to the samples element of an instrument XML.

    Args:
        samples_elem: The samples XML element
        metadata: Metadata dictionary
        instrument_name: Name of the instrument
        original_ext: File extension for audio files
        instrument_channels: Number of channels of the original sample
    """
    # Get velocity levels
    velocity_levels = metadata.get("velocity_levels", constants.DEFAULT_VELOCITY_LEVELS)

    # Add a sample for each velocity level
    for i in range(1, velocity_levels + 1):
        sample_elem = ET.SubElement(samples_elem, "sample")
        sample_elem.set("name", f"{instrument_name}-{i}")

        # Calculate power based on velocity level using cartesian division
        # First sample (i=1) gets power=1.0, then decreases
        power = (velocity_levels - i + 1) / velocity_levels

        sample_elem.set("power", f"{power:.6f}")

        # Add audiofile elements for each channel
        for j, channel in enumerate(metadata["channels"]):
            audiofile_elem = ET.SubElement(sample_elem, "audiofile")
            audiofile_elem.set("channel", channel)
            audiofile_elem.set("file", f"samples/{i}-{instrument_name}{original_ext}")

            # Set filechannel index based on position in instrument_channels (starting from 1)
            filechannel = str((j % instrument_channels) + 1)
            audiofile_elem.set("filechannel", filechannel)


# pylint: disable=too-many-locals
def generate_instrument_xml(
    target_dir: str,
    instrument_name: str,
    audio_sources: Dict[str, Dict[str, Any]],
    audio_files: Dict[str, Dict[str, Any]],
    metadata: Dict[str, Any],
) -> None:
    """
    Generate the instrument.xml file for a DrumGizmo instrument.

    Args:
        target_dir: Path to the target directory
        instrument_name: Name of the instrument
        audio_files: Dict containing at least 'config', 'audio_files', and 'audio_files_processed' keys
    """
    instrument_files = audio_files.get(instrument_name)

    instrument_dir = os.path.join(target_dir, instrument_name)
    xml_path = os.path.join(instrument_dir, f"{instrument_name}.xml")
    instrument_channels = 1

    if audio_sources.get(instrument_name) is None:
        logger.debug(f"No audio_files entry found for {instrument_name}, fallback to channels=1")
    else:
        instrument_channels = audio_sources.get(instrument_name).get("channels", 1)
        logger.debug(f"Detected {instrument_channels} channels for {instrument_name}")

    logger.debug(
        f"Generating instrument XML for '{instrument_name}' at '{xml_path}'"
        f" with {instrument_channels} channel(s)"
    )

    # Create instrument directory if it doesn't exist
    os.makedirs(instrument_dir, exist_ok=True)

    # Create the root element
    root = ET.Element("instrument")
    root.set("version", "2.0")
    root.set("name", instrument_name)

    # Add samples section
    samples_elem = ET.SubElement(root, "samples")

    # Get the original file extension from the first audio file
    original_ext = ".wav"  # Default extension
    if instrument_files:
        for file_path in instrument_files:
            if instrument_name in os.path.basename(file_path):
                _, original_ext = os.path.splitext(file_path)
                break

    # Add samples
    _add_instrument_samples(
        samples_elem, metadata, instrument_name, original_ext, instrument_channels
    )

    # Pretty print the XML
    xml_string = ET.tostring(root, encoding="utf-8")
    pretty_xml = xml.dom.minidom.parseString(xml_string).toprettyxml(indent="  ")

    with open(xml_path, "w", encoding="utf-8") as f:
        f.write(pretty_xml)


def _add_midimap_elements(root: ET.Element, midi_mapping: Dict[str, int]) -> Dict[str, int]:
    """
    Add mapping elements to the midimap XML.

    Args:
        root: The root XML element
        instruments: List of instrument names
        midi_params: Dictionary with MIDI parameters (min, max, median)
    Returns:
        A dictionary with the MIDI mapping
    """
    # Generate notes for each instrument
    for instrument_name, note in midi_mapping.items():
        # Create the map element
        map_elem = ET.SubElement(root, "map")
        map_elem.set("note", str(note))
        map_elem.set("instr", instrument_name)
        map_elem.set("velmin", "0")
        map_elem.set("velmax", "127")

        # Store MIDI mapping
        midi_mapping[instrument_name] = note

    return midi_mapping


def generate_midimap_xml(target_dir: str, midi_mapping: Dict[str, int]) -> None:
    """
    Generate the midimap.xml file for a DrumGizmo kit.

    Args:
        target_dir: Path to the target directory
        metadata: Metadata for the midimap
    """
    xml_path = os.path.join(target_dir, "midimap.xml")
    logger.debug(f"Generating midimap XML at '{xml_path}'")

    # Create the root element
    root = ET.Element("midimap")

    if not midi_mapping:
        logger.warning("No instruments found for MIDI mapping")
        return

    # Add mapping elements
    _add_midimap_elements(root, midi_mapping)

    # Pretty print the XML
    xml_string = ET.tostring(root, encoding="utf-8")
    pretty_xml = xml.dom.minidom.parseString(xml_string).toprettyxml(indent="  ")

    with open(xml_path, "w", encoding="utf-8") as f:
        f.write(pretty_xml)

    # Display MIDI mapping
    logger.debug("MIDI mapping (alphabetical order):")
    for instrument, note in sorted(midi_mapping.items(), key=lambda x: x[0]):
        logger.debug(f"  MIDI Note {note}: {instrument}")
