#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-locals
# pylint: disable=broad-exception-caught
# pylint: disable=redundant-unittest-assert
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
# pylint: disable=unused-variable
# pylint: disable=unspecified-encoding
# pylint: disable=consider-using-with
# pylint: disable=import-outside-toplevel,wrong-import-position
"""
Additional tests for the xml_generator module to improve test coverage.
"""

import os
import sys
import xml.etree.ElementTree as ET
from unittest.mock import mock_open, patch

# Add the parent directory to the path to be able to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from drumgizmo_kits_generator.xml_generator import (
    calculate_midi_start_note,
    create_drumkit_xml,
    create_instrument_xml,
    create_midimap_xml,
    get_channels_from_metadata,
    write_pretty_xml,
)
from tests.test_base import BaseTestCase


class TestXmlGeneratorAdditional(BaseTestCase):
    """Additional tests for the xml_generator module to improve test coverage."""

    def test_write_pretty_xml_permission_error(self):
        """Test write_pretty_xml with a permission error."""
        # Create a simple XML tree
        root = ET.Element("root")
        ET.SubElement(root, "child")
        tree = ET.ElementTree(root)

        # Create a path to a file in a non-existent directory to trigger a permission error
        xml_file = os.path.join("/nonexistent", "test.xml")

        # Call write_pretty_xml
        with patch("builtins.open", mock_open()) as mock_file:
            mock_file.side_effect = PermissionError("Permission denied")
            result = write_pretty_xml(tree, xml_file)

            # Check that the result is False
            self.assertFalse(result, "Should return False when a PermissionError occurs")

            # Check that the output contains the expected error message
            output = self.mock_stderr.getvalue()
            self.assertIn("Permission denied", output)

    def test_write_pretty_xml_os_error(self):
        """Test write_pretty_xml with an OS error."""
        # Create a simple XML tree
        root = ET.Element("root")
        ET.SubElement(root, "child")
        tree = ET.ElementTree(root)

        # Create a path to a file
        xml_file = os.path.join(self.temp_dir, "test.xml")

        # Call write_pretty_xml
        with patch("builtins.open", mock_open()) as mock_file:
            mock_file.side_effect = OSError("File system error")
            result = write_pretty_xml(tree, xml_file)

            # Check that the result is False
            self.assertFalse(result, "Should return False when an OSError occurs")

            # Check that the output contains the expected error message
            output = self.mock_stderr.getvalue()
            self.assertIn("File system error", output)

    def test_create_instrument_xml_exception(self):
        """Test create_instrument_xml with an exception."""
        # Set up test parameters
        instrument = "snare"
        kit_dir = self.temp_dir
        extension = ".wav"
        velocity_levels = 3
        metadata = {"channels": "L,R"}

        # Create the instrument directory
        instrument_dir = os.path.join(kit_dir, instrument)
        os.makedirs(instrument_dir, exist_ok=True)

        # Mock ET.Element to raise an exception
        with patch("xml.etree.ElementTree.Element") as mock_element:
            mock_element.side_effect = ValueError("Invalid element")

            # Call create_instrument_xml
            result = create_instrument_xml(
                instrument, kit_dir, extension, velocity_levels, metadata
            )

            # Check that the result is None
            self.assertIsNone(result, "Should return None when an exception occurs")

            # Check that the output contains the expected error message
            output = self.mock_stderr.getvalue()
            self.assertIn("Error creating instrument XML file", output)
            self.assertIn("ValueError", output)

    def test_create_drumkit_xml_exception(self):
        """Test create_drumkit_xml with an exception."""
        # Set up test parameters
        instruments = ["kick", "snare", "hihat"]
        kit_dir = self.temp_dir
        metadata = {
            "name": "Test Kit",
            "version": "1.0",
            "samplerate": "44100",
            "description": "Test description",
            "author": "Test Author",
            "license": "CC0",
        }

        # Mock ET.Element to raise an exception
        with patch("xml.etree.ElementTree.Element") as mock_element:
            mock_element.side_effect = ValueError("Invalid element")

            # Call create_drumkit_xml
            result = create_drumkit_xml(instruments, kit_dir, metadata)

            # Check that the result is None
            self.assertIsNone(result, "Should return None when an exception occurs")

            # Check that the output contains the expected error message
            output = self.mock_stderr.getvalue()
            self.assertIn("Error creating drumkit XML file", output)
            self.assertIn("ValueError", output)

    def test_create_midimap_xml_exception(self):
        """Test create_midimap_xml with an exception."""
        # Set up test parameters
        instruments = ["kick", "snare", "hihat"]
        kit_dir = self.temp_dir
        midi_note_min = 35
        midi_note_max = 81
        midi_note_median = 60

        # Mock ET.Element to raise an exception
        with patch("xml.etree.ElementTree.Element") as mock_element:
            mock_element.side_effect = ValueError("Invalid element")

            # Call create_midimap_xml
            result = create_midimap_xml(
                instruments, kit_dir, midi_note_min, midi_note_max, midi_note_median
            )

            # Check that the result is None
            self.assertIsNone(result, "Should return None when an exception occurs")

            # Check that the output contains the expected error message
            output = self.mock_stderr.getvalue()
            self.assertIn("Error creating midimap XML file", output)
            self.assertIn("ValueError", output)

    def test_create_midimap_xml_with_out_of_range_notes(self):
        """Test create_midimap_xml with notes outside the allowed range."""
        # Set up test parameters
        instruments = ["kick", "snare", "hihat", "tom1", "tom2", "tom3", "crash", "ride"]
        kit_dir = self.temp_dir
        midi_note_min = 60
        midi_note_max = 62
        midi_note_median = 61

        # Call create_midimap_xml
        result = create_midimap_xml(
            instruments, kit_dir, midi_note_min, midi_note_max, midi_note_median
        )

        # Check that the result is not None
        self.assertIsNotNone(result, "Should return the path to the created XML file")

        # Check that the output contains warnings about skipped instruments
        output = self.mock_stderr.getvalue()
        self.assertIn("Warning: Skipping", output)

        # Check that the XML file exists
        self.assertTrue(os.path.exists(result), "XML file should exist")

        # Parse the XML file and check its content
        tree = ET.parse(result)
        root = tree.getroot()

        # Check that only instruments within the allowed range are included
        map_elements = root.findall("map")
        self.assertEqual(
            len(map_elements), 3, "Should only include 3 instruments within the allowed range"
        )

    def test_calculate_midi_start_note_with_constraints(self):
        """Test calculate_midi_start_note with various constraints."""
        # Test with number of instruments that fit within the range
        num_instruments = 5
        midi_note_median = 60
        midi_note_min = 35
        midi_note_max = 81

        start_note = calculate_midi_start_note(
            num_instruments, midi_note_median, midi_note_min, midi_note_max
        )

        # Check that the start note is calculated correctly
        expected_start_note = midi_note_median - num_instruments // 2
        self.assertEqual(
            start_note, expected_start_note, "Start note should be calculated correctly"
        )

        # Test with number of instruments that would go below the minimum
        num_instruments = 50
        midi_note_median = 60
        midi_note_min = 35
        midi_note_max = 81

        start_note = calculate_midi_start_note(
            num_instruments, midi_note_median, midi_note_min, midi_note_max
        )

        # Check that the start note is adjusted to the minimum
        self.assertEqual(start_note, midi_note_min, "Start note should be adjusted to the minimum")

    def test_get_channels_from_metadata(self):
        """Test get_channels_from_metadata with various inputs."""
        # Test with channels in metadata
        metadata = {"channels": ["L", "R"]}
        channels = get_channels_from_metadata(metadata)
        self.assertEqual(channels, ["L", "R"], "Should return the channels from metadata")

        # Test with no channels in metadata
        metadata = {}
        channels = get_channels_from_metadata(metadata)
        self.assertIsInstance(channels, list, "Should return a list of default channels")
        self.assertGreater(len(channels), 0, "Should return a non-empty list of default channels")


if __name__ == "__main__":
    import unittest

    unittest.main()
