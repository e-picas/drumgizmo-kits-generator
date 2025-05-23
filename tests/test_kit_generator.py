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

# NOTE: All tests in this file are already compatible with the RunData architecture.
# Each test constructs and manages its own RunData instance explicitly, so no patching is required.

"""

import argparse
import os
import shutil
import tempfile
from unittest import mock

import pytest

from drumgizmo_kits_generator import constants, kit_generator
from drumgizmo_kits_generator.exceptions import ValidationError
from drumgizmo_kits_generator.state import RunData


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

    def test_evaluate_midi_mapping_full_range(self, mock_logger):
        """Test evaluate_midi_mapping with as many instruments as MIDI notes (mapping exhaustif)."""
        min_note = 10
        max_note = 14
        instruments = [f"Instr{i}" for i in range(min_note, max_note + 1)]
        audio_files = [f"/src/{name}.wav" for name in instruments]
        metadata = {"midi_note_min": min_note, "midi_note_max": max_note, "midi_note_median": 12}
        with mock.patch("drumgizmo_kits_generator.utils.extract_instrument_names") as mock_extract:
            mock_extract.return_value = instruments
            run_data = RunData(source_dir="/src", target_dir="/target")
            run_data.audio_sources = audio_files
            run_data.config = metadata
            kit_generator.evaluate_midi_mapping(run_data)
        result = run_data.midi_mapping
        expected = dict(zip(instruments, range(min_note, max_note + 1)))
        assert result == expected

    def test_evaluate_midi_mapping_not_full_range(self, mock_logger):
        """Test evaluate_midi_mapping with fewer instruments than notes (algo médian classique)."""
        min_note = 10
        max_note = 14
        instruments = ["Kick", "Snare", "HiHat"]
        audio_files = [f"/src/{name}.wav" for name in instruments]
        metadata = {"midi_note_min": min_note, "midi_note_max": max_note, "midi_note_median": 12}
        with mock.patch("drumgizmo_kits_generator.utils.extract_instrument_names") as mock_extract:
            mock_extract.return_value = instruments
            run_data = RunData(source_dir="/src", target_dir="/target")
            run_data.audio_sources = audio_files
            run_data.config = metadata
            kit_generator.evaluate_midi_mapping(run_data)
        result = run_data.midi_mapping
        # Pour 3 instruments autour de 12 : [11, 12, 13]
        assert list(result.values()) == [11, 12, 13]

    def test_evaluate_midi_mapping_with_valid_input(self, mock_logger):
        """Test evaluate_midi_mapping with valid input."""
        # Setup
        metadata = {"midi_note_min": 30, "midi_note_max": 90, "midi_note_median": 60}

        # Mock utils functions
        # Construction correcte de audio_sources
        run_data = RunData(source_dir="/src", target_dir="/target")
        run_data.audio_sources = {"Kick": {}, "Snare": {}, "HiHat": {}}
        run_data.config = metadata
        kit_generator.evaluate_midi_mapping(run_data)
        result = run_data.midi_mapping
        # Assertions
        expected_mapping = {"Kick": 59, "Snare": 60, "HiHat": 61}
        assert result == expected_mapping

    def test_evaluate_midi_mapping_with_empty_files(self, mock_logger):
        """Test evaluate_midi_mapping with empty input list."""
        # Setup
        audio_files = []
        metadata = {"midi_note_min": 30, "midi_note_max": 90, "midi_note_median": 60}

        # Call the function
        run_data = RunData(source_dir="/src", target_dir="/target")
        run_data.audio_sources = audio_files
        run_data.config = metadata
        kit_generator.evaluate_midi_mapping(run_data)
        result = run_data.midi_mapping

        # Assertions
        assert not result

    def test_evaluate_midi_mapping_with_missing_metadata(self, mock_logger):
        """Test evaluate_midi_mapping with missing metadata keys."""
        # Setup
        metadata = {}  # Missing required metadata keys

        # Mock utils functions
        # Construction correcte de audio_sources
        run_data = RunData(source_dir="/src", target_dir="/target")
        run_data.audio_sources = {"Kick": {}}
        run_data.config = metadata
        kit_generator.evaluate_midi_mapping(run_data)
        result = run_data.midi_mapping
        # Assertions
        expected_mapping = {"Kick": 60}
        assert result == expected_mapping
        assert result == {"Kick": 60}


class TestPrepareTargetDirectory:
    """Tests for the prepare_target_directory function (main.py)."""

    @mock.patch("os.path.exists")
    @mock.patch("os.makedirs")
    def test_prepare_target_directory_new(self, mock_makedirs, mock_exists, mock_logger):
        """Test prepare_target_directory with a new directory."""
        mock_exists.return_value = False
        run_data = RunData(source_dir="/src", target_dir="/path/to/target")
        kit_generator.prepare_target_directory(run_data)
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
        run_data = RunData(source_dir="/src", target_dir="/path/to/target")
        kit_generator.prepare_target_directory(run_data)
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
    def test_scan_source_files_no_extensions(self, mock_get_info, temp_dir):
        """Test scan_source_files returns empty dict if extensions missing."""
        metadata = {"midi_note_min": 10, "midi_note_max": 20}
        # Crée un fichier
        path = os.path.join(temp_dir, "sample.wav")
        with open(path, "w"):
            pass
        run_data = RunData(source_dir=temp_dir, target_dir="/tmp/unused", config=metadata)
        kit_generator.scan_source_files(run_data)
        result = run_data.audio_sources
        assert not result

    @mock.patch("drumgizmo_kits_generator.audio.get_audio_info")
    def test_scan_source_files_missing_midi_min(self, mock_get_info, temp_dir):
        """Test scan_source_files lève KeyError si midi_note_min absent."""
        metadata = {"extensions": ["wav"], "midi_note_max": 20}
        path = os.path.join(temp_dir, "sample.wav")
        with open(path, "w"):
            pass
        run_data = RunData(source_dir=temp_dir, target_dir="/tmp/unused", config=metadata)
        with pytest.raises(ValidationError):
            kit_generator.scan_source_files(run_data)

    @mock.patch("drumgizmo_kits_generator.audio.get_audio_info")
    def test_scan_source_files_missing_midi_max(self, mock_get_info, temp_dir):
        """Test scan_source_files lève KeyError si midi_note_max absent."""
        metadata = {"extensions": ["wav"], "midi_note_min": 10}
        path = os.path.join(temp_dir, "sample.wav")
        with open(path, "w"):
            pass
        run_data = RunData(source_dir=temp_dir, target_dir="/tmp/unused", config=metadata)
        with pytest.raises(ValidationError):
            kit_generator.scan_source_files(run_data)

    @mock.patch("drumgizmo_kits_generator.audio.get_audio_info")
    def test_scan_source_files_too_many_files(self, mock_get_info, temp_dir, mock_logger):
        """Test scan_source_files warns and limits files if too many audio files are present."""
        midi_min = 10
        midi_max = 19  # plage = 10
        metadata = {"extensions": ["wav"], "midi_note_min": midi_min, "midi_note_max": midi_max}
        num_files = 15  # plus que la plage

        # Crée 15 fichiers audio
        for i in range(num_files):
            path = os.path.join(temp_dir, f"sample_{i}.wav")
            with open(path, "w"):
                pass

        mock_get_info.side_effect = lambda path: {"samplerate": 44100, "channels": 2}

        run_data = RunData(source_dir=temp_dir, target_dir="/tmp/unused", config=metadata)
        kit_generator.scan_source_files(run_data)
        result = run_data.audio_sources
        # La dict doit être limitée à la plage MIDI (10 fichiers)
        assert len(result) == (midi_max - midi_min + 1)
        # Un warning doit avoir été émis
        assert mock_logger["warning"].called
        # Le message doit mentionner le dépassement
        warning_args = "".join(str(a) for a in mock_logger["warning"].call_args[0])
        assert "exceeds MIDI note range" in warning_args

    @mock.patch("drumgizmo_kits_generator.audio.get_audio_info")
    def test_scan_source_files(self, mock_get_info, temp_dir):
        """Test scan_source_files with valid input."""

        metadata = {"extensions": ["wav", "flac"], "midi_note_min": 30, "midi_note_max": 90}
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
        mock_get_info.side_effect = lambda path: {
            "samplerate": 44100,
            "channels": 2,
            "mocked": os.path.basename(path),
        }
        # Test extensions .wav/.flac
        run_data = RunData(source_dir=temp_dir, target_dir="/tmp/unused", config=metadata)
        kit_generator.scan_source_files(run_data)
        result = run_data.audio_sources
        # Debug explicite en cas d’échec
        found_instruments = set(result.keys())
        expected_instruments = {"test1", "test2", "test5", "test6"}
        if found_instruments != expected_instruments:
            print("Expected:", expected_instruments)
            print("Found:", found_instruments)
        assert found_instruments == expected_instruments
        for inst in expected_instruments:
            assert result[inst]["mocked"].startswith(inst)
        assert mp3_file not in result
        assert txt_file not in result
        # Test insensibilité à la casse : inutile, car extensions sont prises de metadata
        # Test extensions vides : non pertinent, car extensions ne sont plus passées en paramètre


def test_print_metadata(mock_logger):
    """Test print_metadata function (déplacée dans kit_generator)."""
    config = {
        "name": "Test Kit",
        "version": "1.0.0",
        "description": "Test description",
        "notes": "Test notes",
        "author": "Test Author",
        "license": "Test License",
        "website": "https://example.com",
        "logo": "logo.png",
        "samplerate": "44100",
        "extra_files": ["file1.txt", "file2.txt"],
        "velocity_levels": 5,
        "variations_method": "linear",
        "midi_note_min": 30,
        "midi_note_max": 90,
        "midi_note_median": 60,
        "extensions": ["wav", "flac"],
        "channels": ["Left", "Right"],
        "main_channels": ["Left", "Right"],
    }

    run_data = RunData(source_dir="/src", target_dir="/target", config=config)
    kit_generator.print_metadata(run_data)
    mock_logger["section"].assert_called_with("Kit Metadata")
    assert mock_logger["info"].call_count >= 10  # Should call info for each metadata item


def test_validate_directories_valid(tmp_path):
    """Test validate_directories with valid directories."""
    # Setup
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    target_dir = tmp_path / "target"

    # Test (should not raise)
    kit_generator.validate_directories(
        RunData(source_dir=str(source_dir), target_dir=str(target_dir))
    )


def test_validate_directories_source_not_exists(tmp_path):
    """Test validate_directories with non-existent source directory."""
    # Setup
    source_dir = tmp_path / "nonexistent"
    target_dir = tmp_path / "target"

    # Test (should raise)
    with pytest.raises(kit_generator.ValidationError):
        kit_generator.validate_directories(
            RunData(source_dir=str(source_dir), target_dir=str(target_dir))
        )


def test_validate_directories_target_parent_not_exists(tmp_path):
    """Test validate_directories with non-existent target parent directory."""
    # Setup
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    target_dir = tmp_path / "nonexistent" / "target"

    # Test (should raise)
    with pytest.raises(kit_generator.ValidationError):
        kit_generator.validate_directories(
            RunData(source_dir=str(source_dir), target_dir=str(target_dir))
        )


if __name__ == "__main__":
    pytest.main(["-v", __file__])
