#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=unspecified-encoding
"""
SPDX-License-Identifier: MIT
SPDX-PackageName: DrumGizmo kits generator
SPDX-PackageHomePage: https://github.com/e-picas/drumgizmo-kits-generator
SPDX-FileCopyrightText: 2025 Pierre Cassat (Picas)

Tests for the copy_additional_files function in kit_generator.py
"""

import os
import tempfile
from unittest.mock import patch

import pytest

from drumgizmo_kits_generator.exceptions import DirectoryError
from drumgizmo_kits_generator.kit_generator import copy_additional_files
from drumgizmo_kits_generator.state import RunData


def test_copy_additional_files_logo_success():
    """Test that copy_additional_files successfully copies a logo file."""
    with tempfile.TemporaryDirectory() as source_dir:
        with tempfile.TemporaryDirectory() as target_dir:
            # Create a test logo file in the source directory
            logo_filename = "test_logo.png"
            logo_path = os.path.join(source_dir, logo_filename)
            with open(logo_path, "w") as f:
                f.write("test logo content")

            # Create a RunData instance with the test directories and logo
            config = {"logo": logo_filename}
            run_data = RunData(source_dir=source_dir, target_dir=target_dir, config=config)

            # Call the function
            copy_additional_files(run_data)

            # Check that the logo file was copied to the target directory
            target_logo_path = os.path.join(target_dir, logo_filename)
            assert os.path.exists(target_logo_path)
            with open(target_logo_path, "r") as f:
                assert f.read() == "test logo content"


def test_copy_additional_files_extra_files_success():
    """Test that copy_additional_files successfully copies extra files."""
    with tempfile.TemporaryDirectory() as source_dir:
        with tempfile.TemporaryDirectory() as target_dir:
            # Create test extra files in the source directory
            extra_file1 = "extra1.txt"
            extra_file2 = "extra2.txt"
            extra_path1 = os.path.join(source_dir, extra_file1)
            extra_path2 = os.path.join(source_dir, extra_file2)

            with open(extra_path1, "w") as f:
                f.write("extra file 1 content")
            with open(extra_path2, "w") as f:
                f.write("extra file 2 content")

            # Create a RunData instance with the test directories and extra files
            config = {"extra_files": f"{extra_file1},{extra_file2}"}
            run_data = RunData(source_dir=source_dir, target_dir=target_dir, config=config)

            # Call the function
            copy_additional_files(run_data)

            # Check that the extra files were copied to the target directory
            target_extra_path1 = os.path.join(target_dir, extra_file1)
            target_extra_path2 = os.path.join(target_dir, extra_file2)

            assert os.path.exists(target_extra_path1)
            assert os.path.exists(target_extra_path2)

            with open(target_extra_path1, "r") as f:
                assert f.read() == "extra file 1 content"
            with open(target_extra_path2, "r") as f:
                assert f.read() == "extra file 2 content"


def test_copy_additional_files_logo_not_found():
    """Test that copy_additional_files handles a missing logo file gracefully."""
    with tempfile.TemporaryDirectory() as source_dir:
        with tempfile.TemporaryDirectory() as target_dir:
            # Create a RunData instance with a non-existent logo
            config = {"logo": "non_existent_logo.png"}
            run_data = RunData(source_dir=source_dir, target_dir=target_dir, config=config)

            # Mock the logger to capture warnings
            with patch("drumgizmo_kits_generator.logger.warning") as mock_warning:
                # Call the function
                copy_additional_files(run_data)

                # Check that a warning was logged
                mock_warning.assert_called_once()
                assert "Logo file not found" in mock_warning.call_args[0][0]


def test_copy_additional_files_extra_file_not_found():
    """Test that copy_additional_files handles a missing extra file gracefully."""
    with tempfile.TemporaryDirectory() as source_dir:
        with tempfile.TemporaryDirectory() as target_dir:
            # Create one existing extra file
            extra_file1 = "extra1.txt"
            extra_path1 = os.path.join(source_dir, extra_file1)
            with open(extra_path1, "w") as f:
                f.write("extra file 1 content")

            # Create a RunData instance with one existing and one non-existent extra file
            config = {"extra_files": f"{extra_file1},non_existent_extra.txt"}
            run_data = RunData(source_dir=source_dir, target_dir=target_dir, config=config)

            # Mock the logger to capture warnings
            with patch("drumgizmo_kits_generator.logger.warning") as mock_warning:
                # Call the function
                copy_additional_files(run_data)

                # Check that a warning was logged for the non-existent file
                assert mock_warning.call_count == 1
                assert "Extra file not found" in mock_warning.call_args[0][0]

                # Check that the existing file was copied
                target_extra_path1 = os.path.join(target_dir, extra_file1)
                assert os.path.exists(target_extra_path1)


def test_copy_additional_files_file_not_found_error():
    """Test that copy_additional_files raises DirectoryError with context on FileNotFoundError."""
    with tempfile.TemporaryDirectory() as source_dir:
        with tempfile.TemporaryDirectory() as target_dir:
            # Create a test logo file in the source directory
            logo_filename = "test_logo.png"
            logo_path = os.path.join(source_dir, logo_filename)
            with open(logo_path, "w") as f:
                f.write("test logo content")

            # Create a RunData instance with the test directories and logo
            config = {"logo": logo_filename}
            run_data = RunData(source_dir=source_dir, target_dir=target_dir, config=config)

            # Mock shutil.copy2 to raise FileNotFoundError
            error = FileNotFoundError(2, "No such file or directory", logo_path)
            with patch("shutil.copy2", side_effect=error):
                # Call the function and expect a DirectoryError
                with pytest.raises(DirectoryError) as excinfo:
                    copy_additional_files(run_data)

                # Check that the exception has the expected message and context
                assert "File not found when copying additional files" in excinfo.value.message
                assert excinfo.value.context is not None
                assert "file" in excinfo.value.context
                assert "source_dir" in excinfo.value.context
                assert "target_dir" in excinfo.value.context
                assert excinfo.value.context["file"] == logo_path
                assert excinfo.value.context["source_dir"] == source_dir
                assert excinfo.value.context["target_dir"] == target_dir


def test_copy_additional_files_permission_error():
    """Test that copy_additional_files raises DirectoryError with context on PermissionError."""
    with tempfile.TemporaryDirectory() as source_dir:
        with tempfile.TemporaryDirectory() as target_dir:
            # Create a test logo file in the source directory
            logo_filename = "test_logo.png"
            logo_path = os.path.join(source_dir, logo_filename)
            with open(logo_path, "w") as f:
                f.write("test logo content")

            # Create a RunData instance with the test directories and logo
            config = {"logo": logo_filename}
            run_data = RunData(source_dir=source_dir, target_dir=target_dir, config=config)

            # Mock shutil.copy2 to raise PermissionError
            error = PermissionError(13, "Permission denied", logo_path)
            with patch("shutil.copy2", side_effect=error):
                # Call the function and expect a DirectoryError
                with pytest.raises(DirectoryError) as excinfo:
                    copy_additional_files(run_data)

                # Check that the exception has the expected message and context
                assert "Permission error when copying additional files" in excinfo.value.message
                assert excinfo.value.context is not None
                assert "file" in excinfo.value.context
                assert "error_code" in excinfo.value.context
                assert excinfo.value.context["file"] == logo_path
                assert excinfo.value.context["error_code"] == 13


def test_copy_additional_files_os_error():
    """Test that copy_additional_files raises DirectoryError with context on OSError."""
    with tempfile.TemporaryDirectory() as source_dir:
        with tempfile.TemporaryDirectory() as target_dir:
            # Create a test logo file in the source directory
            logo_filename = "test_logo.png"
            logo_path = os.path.join(source_dir, logo_filename)
            with open(logo_path, "w") as f:
                f.write("test logo content")

            # Create a RunData instance with the test directories and logo
            config = {"logo": logo_filename}
            run_data = RunData(source_dir=source_dir, target_dir=target_dir, config=config)

            # Mock shutil.copy2 to raise OSError
            error = OSError(5, "Input/output error", logo_path)
            with patch("shutil.copy2", side_effect=error):
                # Call the function and expect a DirectoryError
                with pytest.raises(DirectoryError) as excinfo:
                    copy_additional_files(run_data)

                # Check that the exception has the expected message and context
                assert "System error when copying additional files" in excinfo.value.message
                assert excinfo.value.context is not None
                assert "file" in excinfo.value.context
                assert "error_code" in excinfo.value.context
                assert excinfo.value.context["file"] == logo_path
                assert excinfo.value.context["error_code"] == 5


def test_copy_additional_files_generic_exception():
    """Test that copy_additional_files raises DirectoryError with context on generic Exception."""
    with tempfile.TemporaryDirectory() as source_dir:
        with tempfile.TemporaryDirectory() as target_dir:
            # Create a test logo file in the source directory
            logo_filename = "test_logo.png"
            logo_path = os.path.join(source_dir, logo_filename)
            with open(logo_path, "w") as f:
                f.write("test logo content")

            # Create a RunData instance with the test directories and logo
            config = {"logo": logo_filename}
            run_data = RunData(source_dir=source_dir, target_dir=target_dir, config=config)

            # Mock shutil.copy2 to raise a generic Exception
            error = Exception("Something went wrong")
            with patch("shutil.copy2", side_effect=error):
                # Call the function and expect a DirectoryError
                with pytest.raises(DirectoryError) as excinfo:
                    copy_additional_files(run_data)

                # Check that the exception has the expected message and context
                assert "Unexpected error when copying additional files" in excinfo.value.message
                assert excinfo.value.context is not None
                assert "exception_type" in excinfo.value.context
                assert "source_dir" in excinfo.value.context
                assert "target_dir" in excinfo.value.context
                assert excinfo.value.context["exception_type"] == "Exception"
                assert excinfo.value.context["source_dir"] == source_dir
                assert excinfo.value.context["target_dir"] == target_dir
