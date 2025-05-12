#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=unspecified-encoding
"""
SPDX-License-Identifier: MIT
SPDX-PackageName: DrumGizmo kits generator
SPDX-FileCopyrightText: 2023 E-Picas <drumgizmo@e-picas.fr>
SPDX-FileType: SOURCE

Additional tests for the utils.py module
"""

import os
import subprocess

import pytest

from drumgizmo_kits_generator.exceptions import AudioProcessingError
from drumgizmo_kits_generator.utils import (
    get_file_basename,
    get_file_extension,
    get_instrument_name,
    handle_subprocess_error,
    join_paths,
    split_comma_separated,
    strip_quotes,
)


def test_get_instrument_name():
    """Test get_instrument_name function."""
    # Test with simple filename
    assert get_instrument_name("kick.wav") == "kick"

    # Test with velocity prefix
    assert get_instrument_name("1-kick.wav") == "kick"

    # Test with _converted suffix
    assert get_instrument_name("kick_converted.wav") == "kick"

    # Test with both velocity prefix and _converted suffix
    assert get_instrument_name("1-kick_converted.wav") == "kick"

    # Test with full path
    assert get_instrument_name("/path/to/kick.wav") == "kick"


def test_split_comma_separated():
    """Test split_comma_separated function."""
    # Test with simple string
    assert split_comma_separated("a,b,c") == ["a", "b", "c"]

    # Test with spaces
    assert split_comma_separated(" a , b , c ") == ["a", "b", "c"]

    # Test with empty items
    assert split_comma_separated("a,,c") == ["a", "c"]

    # Test with None
    assert split_comma_separated(None) == []

    # Test with non-string, non-list input
    assert split_comma_separated(123) == []

    # Test with list input
    assert split_comma_separated(["a", "b", "c"]) == ["a", "b", "c"]


def test_strip_quotes():
    """Test strip_quotes function."""
    # Test with double quotes
    assert strip_quotes('"test"') == "test"

    # Test with single quotes
    assert strip_quotes("'test'") == "test"

    # Test with no quotes
    assert strip_quotes("test") == "test"

    # Test with non-string input
    assert strip_quotes(123) == 123


def test_get_file_extension():
    """Test get_file_extension function."""
    # Test with simple file
    assert get_file_extension("test.wav") == "wav"

    # Test with full path
    assert get_file_extension("/path/to/test.wav") == "wav"

    # Test with dot option
    assert get_file_extension("test.wav", with_dot=True) == ".wav"

    # Test with uppercase extension
    assert get_file_extension("test.WAV") == "wav"

    # Test with uppercase extension and lowercase=False
    assert get_file_extension("test.WAV", lowercase=False) == "WAV"


def test_get_file_basename():
    """Test get_file_basename function."""
    # Test with simple file
    assert get_file_basename("test.wav") == "test"

    # Test with full path
    assert get_file_basename("/path/to/test.wav") == "test"

    # Test with no extension
    assert get_file_basename("test") == "test"


def test_handle_subprocess_error_with_subprocess_error():
    """Test handle_subprocess_error with a subprocess.CalledProcessError."""
    # Create a mock subprocess error
    cmd = ["sox", "input.wav", "output.wav"]
    error = subprocess.CalledProcessError(1, cmd)
    error.stderr = "Error: invalid audio format"

    # Test handling of the error
    with pytest.raises(AudioProcessingError) as excinfo:
        handle_subprocess_error(error, "converting audio")

    # Check the error message
    assert "Failed during converting audio" in str(excinfo.value)
    assert "invalid audio format" in str(excinfo.value)


def test_join_paths():
    """Test join_paths function."""
    # Test with multiple path components
    assert join_paths("path", "to", "file.txt") == os.path.join("path", "to", "file.txt")

    # Test with absolute path
    assert join_paths("/path", "to", "file.txt") == os.path.join("/path", "to", "file.txt")

    # Test with empty components
    assert join_paths("path", "", "file.txt") == os.path.join("path", "", "file.txt")
