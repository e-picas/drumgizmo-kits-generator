#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SPDX-License-Identifier: MIT
SPDX-PackageName: DrumGizmo kits generator
SPDX-PackageHomePage: https://github.com/e-picas/drumgizmo-kits-generator
SPDX-FileCopyrightText: 2025 Pierre Cassat (Picas)

Tests for the validate_directories function in kit_generator.py
"""

import os
import tempfile
from unittest.mock import patch

import pytest

from drumgizmo_kits_generator.exceptions import ValidationError
from drumgizmo_kits_generator.kit_generator import validate_directories
from drumgizmo_kits_generator.state import RunData


def test_validate_directories_success():
    """Test that validate_directories succeeds when both directories exist."""
    with tempfile.TemporaryDirectory() as source_dir:
        with tempfile.TemporaryDirectory() as target_dir:
            # Create a RunData instance with valid directories
            run_data = RunData(source_dir=source_dir, target_dir=target_dir)

            # This should not raise an exception
            validate_directories(run_data)


def test_validate_directories_source_not_exist():
    """Test that validate_directories raises ValidationError with context when source directory doesn't exist."""
    non_existent_source = "/path/that/does/not/exist"
    with tempfile.TemporaryDirectory() as target_dir:
        # Create a RunData instance with invalid source directory
        run_data = RunData(source_dir=non_existent_source, target_dir=target_dir)

        # Test with a non-existent source directory
        with pytest.raises(ValidationError) as excinfo:
            validate_directories(run_data)

        # Check that the exception has the expected message and context
        assert "Source directory" in excinfo.value.message
        assert non_existent_source in excinfo.value.message
        # Context is not explicitly set in the function, but we could add it in the future


def test_validate_directories_target_parent_not_exist():
    """Test that validate_directories raises ValidationError with context when target's parent directory doesn't exist."""
    with tempfile.TemporaryDirectory() as source_dir:
        non_existent_target_parent = "/path/that/does/not/exist"
        non_existent_target = os.path.join(non_existent_target_parent, "target")

        # Create a RunData instance with invalid target directory
        run_data = RunData(source_dir=source_dir, target_dir=non_existent_target)

        # Nous devons d'abord patcher isdir pour le répertoire source afin qu'il retourne True
        # puis patcher exists pour le répertoire cible afin qu'il retourne False
        # et enfin patcher isdir pour le parent du répertoire cible afin qu'il retourne False
        def mock_isdir(path):
            if path == source_dir:
                return True
            if path == os.path.dirname(os.path.abspath(non_existent_target)):
                return False
            return False

        with patch("os.path.isdir", side_effect=mock_isdir):
            with patch("os.path.exists", return_value=False):
                # Test with a non-existent target parent directory
                with pytest.raises(ValidationError) as excinfo:
                    validate_directories(run_data)

                # Check that the exception has the expected message and context
                assert "Parent directory of target" in excinfo.value.message
                assert non_existent_target_parent in excinfo.value.message
