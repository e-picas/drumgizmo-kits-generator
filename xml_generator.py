#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XML generation module for DrumGizmo kit generator.
Contains functions to create the XML files needed for DrumGizmo kits.
"""

import os
import sys
import tempfile
import shutil
import datetime
from config import CHANNELS, MAIN_CHANNELS
from constants import APP_NAME, APP_VERSION, APP_LINK

def create_xml_file(instrument, kit_dir, extension):
    """
    Creates the XML file for an instrument.

    Args:
        instrument (str): Name of the instrument
        kit_dir (str): Target directory for the kit
        extension (str): Audio file extension (with the dot)
    """
    xml_file = os.path.join(kit_dir, instrument, f"{instrument}.xml")

    print(f"Creating XML file: {xml_file}", file=sys.stderr)

    # Create a temporary XML file
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp:
        # Write XML header
        temp.write(f"""<?xml version='1.0' encoding='UTF-8'?>
<instrument version="2.0" name="{instrument}">
  <samples>
""")

        # Add 10 samples with power values from 0 to 1
        for i in range(1, 11):
            # Calculate power value (0-1) based on volume
            # Sample 1 (100% volume) -> power=1.0
            # Sample 10 (10% volume) -> power=0.1
            power = 1.0 - (i-1) * 0.1

            temp.write(f"""    <sample name="{instrument}-{i}" power="{power:.6f}">
""")
            # Add audiofiles for each channel, but map them all to the available stereo channels (1 and 2)
            # For stereo files, we map left channels to filechannel 1 and right channels to filechannel 2
            for channel in CHANNELS:
                # Determine if this channel should use left (1) or right (2) audio channel
                if channel in ["AmbL", "Hihat", "Kdrum_back", "OHL", "Snare_bottom", "Tom1", "Tom2", "Tom3"]:
                    filechannel = "1"  # Left channel
                else:
                    filechannel = "2"  # Right channel

                temp.write(f"""      <audiofile channel="{channel}" file="samples/{i}-{instrument}{extension}" filechannel="{filechannel}"/>
""")
            temp.write("""    </sample>
""")

        # Add XML file ending
        temp.write("""  </samples>
</instrument>
""")

    # Move temporary file to final XML file
    shutil.move(temp.name, xml_file)

    print(f"XML file successfully created: {xml_file}", file=sys.stderr)

def create_drumkit_xml(instruments, kit_dir, metadata):
    """
    Creates the main drumkit.xml file.

    Args:
        instruments (list): List of instrument names
        kit_dir (str): Target directory for the kit
        metadata (dict): Kit metadata
    """
    drumkit_file = os.path.join(kit_dir, "drumkit.xml")

    print("Creating drumkit.xml file", file=sys.stderr)

    # Create a temporary XML file
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp:
        # Write XML header with proper metadata structure
        # Add samplerate attribute to the drumkit tag
        temp.write(f"""<?xml version="1.0" encoding="UTF-8"?>
<drumkit version="{metadata.get('version', '1.0.0')}" name="{metadata['name']}" samplerate="{metadata.get('samplerate', '44100')}">
 <metadata>
  <title>{metadata['name']}</title>
  <description>{metadata['description']}</description>
""")

        # Add notes if available
        if 'notes' in metadata and metadata['notes']:
            temp.write(f"""  <notes>{metadata['notes']}</notes>
""")

        # Add license, author, website, and samplerate
        temp.write(f"""  <license>{metadata.get('license', 'Private license')}</license>
  <author>{metadata.get('author', 'Unknown')}</author>
  <samplerate>{metadata.get('samplerate', '44100')}</samplerate>
""")

        # Add website if available
        if 'website' in metadata and metadata['website']:
            temp.write(f"""  <website>{metadata['website']}</website>
""")

        # Add logo if available - using the correct format with src attribute
        if 'logo' in metadata and metadata['logo']:
            temp.write(f"""  <logo src="{metadata['logo']}"/>
""")

        # Add generation timestamp with app information
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        temp.write(f"""  <created>Generated on {current_time} with {APP_NAME} v{APP_VERSION} ({APP_LINK})</created>
 </metadata>
 <channels>
""")

        for channel in CHANNELS:
            temp.write(f"""    <channel name="{channel}"/>
""")

        temp.write("""  </channels>
  <instruments>
""")

        # Add each instrument with channelmaps
        for instrument in instruments:
            temp.write(f"""    <instrument name="{instrument}" file="{instrument}/{instrument}.xml">
""")
            for channel in CHANNELS:
                if channel in MAIN_CHANNELS:
                    temp.write(f"""      <channelmap in="{channel}" out="{channel}" main="true"/>
""")
                else:
                    temp.write(f"""      <channelmap in="{channel}" out="{channel}"/>
""")

            temp.write("""    </instrument>
""")

        # Add XML file ending
        temp.write("""  </instruments>
</drumkit>
""")

    # Move temporary file to final XML file
    shutil.move(temp.name, drumkit_file)

    print(f"drumkit.xml file successfully created: {drumkit_file}", file=sys.stderr)

def create_midimap_xml(instruments, kit_dir):
    """
    Creates the midimap.xml file.

    Args:
        instruments (list): List of instrument names
        kit_dir (str): Target directory for the kit
    """
    midimap_file = os.path.join(kit_dir, "midimap.xml")

    print("Creating midimap.xml file", file=sys.stderr)

    # Sort instruments alphabetically to ensure consistent MIDI mapping
    sorted_instruments = sorted(instruments, key=lambda x: x.lower())

    # Create a temporary XML file
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp:
        # Write XML header
        temp.write("""<?xml version="1.0" encoding="UTF-8"?>
<midimap>
""")

        # Add each instrument with a different MIDI note in alphabetical order
        midi_note = 35  # Start with MIDI note 35 (standard for kick drum)

        # Create a mapping of instruments to MIDI notes for logging
        instrument_to_midi = {}

        for instrument in sorted_instruments:
            temp.write(f"""  <map note="{midi_note}" instr="{instrument}" velmin="0" velmax="127"/>
""")
            instrument_to_midi[instrument] = midi_note
            midi_note += 1
            # Avoid exceeding 81 (reasonable upper limit for drum MIDI notes)
            if midi_note > 81:
                print("Warning: Too many instruments, some will share MIDI note 81", file=sys.stderr)
                midi_note = 81

        # Add XML file ending
        temp.write("""</midimap>
""")

    # Move temporary file to final XML file
    shutil.move(temp.name, midimap_file)

    # Print the MIDI mapping for reference
    print("\nMIDI mapping (alphabetical order):", file=sys.stderr)
    for instrument, note in instrument_to_midi.items():
        print(f"  MIDI Note {note}: {instrument}", file=sys.stderr)

    print(f"midimap.xml file successfully created: {midimap_file}", file=sys.stderr)
