#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for the XML generator module of the DrumGizmo kit generator.

These tests verify the functionality of XML generation for DrumGizmo kits,
including the creation of drumkit.xml, instrument XML files, and midimap.xml.
"""

import os
import sys
import unittest
import tempfile
import xml.etree.ElementTree as ET
from unittest.mock import patch

# Add the parent directory to the path to be able to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the module to test
# pylint: disable-next=wrong-import-position
from xml_generator import (
    create_drumkit_xml,
    create_xml_file,
    create_midimap_xml
)


class TestXmlGenerator(unittest.TestCase):
    """Tests for the XML generator module."""

    def setUp(self):
        """Initialize before each test by creating test directories and metadata."""
        # Create a temporary directory for tests
        self.temp_dir = tempfile.mkdtemp()

        # Create test metadata
        self.metadata = {
            'name': 'Test Kit',
            'version': '1.0',
            'description': 'Test description',
            'notes': 'Test notes',
            'author': 'Test Author',
            'license': 'Test License',
            'website': 'http://example.com',
            'samplerate': '44100',
            'logo': 'test_logo.png'
        }

        # Create test instruments
        self.instruments = ['Kick', 'Snare', 'Hi-Hat']

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
        xml_file = os.path.join(self.temp_dir, 'drumkit.xml')
        self.assertTrue(os.path.exists(xml_file), "drumkit.xml file should be created")
        self.assertGreater(os.path.getsize(xml_file), 0, "drumkit.xml file should not be empty")

        # Parse the XML file and verify its content
        tree = ET.parse(xml_file)
        root = tree.getroot()

        # Verify the root element
        self.assertEqual(root.tag, 'drumkit', "Root element should be 'drumkit'")
        self.assertEqual(root.attrib['name'], 'Test Kit', "Kit name attribute should match")
        self.assertEqual(root.attrib['version'], '1.0', "Version attribute should match")
        self.assertEqual(root.attrib['samplerate'], '44100', "Samplerate attribute should match")

        # Verify the metadata
        metadata = root.find('metadata')
        self.assertIsNotNone(metadata, "Metadata element should exist")
        self.assertEqual(metadata.find('title').text, 'Test Kit', "Title should match kit name")
        self.assertEqual(metadata.find('description').text, 'Test description', "Description should match")
        self.assertEqual(metadata.find('notes').text, 'Test notes', "Notes should match")
        self.assertEqual(metadata.find('author').text, 'Test Author', "Author should match")
        self.assertEqual(metadata.find('license').text, 'Test License', "License should match")
        self.assertEqual(metadata.find('website').text, 'http://example.com', "Website should match")
        self.assertIsNotNone(metadata.find('logo'), "Logo element should exist")
        
        # Verify the created element exists
        self.assertIsNotNone(metadata.find('created'), "Created element should exist")

        # Verify the channels element exists
        channels = root.find('channels')
        self.assertIsNotNone(channels, "Channels element should exist")
        
        # Verify channel elements exist
        channel_elements = channels.findall('channel')
        self.assertGreater(len(channel_elements), 0, "At least one channel should be defined")
        
        # Verify the instruments element exists
        instruments_elem = root.find('instruments')
        self.assertIsNotNone(instruments_elem, "Instruments element should exist")
        
        # Verify the instrument elements under instruments
        instrument_elements = instruments_elem.findall('instrument')
        self.assertEqual(len(instrument_elements), len(self.instruments), 
                        f"Should have {len(self.instruments)} instrument elements")
        
        for i, instrument in enumerate(instrument_elements):
            self.assertEqual(instrument.attrib['name'], self.instruments[i], 
                            f"Instrument {i} name should match")
            self.assertEqual(instrument.attrib['file'], 
                            f"{self.instruments[i]}/{self.instruments[i]}.xml", 
                            f"Instrument {i} file path should match")

    def test_create_xml_file(self):
        """Test creating an instrument XML file with proper structure and sample references."""
        # Create a directory for the instrument
        instrument_name = 'Kick'
        instrument_dir = os.path.join(self.temp_dir, instrument_name)
        os.makedirs(instrument_dir, exist_ok=True)

        # Create a samples directory
        samples_dir = os.path.join(instrument_dir, 'samples')
        os.makedirs(samples_dir, exist_ok=True)

        # Create sample files
        for i in range(1, 11):
            sample_file = os.path.join(samples_dir, f"{i}-{instrument_name}.wav")
            with open(sample_file, 'w', encoding='utf-8') as f:
                f.write('Sample content')

        # Call the function to test
        create_xml_file(instrument_name, self.temp_dir, ".wav")

        # Verify that the file has been created
        xml_file = os.path.join(instrument_dir, f"{instrument_name}.xml")
        self.assertTrue(os.path.exists(xml_file), "Instrument XML file should be created")
        self.assertGreater(os.path.getsize(xml_file), 0, "Instrument XML file should not be empty")

        # Parse the XML file and verify its content
        tree = ET.parse(xml_file)
        root = tree.getroot()

        # Verify the root element
        self.assertEqual(root.tag, 'instrument', "Root element should be 'instrument'")
        self.assertEqual(root.attrib['name'], instrument_name, "Instrument name attribute should match")
        self.assertEqual(root.attrib['version'], '2.0', "Version should be 2.0 for instrument files")

        # Verify the samples
        samples_element = root.find('samples')
        self.assertIsNotNone(samples_element, "Samples element should exist")
        
        samples = samples_element.findall('sample')
        self.assertEqual(len(samples), 10, "Should have 10 sample elements")
        
        for i, sample in enumerate(samples, 1):
            self.assertEqual(sample.attrib['name'], f"{instrument_name}-{i}", f"Sample {i} name should match")
            
            # Verify audiofile elements exist
            audiofiles = sample.findall('audiofile')
            self.assertGreater(len(audiofiles), 0, f"Sample {i} should have audiofile elements")
            
            # Verify that the power value decreases as sample number increases
            power_value = float(sample.attrib['power'])
            if i > 1:
                prev_power = float(samples[i-2].attrib['power'])
                self.assertLess(power_value, prev_power, 
                               f"Power for sample {i} should be less than for sample {i-1}")

    def test_create_midimap_xml(self):
        """Test creating the MIDI map XML file with proper note mappings."""
        # Call the function to test
        create_midimap_xml(self.instruments, self.temp_dir)

        # Verify that the file has been created
        xml_file = os.path.join(self.temp_dir, 'midimap.xml')
        self.assertTrue(os.path.exists(xml_file), "midimap.xml file should be created")
        self.assertGreater(os.path.getsize(xml_file), 0, "midimap.xml file should not be empty")

        # Parse the XML file and verify its content
        tree = ET.parse(xml_file)
        root = tree.getroot()

        # Verify the root element
        self.assertEqual(root.tag, 'midimap', "Root element should be 'midimap'")

        # Verify the instruments
        maps = root.findall('map')
        self.assertEqual(len(maps), len(self.instruments), 
                        f"Should have {len(self.instruments)} map elements")

        # Sort instruments alphabetically to match the function's behavior
        sorted_instruments = sorted(self.instruments, key=lambda x: x.lower())

        # Verify the map entries
        for i, map_entry in enumerate(maps):
            self.assertEqual(map_entry.attrib['instr'], sorted_instruments[i], 
                            f"Instrument name for map {i} should match")
            self.assertEqual(map_entry.attrib['velmin'], '0', 
                            f"Velocity min for map {i} should be 0")
            self.assertEqual(map_entry.attrib['velmax'], '127', 
                            f"Velocity max for map {i} should be 127")
        
        # Test with a large number of instruments to verify MIDI note assignment
        many_instruments = [f"Instrument{i}" for i in range(20)]
        create_midimap_xml(many_instruments, self.temp_dir)
        
        # Parse the new XML file
        tree = ET.parse(xml_file)
        root = tree.getroot()
        maps = root.findall('map')
        
        # Verify all instruments have unique MIDI notes
        midi_notes = set()
        for map_entry in maps:
            note = map_entry.attrib['note']
            self.assertNotIn(note, midi_notes, f"MIDI note {note} should be unique")
            midi_notes.add(note)

    @patch('datetime.datetime')
    def test_create_drumkit_xml_with_timestamp(self, mock_datetime):
        """Test creating the drumkit XML file with a consistent timestamp."""
        # Configure the mock
        mock_now = unittest.mock.MagicMock()
        mock_now.strftime.return_value = '2023-01-01 12:00:00'
        mock_datetime.now.return_value = mock_now

        # Call the function to test
        create_drumkit_xml(self.instruments, self.temp_dir, self.metadata)

        # Verify that the file has been created
        xml_file = os.path.join(self.temp_dir, 'drumkit.xml')
        self.assertTrue(os.path.exists(xml_file), "drumkit.xml file should be created")

        # Parse the XML file and verify its content
        tree = ET.parse(xml_file)
        root = tree.getroot()

        # Verify the timestamp in the metadata
        metadata = root.find('metadata')
        
        # Verify that the created element contains the timestamp
        created = metadata.find('created')
        self.assertIsNotNone(created, "Created element should exist")
        self.assertIn('2023-01-01 12:00:00', created.text, 
                     "Created text should contain the timestamp")
        
    def test_create_drumkit_xml_with_minimal_metadata(self):
        """Test creating the drumkit XML file with minimal metadata."""
        # Create minimal metadata
        minimal_metadata = {
            'name': 'Minimal Kit',
            'version': '0.1',
            'samplerate': '48000'
        }
        
        # Call the function
        create_drumkit_xml(self.instruments, self.temp_dir, minimal_metadata)
        
        # Verify the result
        xml_file = os.path.join(self.temp_dir, 'drumkit.xml')
        self.assertTrue(os.path.exists(xml_file), "drumkit.xml file should be created")
        
        # Parse the XML file
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        # Verify the root attributes
        self.assertEqual(root.attrib['name'], 'Minimal Kit', "Kit name should match")
        self.assertEqual(root.attrib['version'], '0.1', "Version should match")
        self.assertEqual(root.attrib['samplerate'], '48000', "Samplerate should match")
        
        # Verify that metadata section still exists
        metadata = root.find('metadata')
        self.assertIsNotNone(metadata, "Metadata element should exist even with minimal data")
        
        # Verify that title exists
        self.assertEqual(metadata.find('title').text, 'Minimal Kit', "Title should match kit name")


if __name__ == '__main__':
    unittest.main()
