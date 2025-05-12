#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SPDX-License-Identifier: MIT
SPDX-PackageName: DrumGizmo kits generator
SPDX-PackageHomePage: https://github.com/e-picas/drumgizmo-kits-generator
SPDX-FileCopyrightText: 2025 Pierre Cassat (Picas)

Tests for the convert_sample_rate function in audio.py
"""

import subprocess
import tempfile
from unittest.mock import patch

import pytest

from drumgizmo_kits_generator.audio import convert_sample_rate
from drumgizmo_kits_generator.exceptions import AudioProcessingError, DependencyError


def test_convert_sample_rate_dependency_error():
    """Test that convert_sample_rate raises DependencyError with context when SoX is not found."""
    # Mock shutil.which to return None (dependency not found)
    with patch("shutil.which", return_value=None):
        with pytest.raises(DependencyError) as excinfo:
            convert_sample_rate("test.wav", "44100")

        # Check that the exception has the expected message
        assert "SoX not found" in excinfo.value.message


def test_convert_sample_rate_subprocess_error():
    """Test that convert_sample_rate raises AudioProcessingError with context when subprocess fails."""
    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix=".wav") as temp_file:
        # Mock shutil.which to return a path (dependency found)
        with patch("shutil.which", return_value="/usr/bin/sox"):
            # Mock subprocess.run to raise CalledProcessError
            mock_error = subprocess.CalledProcessError(
                returncode=1,
                cmd=["sox", temp_file.name, "-r", "44100", "output.wav"],
                stderr="SoX failed: invalid audio format",
            )
            with patch("subprocess.run", side_effect=mock_error):
                with pytest.raises(AudioProcessingError) as excinfo:
                    convert_sample_rate(temp_file.name, "44100")

                # Check that the exception has the expected message and context
                assert "Failed to convert sample rate" in excinfo.value.message
                assert excinfo.value.context is not None
                assert "file" in excinfo.value.context
                assert "target_samplerate" in excinfo.value.context
                assert "exit_code" in excinfo.value.context
                assert "stderr" in excinfo.value.context
                assert excinfo.value.context["target_samplerate"] == "44100"
                assert excinfo.value.context["exit_code"] == 1
                assert "SoX failed" in excinfo.value.context["stderr"]


def test_convert_sample_rate_file_not_found():
    """Test that convert_sample_rate raises AudioProcessingError with context when file is not found."""
    # Mock shutil.which to return a path (dependency found)
    with patch("shutil.which", return_value="/usr/bin/sox"):
        # Mock subprocess.run to raise FileNotFoundError
        mock_error = FileNotFoundError(2, "No such file or directory", "test.wav")
        with patch("subprocess.run", side_effect=mock_error):
            with pytest.raises(AudioProcessingError) as excinfo:
                convert_sample_rate("test.wav", "44100")

            # Check that the exception has the expected message and context
            assert "File not found" in excinfo.value.message
            assert excinfo.value.context is not None
            assert "file" in excinfo.value.context
            assert "test.wav" in str(excinfo.value.context["file"])


def test_convert_sample_rate_cleanup_on_error():
    """Test that temporary files are cleaned up when an error occurs."""
    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix=".wav") as temp_file:
        # Mock shutil.which to return a path (dependency found)
        with patch("shutil.which", return_value="/usr/bin/sox"):
            # Mock subprocess.run to raise CalledProcessError
            mock_error = subprocess.CalledProcessError(
                returncode=1,
                cmd=["sox", temp_file.name, "-r", "44100", "output.wav"],
                stderr="SoX failed: invalid audio format",
            )

            # Mock os.remove and os.rmdir to track cleanup calls
            with patch("subprocess.run", side_effect=mock_error):
                with patch("os.remove") as mock_remove:
                    with patch("os.rmdir") as mock_rmdir:
                        with pytest.raises(AudioProcessingError):
                            convert_sample_rate(temp_file.name, "44100")

                        # Check that cleanup functions were called
                        assert mock_remove.called or mock_rmdir.called
