#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name
# pylint: disable=unspecified-encoding
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-arguments
# pylint: disable=too-many-locals
# pylint: disable=too-many-lines
# pylint: disable=attribute-defined-outside-init
# pylint: disable=unused-argument
# pylint: disable=R0801 # code duplication
"""
SPDX-License-Identifier: MIT
SPDX-PackageName: DrumGizmo kits generator
SPDX-PackageHomePage: https://github.com/e-picas/drumgizmo-kits-generator
SPDX-FileCopyrightText: 2025 Pierre Cassat (Picas)

Tests for the main module of the DrumGizmo kit generator.
"""

import argparse
import os
import shutil
import tempfile
from unittest import mock

import pytest

from drumgizmo_kits_generator import constants, kit_generator, utils


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
        "drumgizmo_kits_generator.logger.section"
    ) as mock_section, mock.patch(
        "drumgizmo_kits_generator.logger.message"
    ) as mock_message, mock.patch(
        "drumgizmo_kits_generator.logger.set_verbose"
    ) as mock_set_verbose, mock.patch(
        "drumgizmo_kits_generator.logger.set_raw_output"
    ) as mock_set_raw_output, mock.patch(
        "drumgizmo_kits_generator.logger.print_action_start"
    ) as mock_print_action_start, mock.patch(
        "drumgizmo_kits_generator.logger.print_action_end"
    ) as mock_print_action_end:
        yield {
            "info": mock_info,
            "debug": mock_debug,
            "warning": mock_warning,
            "error": mock_error,
            "section": mock_section,
            "message": mock_message,
            "set_verbose": mock_set_verbose,
            "set_raw_output": mock_set_raw_output,
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
def sample_config_file(temp_dir):
    """Create a sample configuration file for testing."""
    config_content = """[drumgizmo_kit_generator]
name = "Test Kit"
version = "1.0"
description = "Test description"
notes = "Test notes"
author = "Test Author"
license = "CC-BY-SA"
website = "https://example.com"
samplerate = "48000"
velocity_levels = 3
midi_note_min = 0
midi_note_max = 127
midi_note_median = 60
extensions = "wav,flac,ogg"
channels = "Left,Right,Overhead"
main_channels = "Left,Right"
"""
    config_path = os.path.join(temp_dir, "test-config.ini")
    with open(config_path, "w") as f:
        f.write(config_content)
    yield config_path


@pytest.fixture
def sample_args():
    """Create sample command line arguments for testing."""
    args = argparse.Namespace()
    args.source = "/path/to/source"
    args.target = "/path/to/target"
    args.config = constants.DEFAULT_CONFIG_FILE
    args.verbose = False
    args.raw_output = False
    args.dry_run = False
    args.name = None
    args.version = None
    args.description = None
    args.notes = None
    args.author = None
    args.license = None
    args.website = None
    args.logo = None
    args.samplerate = None
    args.extra_files = None
    args.velocity_levels = None
    args.midi_note_min = None
    args.midi_note_max = None
    args.midi_note_median = None
    args.extensions = None
    args.channels = None
    args.main_channels = None
    return args


@pytest.fixture
def temp_config_file():
    """Create a temporary configuration file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ini", delete=False) as temp_file:
        temp_file.write(
            """[drumgizmo_kit_generator]
name = Test Kit
version = 1.0.0
description = Test description
notes = Test notes
author = Test Author
license = Test License
website = https://example.com
logo = logo.png
samplerate = 44100
extra_files = file1.txt,file2.txt
velocity_levels = 5
midi_note_min = 30
midi_note_max = 90
midi_note_median = 60
extensions = wav,flac
channels = Left,Right
main_channels = Left,Right
"""
        )
        temp_file_path = temp_file.name

    yield temp_file_path

    # Clean up
    if os.path.exists(temp_file_path):
        os.unlink(temp_file_path)


class TestEvaluateMidiMapping:
    """Tests for the evaluate_midi_mapping function."""

    def test_evaluate_midi_mapping_with_valid_input(self, mock_logger):
        """Test evaluate_midi_mapping with valid input."""
        # Setup
        audio_files = [
            "/path/to/source/Kick.wav",
            "/path/to/source/Snare.wav",
            "/path/to/source/HiHat.wav",
        ]

        metadata = {"midi_note_min": 30, "midi_note_max": 90, "midi_note_median": 60}

        # Mock utils functions
        with mock.patch(
            "drumgizmo_kits_generator.utils.extract_instrument_names"
        ) as mock_extract, mock.patch(
            "drumgizmo_kits_generator.utils.calculate_midi_mapping"
        ) as mock_calculate:
            # Configure mocks
            mock_extract.return_value = ["Kick", "Snare", "HiHat"]
            mock_calculate.return_value = {"Kick": 30, "Snare": 60, "HiHat": 90}

            # Call the function
            result = utils.evaluate_midi_mapping(audio_files, metadata)

            # Assertions
            mock_extract.assert_called_once_with(audio_files)
            mock_calculate.assert_called_once_with(
                ["Kick", "Snare", "HiHat"], {"min": 30, "max": 90, "median": 60}
            )
            assert result == {"Kick": 30, "Snare": 60, "HiHat": 90}

    def test_evaluate_midi_mapping_with_empty_files(self, mock_logger):
        """Test evaluate_midi_mapping with empty input list."""
        # Setup
        audio_files = []
        metadata = {"midi_note_min": 30, "midi_note_max": 90, "midi_note_median": 60}

        # Call the function
        result = utils.evaluate_midi_mapping(audio_files, metadata)

        # Assertions
        assert not result

    def test_evaluate_midi_mapping_with_missing_metadata(self, mock_logger):
        """Test evaluate_midi_mapping with missing metadata keys."""
        # Setup
        audio_files = ["/path/to/source/Kick.wav"]
        metadata = {}  # Missing required metadata keys

        # Mock utils functions
        with mock.patch(
            "drumgizmo_kits_generator.utils.extract_instrument_names"
        ) as mock_extract, mock.patch(
            "drumgizmo_kits_generator.utils.calculate_midi_mapping"
        ) as mock_calculate:
            # Configure mocks
            mock_extract.return_value = ["Kick"]
            mock_calculate.return_value = {"Kick": 60}  # Default value when min/max not specified

            # Call the function
            result = utils.evaluate_midi_mapping(audio_files, metadata)

            # Assertions
            mock_extract.assert_called_once_with(audio_files)
            mock_calculate.assert_called_once_with(
                ["Kick"], {"min": None, "max": None, "median": None}
            )
            assert result == {"Kick": 60}


class TestPrepareTargetDirectory:
    """Tests for the prepare_target_directory function (main.py)."""

    @mock.patch("os.path.exists")
    @mock.patch("os.makedirs")
    def test_prepare_target_directory_new(self, mock_makedirs, mock_exists, mock_logger):
        """Test prepare_target_directory with a new directory."""
        mock_exists.return_value = False
        kit_generator.prepare_target_directory("/path/to/target")
        mock_makedirs.assert_called_once_with("/path/to/target")
        assert mock_logger["section"].call_count >= 1
        assert mock_logger["print_action_start"].call_count >= 1

    @mock.patch("os.path.exists")
    @mock.patch("os.path.isdir")
    @mock.patch("os.listdir")
    @mock.patch("os.path.join")
    @mock.patch("shutil.rmtree")
    @mock.patch("os.remove")
    def test_prepare_target_directory_existing(
        self,
        mock_remove,
        mock_rmtree,
        mock_join,
        mock_listdir,
        mock_isdir,
        mock_exists,
        mock_logger,
    ):
        """Test prepare_target_directory with an existing directory."""
        mock_exists.return_value = True
        mock_listdir.return_value = ["file1.txt", "file2.txt", "dir1"]

        def mock_join_paths(dir_path, item):
            return f"{dir_path}/{item}"

        mock_join.side_effect = mock_join_paths

        def mock_is_dir(path):
            return "dir" in path

        mock_isdir.side_effect = mock_is_dir
        kit_generator.prepare_target_directory("/path/to/target")
        assert mock_logger["section"].call_count >= 1
        assert mock_logger["print_action_start"].call_count >= 1
        assert mock_listdir.call_count == 1
        mock_rmtree.assert_called_once_with("/path/to/target/dir1")
        assert mock_remove.call_count == 2
        mock_remove.assert_any_call("/path/to/target/file1.txt")
        mock_remove.assert_any_call("/path/to/target/file2.txt")


class TestScanSourceFiles:
    """Tests for the scan_source_files function in kit_generator module (returns dict)."""

    @mock.patch("drumgizmo_kits_generator.audio.get_audio_info")
    def test_scan_source_files(self, mock_get_info, temp_dir):
        """Test scan_source_files with valid input."""
        # Setup
        wav_file = os.path.join(temp_dir, "test1.wav")
        flac_file = os.path.join(temp_dir, "test2.flac")
        mp3_file = os.path.join(temp_dir, "test3.mp3")
        txt_file = os.path.join(temp_dir, "test4.txt")
        for f in [wav_file, flac_file, mp3_file, txt_file]:
            with open(f, "w"):
                pass
        # Sous-répertoire
        subdir = os.path.join(temp_dir, "subdir")
        os.makedirs(subdir)
        subdir_wav = os.path.join(subdir, "test5.wav")
        subdir_flac = os.path.join(subdir, "test6.flac")
        with open(subdir_wav, "w"):
            pass
        with open(subdir_flac, "w"):
            pass
        # Mock audio info
        mock_get_info.side_effect = lambda path: {"mocked": os.path.basename(path)}
        # Test extensions .wav/.flac
        result = kit_generator.scan_source_files(temp_dir, ["wav", "flac"])
        assert isinstance(result, dict)
        expected = {wav_file, flac_file, subdir_wav, subdir_flac}
        assert set(result.keys()) == expected
        for k in expected:
            assert result[k] == {"mocked": os.path.basename(k)}
        assert mp3_file not in result
        assert txt_file not in result
        # Test insensibilité à la casse
        result2 = kit_generator.scan_source_files(temp_dir, ["WAV", "FLAC"])
        assert set(result2.keys()) == expected
        for k in expected:
            assert result2[k] == {"mocked": os.path.basename(k)}
        # Test extensions vides
        result3 = kit_generator.scan_source_files(temp_dir, [])
        assert not result3


if __name__ == "__main__":
    pytest.main(["-v", __file__])
