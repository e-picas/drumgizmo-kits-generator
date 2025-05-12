#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=unspecified-encoding
# pylint: disable=unused-argument
"""
SPDX-License-Identifier: MIT
SPDX-PackageName: DrumGizmo kits generator
SPDX-PackageHomePage: https://github.com/e-picas/drumgizmo-kits-generator
SPDX-FileCopyrightText: 2025 Pierre Cassat (Picas)

Tests for the process_audio_files function in kit_generator.py
"""

import os
import tempfile
from unittest.mock import patch

import pytest

from drumgizmo_kits_generator.exceptions import AudioProcessingError, DependencyError
from drumgizmo_kits_generator.kit_generator import process_audio_files
from drumgizmo_kits_generator.state import RunData


def test_process_audio_files_success():
    """Test that process_audio_files successfully processes audio files."""
    with tempfile.TemporaryDirectory() as source_dir:
        with tempfile.TemporaryDirectory() as target_dir:
            # Create a test audio file in the source directory
            audio_filename = "kick.wav"
            audio_path = os.path.join(source_dir, audio_filename)
            with open(audio_path, "w") as f:
                f.write("test audio content")

            # Create a RunData instance with the test directories and a mock audio source
            config = {
                "samplerate": "44100",
                "velocity_levels": 3,
                "variations_method": "linear",
            }

            # Mock audio sources - structure doit correspondre à celle utilisée dans la fonction
            audio_sources = {
                "kick": {
                    "source_path": audio_path,  # Utiliser source_path au lieu de path
                    "channels": 2,
                    "samplerate": "48000",
                    "duration": 1.0,
                }
            }

            run_data = RunData(
                source_dir=source_dir,
                target_dir=target_dir,
                config=config,
                audio_sources=audio_sources,
            )

            # Mock audio.process_sample to return a list of processed files
            mock_processed_files = {
                os.path.join(target_dir, "1-kick.wav"): {"volume": 1.0},
                os.path.join(target_dir, "2-kick.wav"): {"volume": 0.8},
                os.path.join(target_dir, "3-kick.wav"): {"volume": 0.6},
            }

            with patch(
                "drumgizmo_kits_generator.audio.process_sample", return_value=mock_processed_files
            ):
                # Call the function
                process_audio_files(run_data)

                # Check that the processed files were added to run_data
                assert run_data.audio_processed
                assert "kick" in run_data.audio_processed
                assert len(run_data.audio_processed["kick"]) == 3


def test_process_audio_files_dependency_error():
    """Test that process_audio_files raises DependencyError when SoX is not found."""
    with tempfile.TemporaryDirectory() as source_dir:
        with tempfile.TemporaryDirectory() as target_dir:
            # Create a test audio file in the source directory
            audio_filename = "kick.wav"
            audio_path = os.path.join(source_dir, audio_filename)
            with open(audio_path, "w") as f:
                f.write("test audio content")

            # Create a RunData instance with the test directories and a mock audio source
            config = {
                "samplerate": "44100",
                "velocity_levels": 3,
                "variations_method": "linear",
            }

            # Mock audio sources
            audio_sources = {
                "kick": {
                    "source_path": audio_path,
                    "channels": 2,
                    "samplerate": "48000",
                    "duration": 1.0,
                }
            }

            run_data = RunData(
                source_dir=source_dir,
                target_dir=target_dir,
                config=config,
                audio_sources=audio_sources,
            )

            # Mock audio.process_sample to raise DependencyError
            error = DependencyError("SoX not found in the system")
            with patch("drumgizmo_kits_generator.audio.process_sample", side_effect=error):
                # Call the function and expect a DependencyError
                with pytest.raises(DependencyError) as excinfo:
                    process_audio_files(run_data)

                # Check that the exception has the expected message
                assert "Missing dependency during audio processing" in excinfo.value.message
                assert "SoX not found" in excinfo.value.message


def test_process_audio_files_audio_processing_error():
    """Test that process_audio_files raises AudioProcessingError with context."""
    with tempfile.TemporaryDirectory() as source_dir:
        with tempfile.TemporaryDirectory() as target_dir:
            # Create a test audio file in the source directory
            audio_filename = "kick.wav"
            audio_path = os.path.join(source_dir, audio_filename)
            with open(audio_path, "w") as f:
                f.write("test audio content")

            # Create a RunData instance with the test directories and a mock audio source
            config = {
                "samplerate": "44100",
                "velocity_levels": 3,
                "variations_method": "linear",
            }

            # Mock audio sources
            audio_sources = {
                "kick": {
                    "source_path": audio_path,
                    "channels": 2,
                    "samplerate": "48000",
                    "duration": 1.0,
                }
            }

            run_data = RunData(
                source_dir=source_dir,
                target_dir=target_dir,
                config=config,
                audio_sources=audio_sources,
            )

            # Mock audio.process_sample to raise AudioProcessingError with context
            error_context = {
                "file": audio_path,
                "target_samplerate": "44100",
                "error": "Failed to process audio file",
            }
            error = AudioProcessingError("Failed to process audio file", context=error_context)

            with patch("drumgizmo_kits_generator.audio.process_sample", side_effect=error):
                # Call the function and expect an AudioProcessingError
                with pytest.raises(AudioProcessingError) as excinfo:
                    process_audio_files(run_data)

                # Check that the exception has the expected message and context
                assert "Failed to process audio file" in excinfo.value.message
                assert excinfo.value.context is not None
                assert "instrument" in excinfo.value.context
                assert "source_path" in excinfo.value.context
                assert "target_dir" in excinfo.value.context
                assert excinfo.value.context["instrument"] == "kick"
                assert excinfo.value.context["source_path"] == audio_path
                assert excinfo.value.context["target_dir"] == target_dir


def test_process_audio_files_with_multiple_instruments():
    """Test that process_audio_files correctly processes multiple instruments."""
    with tempfile.TemporaryDirectory() as source_dir:
        with tempfile.TemporaryDirectory() as target_dir:
            # Create multiple test audio files for testing
            audio_files = ["kick.wav", "snare.wav", "hihat.wav"]
            audio_sources = {}

            for filename in audio_files:
                audio_path = os.path.join(source_dir, filename)
                with open(audio_path, "w") as f:
                    f.write(f"test audio content for {filename}")

                instrument_name = os.path.splitext(filename)[0]
                audio_sources[instrument_name] = {
                    "source_path": audio_path,
                    "channels": 2,
                    "samplerate": "48000",
                    "duration": 1.0,
                }

            # Create a RunData instance with the test directories and mock audio sources
            config = {
                "samplerate": "44100",
                "velocity_levels": 3,
                "variations_method": "linear",
            }

            run_data = RunData(
                source_dir=source_dir,
                target_dir=target_dir,
                config=config,
                audio_sources=audio_sources,
            )

            # Mock audio.process_sample to return a list of processed files
            def mock_process_sample(file_path, target_dir, metadata, audio_info=None):
                instrument_name = os.path.splitext(os.path.basename(file_path))[0]
                return {
                    os.path.join(target_dir, f"1-{instrument_name}.wav"): {"volume": 1.0},
                    os.path.join(target_dir, f"2-{instrument_name}.wav"): {"volume": 0.8},
                    os.path.join(target_dir, f"3-{instrument_name}.wav"): {"volume": 0.6},
                }

            # Utiliser le mock pour process_sample
            with patch(
                "drumgizmo_kits_generator.audio.process_sample", side_effect=mock_process_sample
            ):
                # Call the function
                process_audio_files(run_data)

                # Check that the processed files were added to run_data
                assert run_data.audio_processed
                assert len(run_data.audio_processed) == len(audio_files)
                for instrument in audio_sources:
                    assert instrument in run_data.audio_processed
                    assert len(run_data.audio_processed[instrument]) == 3
