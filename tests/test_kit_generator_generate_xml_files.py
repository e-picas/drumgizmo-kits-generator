#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=unspecified-encoding
"""
SPDX-License-Identifier: MIT
SPDX-PackageName: DrumGizmo kits generator
SPDX-FileCopyrightText: 2023 E-Picas <drumgizmo@e-picas.fr>
SPDX-FileType: SOURCE

Tests for the generate_xml_files function in kit_generator.py
"""

import os
import tempfile
from unittest.mock import patch

import pytest

from drumgizmo_kits_generator.exceptions import XMLGenerationError
from drumgizmo_kits_generator.kit_generator import generate_xml_files
from drumgizmo_kits_generator.state import RunData


def test_generate_xml_files_success():
    """Test that generate_xml_files successfully generates XML files."""
    with tempfile.TemporaryDirectory() as target_dir:
        # Create a RunData instance with the test directories and mock data
        config = {
            "name": "Test Kit",
            "version": "1.0",
            "description": "Test description",
            "license": "MIT",
            "author": "Test Author",
            "website": "https://example.com",
            "samplerate": "44100",
            "velocity_levels": 3,
            "midi_note_min": 35,
            "midi_note_max": 59,
            "midi_note_median": 47,
            "channels": ["Left", "Right"],
            "main_channels": ["Left", "Right"],
        }

        # Mock audio processed data
        audio_processed = {
            "kick": {
                os.path.join(target_dir, "1-kick.wav"): {"volume": 1.0},
                os.path.join(target_dir, "2-kick.wav"): {"volume": 0.8},
                os.path.join(target_dir, "3-kick.wav"): {"volume": 0.6},
            },
            "snare": {
                os.path.join(target_dir, "1-snare.wav"): {"volume": 1.0},
                os.path.join(target_dir, "2-snare.wav"): {"volume": 0.8},
                os.path.join(target_dir, "3-snare.wav"): {"volume": 0.6},
            },
        }

        run_data = RunData(
            source_dir="/tmp/source",
            target_dir=target_dir,
            config=config,
            audio_processed=audio_processed,
        )

        # Mock the XML generation functions to avoid actual file creation
        with patch(
            "drumgizmo_kits_generator.xml_generator.generate_drumkit_xml",
            return_value="drumkit.xml",
        ) as mock_drumkit_xml:
            with patch(
                "drumgizmo_kits_generator.xml_generator.generate_instrument_xml",
                return_value="instrument.xml",
            ) as mock_instrument_xml:
                with patch(
                    "drumgizmo_kits_generator.xml_generator.generate_midimap_xml",
                    return_value="midimap.xml",
                ) as mock_midimap_xml:
                    # Call the function
                    generate_xml_files(run_data)

                    # Check that the XML generation functions were called
                    assert mock_drumkit_xml.call_count > 0
                    assert mock_instrument_xml.call_count > 0
                    assert mock_midimap_xml.call_count > 0


def test_generate_xml_files_error():
    """Test that generate_xml_files raises XMLGenerationError when an error occurs."""
    with tempfile.TemporaryDirectory() as target_dir:
        # Create a RunData instance with the test directories and mock data
        config = {
            "name": "Test Kit",
            "version": "1.0",
            "description": "Test description",
            "license": "MIT",
            "author": "Test Author",
            "website": "https://example.com",
            "samplerate": "44100",
            "velocity_levels": 3,
            "midi_note_min": 35,
            "midi_note_max": 59,
            "midi_note_median": 47,
            "channels": ["Left", "Right"],
            "main_channels": ["Left", "Right"],
        }

        # Mock audio processed data
        audio_processed = {
            "kick": {
                os.path.join(target_dir, "1-kick.wav"): {"volume": 1.0},
                os.path.join(target_dir, "2-kick.wav"): {"volume": 0.8},
                os.path.join(target_dir, "3-kick.wav"): {"volume": 0.6},
            }
        }

        run_data = RunData(
            source_dir="/tmp/source",
            target_dir=target_dir,
            config=config,
            audio_processed=audio_processed,
        )

        # Mock xml_generator.generate_drumkit_xml to raise an exception
        with patch(
            "drumgizmo_kits_generator.xml_generator.generate_drumkit_xml",
            side_effect=Exception("XML generation error"),
        ):
            # Call the function and expect an XMLGenerationError
            with pytest.raises(XMLGenerationError) as excinfo:
                generate_xml_files(run_data)

            # Check that the exception has the expected message
            assert "Unexpected error during XML file generation" in str(excinfo.value)
            assert "XML generation error" in str(excinfo.value)


def test_generate_xml_files_with_midi_mapping():
    """Test that generate_xml_files correctly handles MIDI mapping."""
    with tempfile.TemporaryDirectory() as target_dir:
        # Create a RunData instance with the test directories and mock data
        config = {
            "name": "Test Kit",
            "version": "1.0",
            "description": "Test description",
            "license": "MIT",
            "author": "Test Author",
            "website": "https://example.com",
            "samplerate": "44100",
            "velocity_levels": 3,
            "midi_note_min": 35,
            "midi_note_max": 59,
            "midi_note_median": 47,
            "channels": ["Left", "Right"],
            "main_channels": ["Left", "Right"],
        }

        # Mock audio processed data
        audio_processed = {
            "kick": {
                os.path.join(target_dir, "1-kick.wav"): {"volume": 1.0},
                os.path.join(target_dir, "2-kick.wav"): {"volume": 0.8},
                os.path.join(target_dir, "3-kick.wav"): {"volume": 0.6},
            }
        }

        # Add MIDI mapping
        midi_mapping = {"kick": 36}

        run_data = RunData(
            source_dir="/tmp/source",
            target_dir=target_dir,
            config=config,
            audio_processed=audio_processed,
            midi_mapping=midi_mapping,
        )

        # Mock the XML generation functions to check their inputs
        with patch(
            "drumgizmo_kits_generator.xml_generator.generate_drumkit_xml",
            return_value="drumkit.xml",
        ) as mock_drumkit_xml:
            with patch(
                "drumgizmo_kits_generator.xml_generator.generate_instrument_xml",
                return_value="instrument.xml",
            ) as mock_instrument_xml:
                with patch(
                    "drumgizmo_kits_generator.xml_generator.generate_midimap_xml",
                    return_value="midimap.xml",
                ) as mock_midimap_xml:
                    # Call the function
                    generate_xml_files(run_data)

                    # Check that the XML generation functions were called
                    assert mock_drumkit_xml.call_count > 0
                    assert mock_instrument_xml.call_count > 0
                    assert mock_midimap_xml.call_count > 0

                    # Check that the MIDI mapping was passed correctly
                    if mock_midimap_xml.call_count > 0:
                        midimap_args = mock_midimap_xml.call_args[0]
                        assert len(midimap_args) >= 2
                        assert midimap_args[1] == midi_mapping
