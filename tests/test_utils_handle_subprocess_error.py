#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SPDX-License-Identifier: MIT
SPDX-PackageName: DrumGizmo kits generator
SPDX-PackageHomePage: https://github.com/e-picas/drumgizmo-kits-generator
SPDX-FileCopyrightText: 2025 Pierre Cassat (Picas)

Tests for the handle_subprocess_error function in utils.py
"""

import subprocess

import pytest

from drumgizmo_kits_generator.exceptions import AudioProcessingError
from drumgizmo_kits_generator.utils import handle_subprocess_error


def test_handle_subprocess_error_called_process_error():
    """Test handling of CalledProcessError with context."""
    # Create a CalledProcessError
    error = subprocess.CalledProcessError(
        returncode=1,
        cmd=["sox", "input.wav", "-r", "44100", "output.wav"],
        stderr="SoX failed: invalid audio format",
    )
    # Add stdout attribute manually (not accepted as a constructor parameter)
    error.stdout = "Some stdout output"

    # Test handling the error
    with pytest.raises(AudioProcessingError) as excinfo:
        handle_subprocess_error(error, "sample rate conversion")

    # Check that the exception has the expected message and context
    assert "Failed during sample rate conversion" in excinfo.value.message
    assert excinfo.value.context is not None
    assert "command" in excinfo.value.context
    assert "exit_code" in excinfo.value.context
    assert "operation" in excinfo.value.context
    assert "stderr" in excinfo.value.context
    assert "stdout" in excinfo.value.context
    assert excinfo.value.context["exit_code"] == 1
    assert excinfo.value.context["operation"] == "sample rate conversion"
    assert "SoX failed" in excinfo.value.context["stderr"]
    assert "Some stdout output" in excinfo.value.context["stdout"]


def test_handle_subprocess_error_file_not_found():
    """Test handling of FileNotFoundError with context."""
    # Create a FileNotFoundError
    error = FileNotFoundError(2, "No such file or directory", "input.wav")

    # Test handling the error
    with pytest.raises(AudioProcessingError) as excinfo:
        handle_subprocess_error(error, "reading audio file")

    # Check that the exception has the expected message and context
    assert "File not found during reading audio file" in excinfo.value.message
    assert excinfo.value.context is not None
    assert "file" in excinfo.value.context
    assert "operation" in excinfo.value.context
    assert excinfo.value.context["file"] == "input.wav"
    assert excinfo.value.context["operation"] == "reading audio file"


def test_handle_subprocess_error_permission_error():
    """Test handling of PermissionError with context."""
    # Create a PermissionError
    error = PermissionError(13, "Permission denied", "output.wav")

    # Test handling the error
    with pytest.raises(AudioProcessingError) as excinfo:
        handle_subprocess_error(error, "writing audio file")

    # Check that the exception has the expected message and context
    assert "Permission error during writing audio file" in excinfo.value.message
    assert excinfo.value.context is not None
    assert "file" in excinfo.value.context
    assert "operation" in excinfo.value.context
    assert excinfo.value.context["file"] == "output.wav"
    assert excinfo.value.context["operation"] == "writing audio file"


def test_handle_subprocess_error_generic_exception():
    """Test handling of generic Exception with context."""
    # Create a generic Exception
    error = Exception("Something went wrong")

    # Test handling the error
    with pytest.raises(AudioProcessingError) as excinfo:
        handle_subprocess_error(error, "processing audio")

    # Check that the exception has the expected message and context
    assert "Unexpected error during processing audio" in excinfo.value.message
    assert excinfo.value.context is not None
    assert "exception_type" in excinfo.value.context
    assert "operation" in excinfo.value.context
    assert excinfo.value.context["exception_type"] == "Exception"
    assert excinfo.value.context["operation"] == "processing audio"


def test_handle_subprocess_error_from_exception_false():
    """Test handling of error with from_exception=False."""
    # Create an error
    error = subprocess.CalledProcessError(
        returncode=1,
        cmd=["sox", "input.wav", "-r", "44100", "output.wav"],
        stderr="SoX failed: invalid audio format",
    )

    # Test handling the error with from_exception=False
    with pytest.raises(AudioProcessingError) as excinfo:
        handle_subprocess_error(error, "sample rate conversion", from_exception=False)

    # Check that the exception has the expected message and context
    assert "Failed during sample rate conversion" in excinfo.value.message
    assert excinfo.value.context is not None

    # Check that the exception doesn't have a __cause__ attribute
    # This is a bit tricky to test directly, but we can check that the error
    # message doesn't include "The above exception was the direct cause of"
    assert "The above exception was the direct cause of" not in str(excinfo.getrepr())
