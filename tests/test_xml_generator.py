#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name
# pylint: disable=too-many-locals
# pylint: disable=too-few-public-methods
# pylint: disable=unused-argument
# pylint: disable=chained-comparison
# pylint: disable=R0801 # code duplication
"""
SPDX-License-Identifier: MIT
SPDX-PackageName: DrumGizmo kits generator
SPDX-PackageHomePage: https://github.com/e-picas/drumgizmo-kits-generator
SPDX-FileCopyrightText: 2025 Pierre Cassat (Picas)

Tests for the xml_generator module of the DrumGizmo kit generator.
"""

import os
import shutil
import tempfile
import xml.etree.ElementTree as ET
from unittest import mock

import pytest

from drumgizmo_kits_generator import xml_generator


@pytest.fixture
def mock_logger():
    """Mock logger functions."""
    with mock.patch("drumgizmo_kits_generator.logger.info") as mock_info, mock.patch(
        "drumgizmo_kits_generator.logger.debug"
    ) as mock_debug, mock.patch(
        "drumgizmo_kits_generator.logger.warning"
    ) as mock_warning, mock.patch(
        "drumgizmo_kits_generator.logger.error"
    ) as mock_error, mock.patch(
        "drumgizmo_kits_generator.logger.print_action_start"
    ) as mock_print_action_start, mock.patch(
        "drumgizmo_kits_generator.logger.print_action_end"
    ) as mock_print_action_end:
        yield {
            "info": mock_info,
            "debug": mock_debug,
            "warning": mock_warning,
            "error": mock_error,
            "print_action_start": mock_print_action_start,
            "print_action_end": mock_print_action_end,
        }


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Clean up
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def basic_metadata():
    """Create basic metadata for testing."""
    return {
        "name": "Test Kit",
        "version": "1.0",
        "description": "Test description",
        "notes": "Test notes",
        "author": "Test Author",
        "license": "CC-BY-SA",
        "website": "https://example.com",
        "logo": "logo.png",
        "samplerate": "48000",
        "velocity_levels": 3,
        "midi_note_min": 0,
        "midi_note_max": 127,
        "midi_note_median": 60,
        "channels": ["Left", "Right", "Overhead"],
        "main_channels": ["Left", "Right"],
        "instruments": ["Kick", "Snare", "HiHat"],
    }


@pytest.fixture
def audio_files():
    """Create a list of audio file paths for testing."""
    return ["/path/to/Kick.wav", "/path/to/Snare.wav", "/path/to/HiHat.wav"]


class TestGenerateDrumkitXml:
    """Tests for the generate_drumkit_xml function."""

    def test_generate_drumkit_xml_basic(self, temp_dir, basic_metadata, mock_logger):
        """Test generate_drumkit_xml with basic metadata."""
        # Call the function
        xml_generator.generate_drumkit_xml(temp_dir, basic_metadata)

        # Check that the file was created
        xml_path = os.path.join(temp_dir, "drumkit.xml")
        assert os.path.exists(xml_path)

        # Parse the XML and check its structure
        tree = ET.parse(xml_path)
        root = tree.getroot()

        # Check root attributes
        assert root.tag == "drumkit"
        assert root.get("version") == "1.0"
        assert root.get("name") == basic_metadata["name"]
        assert root.get("samplerate") == basic_metadata["samplerate"]

        # Check metadata section
        metadata_elem = root.find("metadata")
        assert metadata_elem is not None
        assert metadata_elem.find("title").text == basic_metadata["name"]
        assert metadata_elem.find("version").text == basic_metadata["version"]
        assert metadata_elem.find("description").text == basic_metadata["description"]
        assert metadata_elem.find("notes").text == basic_metadata["notes"]
        assert metadata_elem.find("author").text == basic_metadata["author"]
        assert metadata_elem.find("license").text == basic_metadata["license"]
        assert metadata_elem.find("website").text == basic_metadata["website"]
        assert metadata_elem.find("logo").get("src") == basic_metadata["logo"]
        assert metadata_elem.find("created") is not None  # Just check it exists

        # Check channels section
        channels_elem = root.find("channels")
        assert channels_elem is not None
        channel_elems = channels_elem.findall("channel")
        assert len(channel_elems) == len(basic_metadata["channels"])
        channel_names = [channel.get("name") for channel in channel_elems]
        assert set(channel_names) == set(basic_metadata["channels"])

        # Check instruments section
        instruments_elem = root.find("instruments")
        assert instruments_elem is not None
        instrument_elems = instruments_elem.findall("instrument")
        assert len(instrument_elems) == len(basic_metadata["instruments"])

        # Check each instrument
        for instrument_elem in instrument_elems:
            instrument_name = instrument_elem.get("name")
            assert instrument_name in basic_metadata["instruments"]
            assert instrument_elem.get("file") == f"{instrument_name}/{instrument_name}.xml"

            # Check channel mappings
            channelmap_elems = instrument_elem.findall("channelmap")
            assert len(channelmap_elems) == len(basic_metadata["channels"])

            # Check main channels
            for channelmap in channelmap_elems:
                channel = channelmap.get("in")
                assert channelmap.get("out") == channel
                if channel in basic_metadata["main_channels"]:
                    assert channelmap.get("main") == "true"
                else:
                    assert channelmap.get("main") is None

        # Check logger calls
        assert mock_logger["debug"].call_count >= 1

    def test_generate_drumkit_xml_minimal(self, temp_dir, mock_logger):
        """Test generate_drumkit_xml with minimal metadata."""
        # Create minimal metadata
        minimal_metadata = {
            "name": "Minimal Kit",
            "samplerate": "44100",
            "channels": ["Mono"],
            "main_channels": ["Mono"],
            "instruments": ["Drum"],
        }

        # Call the function
        xml_generator.generate_drumkit_xml(temp_dir, minimal_metadata)

        # Check that the file was created
        xml_path = os.path.join(temp_dir, "drumkit.xml")
        assert os.path.exists(xml_path)

        # Parse the XML and check its structure
        tree = ET.parse(xml_path)
        root = tree.getroot()

        # Check root attributes
        assert root.tag == "drumkit"
        assert root.get("name") == minimal_metadata["name"]
        assert root.get("samplerate") == minimal_metadata["samplerate"]

        # Check metadata section
        metadata_elem = root.find("metadata")
        assert metadata_elem is not None
        assert metadata_elem.find("title").text == minimal_metadata["name"]
        assert metadata_elem.find("description") is None  # Not provided
        assert metadata_elem.find("notes") is not None  # Default notes
        assert metadata_elem.find("author") is None  # Not provided
        assert metadata_elem.find("license").text is None  # Not provided
        assert metadata_elem.find("website") is None  # Not provided
        assert metadata_elem.find("logo") is None  # Not provided

        # Check channels and instruments
        assert len(root.find("channels").findall("channel")) == 1
        assert len(root.find("instruments").findall("instrument")) == 1


class TestGenerateInstrumentXml:
    """Tests for the generate_instrument_xml function."""

    def test_generate_instrument_xml(self, temp_dir, basic_metadata, audio_files, mock_logger):
        """Test generate_instrument_xml with basic metadata."""
        instrument_name = "Snare"

        # Call the function
        xml_generator.generate_instrument_xml(
            temp_dir, instrument_name, basic_metadata, audio_files
        )

        # Check that the directories were created
        instrument_dir = os.path.join(temp_dir, instrument_name)
        assert os.path.exists(instrument_dir)

        # Check that the file was created
        xml_path = os.path.join(instrument_dir, f"{instrument_name}.xml")
        assert os.path.exists(xml_path)

        # Parse the XML and check its structure
        tree = ET.parse(xml_path)
        root = tree.getroot()

        # Check root attributes
        assert root.tag == "instrument"
        assert root.get("version") == "2.0"
        assert root.get("name") == instrument_name

        # Check samples section
        samples_elem = root.find("samples")
        assert samples_elem is not None
        sample_elems = samples_elem.findall("sample")
        assert len(sample_elems) == basic_metadata["velocity_levels"]

        # Check each sample
        for i, sample_elem in enumerate(sample_elems, 1):
            assert sample_elem.get("name") == f"{instrument_name}-{i}"

            # Check power attribute
            power = float(sample_elem.get("power"))
            if i == 1:
                assert power == 1.0
            else:
                # Power should decrease with velocity level
                assert power < 1.0

            # Check audiofile elements
            audiofile_elems = sample_elem.findall("audiofile")
            assert len(audiofile_elems) == len(basic_metadata["channels"])

            # Check alternating filechannel values
            for j, audiofile in enumerate(audiofile_elems):
                assert audiofile.get("channel") in basic_metadata["channels"]
                assert audiofile.get("file").startswith(f"samples/{i}-{instrument_name}")

                # Check filechannel alternates between 1 and 2
                expected_filechannel = "1" if j % 2 == 0 else "2"
                assert audiofile.get("filechannel") == expected_filechannel

        # Check logger calls
        assert mock_logger["debug"].call_count >= 1

    @mock.patch("os.path.splitext")
    def test_generate_instrument_xml_with_extension(
        self, mock_splitext, temp_dir, basic_metadata, audio_files, mock_logger
    ):
        """Test generate_instrument_xml preserves file extension."""
        instrument_name = "Snare"

        # Mock os.path.splitext to return a specific extension
        mock_splitext.return_value = ("filename", ".flac")

        # Call the function
        xml_generator.generate_instrument_xml(
            temp_dir, instrument_name, basic_metadata, audio_files
        )

        # Check that the file was created
        xml_path = os.path.join(temp_dir, instrument_name, f"{instrument_name}.xml")
        assert os.path.exists(xml_path)

        # Parse the XML and check file extensions
        tree = ET.parse(xml_path)
        root = tree.getroot()

        # Check that file references use the correct extension
        for sample in root.find("samples").findall("sample"):
            for audiofile in sample.findall("audiofile"):
                assert audiofile.get("file").endswith(".flac")


class TestGenerateMidimapXml:
    """Tests for the generate_midimap_xml function."""

    def test_generate_midimap_xml(self, temp_dir, basic_metadata, mock_logger):
        """Test generate_midimap_xml with basic metadata."""
        # Call the function
        xml_generator.generate_midimap_xml(temp_dir, basic_metadata)

        # Check that the file was created
        xml_path = os.path.join(temp_dir, "midimap.xml")
        assert os.path.exists(xml_path)

        # Parse the XML and check its structure
        tree = ET.parse(xml_path)
        root = tree.getroot()

        # Check root tag
        assert root.tag == "midimap"

        # Check map elements
        map_elems = root.findall("map")
        assert len(map_elems) == len(basic_metadata["instruments"])

        # Check that notes are distributed around the median
        midi_note_median = basic_metadata["midi_note_median"]
        notes = [int(map_elem.get("note")) for map_elem in map_elems]

        # Check that at least one note is at or near the median
        assert any(note >= midi_note_median - 1 and note <= midi_note_median + 1 for note in notes)

        # Check that all notes are within range
        assert all(note >= basic_metadata["midi_note_min"] for note in notes)
        assert all(note <= basic_metadata["midi_note_max"] for note in notes)

        # Check instrument references
        instruments = [map_elem.get("instr") for map_elem in map_elems]
        assert set(instruments) == set(basic_metadata["instruments"])

        # Check velocity range
        for map_elem in map_elems:
            assert map_elem.get("velmin") == "0"
            assert map_elem.get("velmax") == "127"

        # Check logger calls
        assert mock_logger["debug"].call_count >= 1

    def test_generate_midimap_xml_no_instruments(self, temp_dir, mock_logger):
        """Test generate_midimap_xml with no instruments."""
        # Create metadata without instruments
        metadata = {
            "name": "Empty Kit",
            "samplerate": "44100",
            "channels": ["Mono"],
            "main_channels": ["Mono"],
            "midi_note_min": 0,
            "midi_note_max": 127,
            "midi_note_median": 60,
            "instruments": [],  # Empty list
        }

        # Call the function
        xml_generator.generate_midimap_xml(temp_dir, metadata)

        # Check that the file was not created (function should return early)
        xml_path = os.path.join(temp_dir, "midimap.xml")
        assert not os.path.exists(xml_path)

        # Check warning log
        assert mock_logger["warning"].call_count >= 1
        assert "No instruments found" in str(mock_logger["warning"].call_args[0][0])

    def test_generate_midimap_xml_many_instruments(self, temp_dir, mock_logger):
        """Test generate_midimap_xml with many instruments."""
        # Create metadata with many instruments
        instruments = [f"Instrument{i}" for i in range(20)]
        metadata = {
            "name": "Many Instruments Kit",
            "samplerate": "44100",
            "channels": ["Mono"],
            "main_channels": ["Mono"],
            "midi_note_min": 0,
            "midi_note_max": 127,
            "midi_note_median": 60,
            "instruments": instruments,
        }

        # Call the function
        xml_generator.generate_midimap_xml(temp_dir, metadata)

        # Check that the file was created
        xml_path = os.path.join(temp_dir, "midimap.xml")
        assert os.path.exists(xml_path)

        # Parse the XML and check its structure
        tree = ET.parse(xml_path)
        root = tree.getroot()

        # Check that all instruments are mapped
        map_elems = root.findall("map")
        assert len(map_elems) == len(instruments)

        # Check that notes are properly distributed
        notes = [int(map_elem.get("note")) for map_elem in map_elems]

        # Check that notes are within range
        assert all(note >= metadata["midi_note_min"] for note in notes)
        assert all(note <= metadata["midi_note_max"] for note in notes)
