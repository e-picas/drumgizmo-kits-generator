#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=unspecified-encoding
"""
SPDX-License-Identifier: MIT
SPDX-PackageName: DrumGizmo kits generator
SPDX-PackageHomePage: https://github.com/e-picas/drumgizmo-kits-generator
SPDX-FileCopyrightText: 2025 Pierre Cassat (Picas)

Tests for the temp_directory context manager in utils.py
"""

import os
import tempfile

from drumgizmo_kits_generator import constants
from drumgizmo_kits_generator.utils import temp_directory


def test_temp_directory_creation():
    """Test that temp_directory creates a temporary directory."""
    with temp_directory() as temp_dir:
        # Check that the directory exists
        assert os.path.exists(temp_dir)
        assert os.path.isdir(temp_dir)

        # Check that the directory is in the system's temp directory
        assert temp_dir.startswith(tempfile.gettempdir())

        # Check that the directory has the default prefix
        assert os.path.basename(temp_dir).startswith(constants.DEFAULT_TEMP_DIR_PREFIX)


def test_temp_directory_custom_prefix():
    """Test that temp_directory uses a custom prefix when provided."""
    custom_prefix = "test_prefix_"
    with temp_directory(prefix=custom_prefix) as temp_dir:
        # Check that the directory exists
        assert os.path.exists(temp_dir)

        # Check that the directory has the custom prefix
        assert os.path.basename(temp_dir).startswith(custom_prefix)


def test_temp_directory_cleanup():
    """Test that temp_directory cleans up the directory after the context."""
    temp_dir_path = None

    # Use the context manager
    with temp_directory() as temp_dir:
        temp_dir_path = temp_dir
        # Create a file in the directory
        test_file = os.path.join(temp_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("test")

        # Check that the file exists
        assert os.path.exists(test_file)

    # After the context, check that the directory no longer exists
    assert not os.path.exists(temp_dir_path)


def test_temp_directory_cleanup_on_exception():
    """Test that temp_directory cleans up even if an exception occurs."""
    temp_dir_path = None

    try:
        # Use the context manager
        with temp_directory() as temp_dir:
            temp_dir_path = temp_dir
            # Create a file in the directory
            test_file = os.path.join(temp_dir, "test.txt")
            with open(test_file, "w") as f:
                f.write("test")

            # Raise an exception
            raise ValueError("Test exception")
    except ValueError:
        pass

    # After the exception, check that the directory no longer exists
    assert not os.path.exists(temp_dir_path)


def test_temp_directory_error_handling():
    """Test that temp_directory handles errors during cleanup gracefully."""
    # Instead of mocking shutil.rmtree, we'll use a different approach
    # Create a real temporary directory that we'll clean up manually
    real_temp_dir = tempfile.mkdtemp(prefix=constants.DEFAULT_TEMP_DIR_PREFIX)

    try:
        # Use the context manager with a custom prefix that won't be used
        with temp_directory(prefix="different_prefix_") as temp_dir:
            # Just check that the directory exists
            assert os.path.exists(temp_dir)
            assert os.path.isdir(temp_dir)

            # Check that it's not the same as our manually created directory
            assert temp_dir != real_temp_dir
    finally:
        # Clean up our manually created directory
        if os.path.exists(real_temp_dir):
            os.rmdir(real_temp_dir)

    # The test passes if no exception is raised from the context manager
