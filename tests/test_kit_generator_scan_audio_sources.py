#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=unspecified-encoding
# pylint: disable=unused-argument
"""
SPDX-License-Identifier: MIT
SPDX-PackageName: DrumGizmo kits generator
SPDX-FileCopyrightText: 2023 E-Picas <drumgizmo@e-picas.fr>
SPDX-FileType: SOURCE

Tests for the scan_audio_sources function in kit_generator.py
"""

import os
import tempfile
from unittest.mock import patch

import pytest

from drumgizmo_kits_generator.kit_generator import scan_source_files
from drumgizmo_kits_generator.state import RunData


def test_scan_source_files_success():
    """Test that scan_audio_sources successfully scans audio files."""
    with tempfile.TemporaryDirectory() as source_dir:
        # Create test audio files in the source directory
        audio_files = {
            "kick.wav": "test audio content for kick",
            "snare.wav": "test audio content for snare",
            "hihat.wav": "test audio content for hihat",
        }

        for filename, content in audio_files.items():
            file_path = os.path.join(source_dir, filename)
            with open(file_path, "w") as f:
                f.write(content)

        # Create a RunData instance with the test directories
        config = {
            "extensions": ["wav"],
            "midi_note_min": 35,
            "midi_note_max": 59,
        }

        run_data = RunData(source_dir=source_dir, target_dir="/tmp/target", config=config)

        # Mock utils.get_audio_info to return mock audio info
        def mock_get_audio_info(file_path):
            return {
                "channels": 2,
                "samplerate": "48000",
                "duration": 1.0,
            }

        with patch(
            "drumgizmo_kits_generator.audio.get_audio_info", side_effect=mock_get_audio_info
        ):
            # Call the function
            scan_source_files(run_data)

            # Check that the audio sources were added to run_data
            assert run_data.audio_sources
            assert len(run_data.audio_sources) == 3

            # Check that each instrument has the expected properties
            for instrument_name in ["kick", "snare", "hihat"]:
                assert instrument_name in run_data.audio_sources
                assert "source_path" in run_data.audio_sources[instrument_name]
                assert "channels" in run_data.audio_sources[instrument_name]
                assert "samplerate" in run_data.audio_sources[instrument_name]
                assert "duration" in run_data.audio_sources[instrument_name]
                assert run_data.audio_sources[instrument_name]["channels"] == 2
                assert run_data.audio_sources[instrument_name]["samplerate"] == "48000"
                assert run_data.audio_sources[instrument_name]["duration"] == 1.0


def test_scan_source_files_no_files():
    """Test that scan_audio_sources handles the case when no audio files are found."""
    with tempfile.TemporaryDirectory() as source_dir:
        # Create a RunData instance with the test directories
        config = {
            "extensions": ["wav"],
            "midi_note_min": 35,
            "midi_note_max": 59,
        }

        run_data = RunData(source_dir=source_dir, target_dir="/tmp/target", config=config)

        # Call the function - it should not raise an exception
        scan_source_files(run_data)

        # Check that no audio sources were added
        assert run_data.audio_sources == {}


def test_scan_source_files_with_multiple_extensions():
    """Test that scan_audio_sources handles multiple file extensions."""
    with tempfile.TemporaryDirectory() as source_dir:
        # Create test audio files with different extensions
        audio_files = {
            "kick.wav": "test audio content for kick",
            "snare.flac": "test audio content for snare",
            "hihat.aiff": "test audio content for hihat",
            "tom.txt": "this is not an audio file",
        }

        for filename, content in audio_files.items():
            file_path = os.path.join(source_dir, filename)
            with open(file_path, "w") as f:
                f.write(content)

        # Create a RunData instance with the test directories
        config = {
            "extensions": ["wav", "flac", "aiff"],
            "midi_note_min": 35,
            "midi_note_max": 59,
        }

        run_data = RunData(source_dir=source_dir, target_dir="/tmp/target", config=config)

        # Mock utils.get_audio_info to return mock audio info
        def mock_get_audio_info(file_path):
            return {
                "channels": 2,
                "samplerate": "48000",
                "duration": 1.0,
            }

        with patch(
            "drumgizmo_kits_generator.audio.get_audio_info", side_effect=mock_get_audio_info
        ):
            # Call the function
            scan_source_files(run_data)

            # Check that only the audio files were added to run_data
            assert run_data.audio_sources
            assert len(run_data.audio_sources) == 3
            assert "kick" in run_data.audio_sources
            assert "snare" in run_data.audio_sources
            assert "hihat" in run_data.audio_sources
            assert "tom" not in run_data.audio_sources


def test_scan_source_files_audio_info_error():
    """Test that scan_audio_sources handles errors when getting audio info."""
    with tempfile.TemporaryDirectory() as source_dir:
        # Create a test audio file
        audio_path = os.path.join(source_dir, "kick.wav")
        with open(audio_path, "w") as f:
            f.write("test audio content")

        # Create a RunData instance with the test directories
        config = {
            "extensions": ["wav"],
            "midi_note_min": 35,
            "midi_note_max": 59,
        }

        run_data = RunData(source_dir=source_dir, target_dir="/tmp/target", config=config)

        # Mock utils.get_audio_info to raise an exception
        with patch(
            "drumgizmo_kits_generator.audio.get_audio_info",
            side_effect=Exception("Error getting audio info"),
        ):
            # Call the function and expect an AudioProcessingError
            with pytest.raises(Exception) as excinfo:
                scan_source_files(run_data)

            # Check that the exception message contains the expected text
            assert "Error getting audio info" in str(excinfo.value)
