#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=unspecified-encoding
"""
SPDX-License-Identifier: MIT
SPDX-PackageName: DrumGizmo kits generator
SPDX-FileCopyrightText: 2023 E-Picas <drumgizmo@e-picas.fr>
SPDX-FileType: SOURCE

Tests for the prepare_directories function in kit_generator.py
"""

import os
import tempfile
from unittest.mock import patch

import pytest

from drumgizmo_kits_generator.kit_generator import prepare_target_directory
from drumgizmo_kits_generator.state import RunData


def test_prepare_target_directory_success():
    """Test that prepare_directories successfully creates the target directory."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a source directory
        source_dir = os.path.join(temp_dir, "source")
        os.makedirs(source_dir)

        # Create a target directory path (doesn't exist yet)
        target_dir = os.path.join(temp_dir, "target")

        # Create a RunData instance with the test directories
        run_data = RunData(source_dir=source_dir, target_dir=target_dir, config={})

        # Call the function
        prepare_target_directory(run_data)

        # Check that the target directory was created
        assert os.path.exists(target_dir)
        assert os.path.isdir(target_dir)


def test_prepare_target_directory_target_exists():
    """Test that prepare_directories works when the target directory already exists."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a source directory
        source_dir = os.path.join(temp_dir, "source")
        os.makedirs(source_dir)

        # Create a target directory that already exists
        target_dir = os.path.join(temp_dir, "target")
        os.makedirs(target_dir)

        # Create a RunData instance with the test directories
        run_data = RunData(source_dir=source_dir, target_dir=target_dir, config={})

        # Call the function
        prepare_target_directory(run_data)

        # Check that the target directory still exists
        assert os.path.exists(target_dir)
        assert os.path.isdir(target_dir)


def test_prepare_target_directory_permission_error():
    """Test that prepare_target_directory raises PermissionError when a permission error occurs."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a source directory
        source_dir = os.path.join(temp_dir, "source")
        os.makedirs(source_dir)

        # Create a target directory path
        target_dir = os.path.join(temp_dir, "target")

        # Create a RunData instance with the test directories
        run_data = RunData(source_dir=source_dir, target_dir=target_dir, config={})

        # Mock os.makedirs to raise a permission error
        with patch("os.makedirs", side_effect=PermissionError("Permission denied")):
            # Call the function and expect the original PermissionError to be raised
            with pytest.raises(PermissionError) as excinfo:
                prepare_target_directory(run_data)

            # Check that the exception has the expected message
            assert "Permission denied" in str(excinfo.value)


def test_prepare_target_directory_os_error():
    """Test that prepare_target_directory raises OSError when an OS error occurs."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a source directory
        source_dir = os.path.join(temp_dir, "source")
        os.makedirs(source_dir)

        # Create a target directory path
        target_dir = os.path.join(temp_dir, "target")

        # Create a RunData instance with the test directories
        run_data = RunData(source_dir=source_dir, target_dir=target_dir, config={})

        # Mock os.makedirs to raise an OS error
        with patch("os.makedirs", side_effect=OSError("OS error")):
            # Call the function and expect the original OSError to be raised
            with pytest.raises(OSError) as excinfo:
                prepare_target_directory(run_data)

            # Check that the exception has the expected message
            assert "OS error" in str(excinfo.value)


def test_prepare_target_directory_unexpected_error():
    """Test that prepare_target_directory raises Exception when an unexpected error occurs."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a source directory
        source_dir = os.path.join(temp_dir, "source")
        os.makedirs(source_dir)

        # Create a target directory path
        target_dir = os.path.join(temp_dir, "target")

        # Create a RunData instance with the test directories
        run_data = RunData(source_dir=source_dir, target_dir=target_dir, config={})

        # Mock os.makedirs to raise an unexpected error
        with patch("os.makedirs", side_effect=Exception("Unexpected error")):
            # Call the function and expect the original Exception to be raised
            with pytest.raises(Exception) as excinfo:
                prepare_target_directory(run_data)

            # Check that the exception has the expected message
            assert "Unexpected error" in str(excinfo.value)
