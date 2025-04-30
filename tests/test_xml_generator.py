#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=import-outside-toplevel,wrong-import-position
"""
Unit tests for the XML generator module of the DrumGizmo kit generator.

These tests verify the functionality of XML generation for DrumGizmo kits,
including the creation of drumkit.xml, instrument XML files, and midimap.xml.
"""

import os
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from unittest.mock import patch

# Add the parent directory to the path to be able to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from drumgizmo_kits_generator.xml_generator import (
    create_drumkit_xml,
    create_instrument_xml,
    create_midimap_xml,
)


class TestXmlGenerator(unittest.TestCase):
    """Tests for the XML generator module."""

    def setUp(self):
        """Initialize before each test by creating test directories and metadata."""
        # Create a temporary directory for tests
        self.temp_dir = tempfile.mkdtemp()

        # Create test metadata
        self.metadata = {
            "name": "Test Kit",
            "version": "1.0",
            "description": "Test description",
            "notes": "Test notes",
            "author": "Test Author",
            "license": "Test License",
            "website": "http://example.com",
            "samplerate": "44100",
            "logo": "test_logo.png",
        }

        # Create test instruments
        self.instruments = ["Kick", "Snare", "Hi-Hat"]

    def tearDown(self):
        """Cleanup after each test by removing temporary files and directories."""
        # Remove temporary files and directories
        for root, dirs, files in os.walk(self.temp_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(self.temp_dir)

    def test_create_drumkit_xml(self):
        """Test creating the drumkit XML file with proper structure and metadata."""
        # Call the function to test
        create_drumkit_xml(self.instruments, self.temp_dir, self.metadata)

        # Verify that the file has been created
        xml_file = os.path.join(self.temp_dir, "drumkit.xml")
        self.assertTrue(os.path.exists(xml_file), "drumkit.xml file should be created")
        self.assertGreater(os.path.getsize(xml_file), 0, "drumkit.xml file should not be empty")

        # Parse the XML file and verify its content
        tree = ET.parse(xml_file)
        root = tree.getroot()

        # Verify the root element
        self.assertEqual(root.tag, "drumkit", "Root element should be 'drumkit'")
        self.assertEqual(root.attrib["name"], "Test Kit", "Kit name attribute should match")
        self.assertEqual(root.attrib["version"], "1.0", "Version attribute should match")
        self.assertEqual(root.attrib["samplerate"], "44100", "Samplerate attribute should match")

        # Verify the metadata
        metadata = root.find("metadata")
        self.assertIsNotNone(metadata, "Metadata element should exist")
        self.assertEqual(metadata.find("title").text, "Test Kit", "Title should match kit name")
        self.assertEqual(
            metadata.find("description").text, "Test description", "Description should match"
        )
        self.assertEqual(metadata.find("notes").text, "Test notes", "Notes should match")
        self.assertEqual(metadata.find("author").text, "Test Author", "Author should match")
        self.assertEqual(metadata.find("license").text, "Test License", "License should match")
        self.assertEqual(
            metadata.find("website").text, "http://example.com", "Website should match"
        )
        self.assertIsNotNone(metadata.find("logo"), "Logo element should exist")

        # Verify the created element exists
        self.assertIsNotNone(metadata.find("created"), "Created element should exist")

        # Verify the channels element exists
        channels = root.find("channels")
        self.assertIsNotNone(channels, "Channels element should exist")

        # Verify channel elements exist
        channel_elements = channels.findall("channel")
        self.assertGreater(len(channel_elements), 0, "At least one channel should be defined")

        # Verify the instruments element exists
        instruments_elem = root.find("instruments")
        self.assertIsNotNone(instruments_elem, "Instruments element should exist")

        # Verify the instrument elements under instruments
        instrument_elements = instruments_elem.findall("instrument")
        self.assertEqual(
            len(instrument_elements),
            len(self.instruments),
            f"Should have {len(self.instruments)} instrument elements",
        )

        for i, instrument in enumerate(instrument_elements):
            self.assertEqual(
                instrument.attrib["name"], self.instruments[i], f"Instrument {i} name should match"
            )
            self.assertEqual(
                instrument.attrib["file"],
                f"{self.instruments[i]}/{self.instruments[i]}.xml",
                f"Instrument {i} file path should match",
            )

    def _verify_samples(self, samples):
        # Verify each sample
        for i, sample in enumerate(samples, 1):
            # Verify the sample attributes
            self.assertIn("name", sample.attrib, f"Sample {i} should have a name attribute")
            self.assertIn("power", sample.attrib, f"Sample {i} should have a power attribute")

            # Verify the power value
            power_value = float(sample.attrib["power"])
            self.assertGreaterEqual(power_value, 0.0, f"Power for sample {i} should be >= 0")
            self.assertLessEqual(power_value, 1.0, f"Power for sample {i} should be <= 1")

            # Verify the audiofile elements
            audiofiles = sample.findall("audiofile")
            self.assertGreater(len(audiofiles), 0, f"Sample {i} should have audiofile elements")

            # Verify that the power value decreases as sample number increases
            if i > 1:
                prev_power = float(samples[i - 2].attrib["power"])
                self.assertLess(
                    power_value,
                    prev_power,
                    f"Power for sample {i} should be less than for sample {i-1}",
                )

    def test_create_instrument_xml(self):
        """Test creating an instrument XML file with proper structure and sample references."""
        # Configuration
        test_config = {"instrument_name": "Kick", "velocity_levels": 10, "extension": ".wav"}

        # Create directory structure
        instrument_dir = os.path.join(self.temp_dir, test_config["instrument_name"])
        samples_dir = os.path.join(instrument_dir, "samples")
        os.makedirs(samples_dir, exist_ok=True)

        # Create sample files
        for i in range(1, test_config["velocity_levels"] + 1):
            sample_file = os.path.join(
                samples_dir, f"{i}-{test_config['instrument_name']}{test_config['extension']}"
            )
            with open(sample_file, "w", encoding="utf-8") as f:
                f.write(f"Test sample {i}")

        # Call the function to test
        create_instrument_xml(
            test_config["instrument_name"], self.temp_dir, test_config["extension"]
        )

        # Verify file creation
        xml_file = os.path.join(instrument_dir, f"{test_config['instrument_name']}.xml")
        self.assertTrue(
            os.path.exists(xml_file), f"{test_config['instrument_name']}.xml file should be created"
        )
        self.assertGreater(
            os.path.getsize(xml_file),
            0,
            f"{test_config['instrument_name']}.xml file should not be empty",
        )

        # Parse and verify XML content
        tree = ET.parse(xml_file)
        root = tree.getroot()

        # Verify root element
        self.assertEqual(root.tag, "instrument", "Root element should be 'instrument'")
        self.assertEqual(
            root.attrib["name"],
            test_config["instrument_name"],
            "Instrument name attribute should match",
        )

        # Verify samples element exists
        samples_elem = root.find("samples")
        self.assertIsNotNone(samples_elem, "Should have a samples element")

        # Verify samples
        samples = samples_elem.findall("sample")
        self.assertEqual(
            len(samples),
            test_config["velocity_levels"],
            "Should have one sample per velocity level",
        )

        # Verify each sample
        self._verify_samples(samples)

    def test_create_instrument_xml_custom_velocity_levels(self):
        """Test creating an instrument XML file with custom velocity levels."""
        # Configuration
        test_config = {"instrument_name": "Snare", "velocity_levels": 5, "extension": ".wav"}

        # Create directory structure
        instrument_dir = os.path.join(self.temp_dir, test_config["instrument_name"])
        samples_dir = os.path.join(instrument_dir, "samples")
        os.makedirs(samples_dir, exist_ok=True)

        # Create sample files
        for i in range(1, test_config["velocity_levels"] + 1):
            sample_file = os.path.join(
                samples_dir, f"{i}-{test_config['instrument_name']}{test_config['extension']}"
            )
            with open(sample_file, "w", encoding="utf-8") as f:
                f.write(f"Test sample {i}")

        # Call the function to test
        create_instrument_xml(
            test_config["instrument_name"],
            self.temp_dir,
            test_config["extension"],
            test_config["velocity_levels"],
        )

        # Verify file creation
        xml_file = os.path.join(instrument_dir, f"{test_config['instrument_name']}.xml")
        self.assertTrue(
            os.path.exists(xml_file), f"{test_config['instrument_name']}.xml file should be created"
        )

        # Parse and verify XML content
        tree = ET.parse(xml_file)
        root = tree.getroot()

        # Verify samples element exists
        samples_elem = root.find("samples")
        self.assertIsNotNone(samples_elem, "Should have a samples element")

        # Verify samples
        samples = samples_elem.findall("sample")
        self.assertEqual(
            len(samples), test_config["velocity_levels"], "Should have the custom number of samples"
        )

        # Verify the power distribution
        powers = [float(sample.attrib["power"]) for sample in samples]

        # First sample should have power 1.0
        self.assertAlmostEqual(powers[0], 1.0, places=5, msg="First sample should have power 1.0")

        # Last sample should have power close to 1/velocity_levels
        self.assertAlmostEqual(
            powers[-1],
            1.0 - (test_config["velocity_levels"] - 1) / test_config["velocity_levels"],
            places=5,
            msg=f"Last sample should have power {1.0 - (test_config['velocity_levels'] - 1) / test_config['velocity_levels']}",
        )

    def test_create_midimap_xml(self):
        """Test creating the MIDI map XML file with proper note mappings."""
        # Call the function to test
        create_midimap_xml(self.instruments, self.temp_dir)

        # Verify that the file has been created
        xml_file = os.path.join(self.temp_dir, "midimap.xml")
        self.assertTrue(os.path.exists(xml_file), "midimap.xml file should be created")
        self.assertGreater(os.path.getsize(xml_file), 0, "midimap.xml file should not be empty")

        # Parse the XML file and verify its content
        tree = ET.parse(xml_file)
        root = tree.getroot()

        # Verify the root element
        self.assertEqual(root.tag, "midimap", "Root element should be 'midimap'")

        # Verify the instruments
        maps = root.findall("map")
        self.assertEqual(
            len(maps), len(self.instruments), f"Should have {len(self.instruments)} map elements"
        )

        # Sort instruments alphabetically to match the function's behavior
        sorted_instruments = sorted(self.instruments, key=lambda x: x.lower())

        # Verify the map entries
        for i, map_entry in enumerate(maps):
            self.assertEqual(
                map_entry.attrib["instr"],
                sorted_instruments[i],
                f"Instrument name for map {i} should match",
            )
            self.assertEqual(
                map_entry.attrib["velmin"], "0", f"Velocity min for map {i} should be 0"
            )
            self.assertEqual(
                map_entry.attrib["velmax"], "127", f"Velocity max for map {i} should be 127"
            )

        # Test with a large number of instruments to verify MIDI note assignment
        many_instruments = [f"Instrument{i}" for i in range(20)]
        create_midimap_xml(many_instruments, self.temp_dir)

        # Parse the new XML file
        tree = ET.parse(xml_file)
        root = tree.getroot()
        maps = root.findall("map")

        # Verify all instruments have unique MIDI notes
        midi_notes = set()
        for map_entry in maps:
            note = map_entry.attrib["note"]
            self.assertNotIn(note, midi_notes, f"MIDI note {note} should be unique")
            midi_notes.add(note)

    def test_create_midimap_xml_with_custom_midi_params(self):
        """Test creating the MIDI map XML file with custom MIDI parameters."""
        # Test with custom MIDI parameters
        midi_note_min = 40
        midi_note_max = 80
        midi_note_median = 60

        # Create a list of 7 instruments to test odd number distribution
        instruments = ["Kick", "Snare", "Hi-Hat", "Tom1", "Tom2", "Crash", "Ride"]

        # Call the function to test
        create_midimap_xml(
            instruments,
            self.temp_dir,
            midi_note_min=midi_note_min,
            midi_note_max=midi_note_max,
            midi_note_median=midi_note_median,
        )

        # Verify that the file has been created
        xml_file = os.path.join(self.temp_dir, "midimap.xml")
        self.assertTrue(os.path.exists(xml_file), "midimap.xml file should be created")

        # Parse the XML file and verify its content
        tree = ET.parse(xml_file)
        root = tree.getroot()
        maps = root.findall("map")

        # Sort instruments alphabetically to match the function's behavior
        sorted_instruments = sorted(instruments, key=lambda x: x.lower())

        # Verify the number of map elements
        self.assertEqual(
            len(maps),
            len(sorted_instruments),
            f"Should have {len(sorted_instruments)} map elements",
        )

        # Verify that all notes are within the allowed range
        for map_entry in maps:
            note = int(map_entry.attrib["note"])
            self.assertGreaterEqual(
                note, midi_note_min, f"MIDI note {note} should be >= {midi_note_min}"
            )
            self.assertLessEqual(
                note, midi_note_max, f"MIDI note {note} should be <= {midi_note_max}"
            )

        # For odd number of instruments, the middle instrument should be at or near the median
        # Get the notes in the order they appear in the XML
        notes = [int(map_entry.attrib["note"]) for map_entry in maps]

        # Verify distribution around median
        # For 7 instruments, we expect notes to be distributed like: median-3, median-2, median-1, median, median+1, median+2, median+3
        # But since we sort alphabetically, the actual distribution depends on the sorting
        self.assertEqual(len(notes), 7, "Should have 7 notes")

        # Verify that the range of notes matches the number of instruments
        self.assertEqual(
            max(notes) - min(notes) + 1,
            len(instruments),
            "Range of notes should match number of instruments",
        )

        # Test with a range that's too small for the number of instruments
        midi_note_min = 60
        midi_note_max = 65  # Only 6 notes available (60-65)

        # Call the function with 7 instruments but only 6 available notes
        create_midimap_xml(
            instruments,
            self.temp_dir,
            midi_note_min=midi_note_min,
            midi_note_max=midi_note_max,
            midi_note_median=62,
        )

        # Parse the XML file again
        tree = ET.parse(xml_file)
        root = tree.getroot()
        maps = root.findall("map")

        # Verify that we only have 6 instruments mapped (one should be skipped)
        self.assertEqual(len(maps), 6, "Should have 6 map elements when range is limited")

        # Verify that all mapped notes are within the allowed range
        for map_entry in maps:
            note = int(map_entry.attrib["note"])
            self.assertGreaterEqual(note, midi_note_min)
            self.assertLessEqual(note, midi_note_max)

    @patch("datetime.datetime")
    def test_create_drumkit_xml_with_timestamp(self, mock_datetime):
        """Test creating the drumkit XML file with a consistent timestamp."""
        # Configure the mock
        mock_now = unittest.mock.MagicMock()
        mock_now.strftime.return_value = "2023-01-01 12:00:00"
        mock_datetime.now.return_value = mock_now

        # Call the function to test
        create_drumkit_xml(self.instruments, self.temp_dir, self.metadata)

        # Verify that the file has been created
        xml_file = os.path.join(self.temp_dir, "drumkit.xml")
        self.assertTrue(os.path.exists(xml_file), "drumkit.xml file should be created")

        # Parse the XML file and verify its content
        tree = ET.parse(xml_file)
        root = tree.getroot()

        # Verify the timestamp in the metadata
        metadata = root.find("metadata")

        # Verify that the created element contains the timestamp
        created = metadata.find("created")
        self.assertIsNotNone(created, "Created element should exist")
        self.assertIn(
            "2023-01-01 12:00:00", created.text, "Created text should contain the timestamp"
        )

    def test_create_drumkit_xml_with_minimal_metadata(self):
        """Test creating the drumkit XML file with minimal metadata."""
        # Create minimal metadata
        minimal_metadata = {"name": "Minimal Kit", "version": "0.1", "samplerate": "48000"}

        # Call the function
        create_drumkit_xml(self.instruments, self.temp_dir, minimal_metadata)

        # Verify the result
        xml_file = os.path.join(self.temp_dir, "drumkit.xml")
        self.assertTrue(os.path.exists(xml_file), "drumkit.xml file should be created")

        # Parse the XML file
        tree = ET.parse(xml_file)
        root = tree.getroot()

        # Verify the root attributes
        self.assertEqual(root.attrib["name"], "Minimal Kit", "Kit name should match")
        self.assertEqual(root.attrib["version"], "0.1", "Version should match")
        self.assertEqual(root.attrib["samplerate"], "48000", "Samplerate should match")

        # Verify that metadata section still exists
        metadata = root.find("metadata")
        self.assertIsNotNone(metadata, "Metadata element should exist even with minimal data")

        # Verify that title exists
        self.assertEqual(metadata.find("title").text, "Minimal Kit", "Title should match kit name")


if __name__ == "__main__":
    unittest.main()
