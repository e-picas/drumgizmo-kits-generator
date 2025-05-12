#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SPDX-License-Identifier: MIT
SPDX-PackageName: DrumGizmo kits generator
SPDX-PackageHomePage: https://github.com/e-picas/drumgizmo-kits-generator
SPDX-FileCopyrightText: 2025 Pierre Cassat (Picas)

Tests for the check_dependency function in utils.py
"""

from unittest.mock import patch

import pytest

from drumgizmo_kits_generator.exceptions import DependencyError
from drumgizmo_kits_generator.utils import check_dependency


def test_check_dependency_success():
    """Test that check_dependency returns the path when the command is found."""
    # Mock shutil.which to return a path (dependency found)
    with patch("shutil.which", return_value="/usr/bin/sox"):
        # This should not raise an exception
        result = check_dependency("sox")
        assert result == "/usr/bin/sox"


def test_check_dependency_not_found():
    """Test that check_dependency raises DependencyError when the command is not found."""
    # Mock shutil.which to return None (dependency not found)
    with patch("shutil.which", return_value=None):
        with pytest.raises(DependencyError) as excinfo:
            check_dependency("sox")

        # Check that the exception has the expected message
        assert "Dependency 'sox' not found" in excinfo.value.message


def test_check_dependency_custom_error_message():
    """Test that check_dependency uses the custom error message when provided."""
    # Mock shutil.which to return None (dependency not found)
    with patch("shutil.which", return_value=None):
        custom_message = "SoX is required for audio processing"
        with pytest.raises(DependencyError) as excinfo:
            check_dependency("sox", custom_message)

        # Check that the exception has the custom message
        assert custom_message in excinfo.value.message


def test_check_dependency_with_context():
    """Test that DependencyError raised by check_dependency can have context."""
    # Mock shutil.which to return None (dependency not found)
    with patch("shutil.which", return_value=None):
        # Create a DependencyError with context
        error_context = {
            "dependency": "sox",
            "required_version": "14.4.2",
            "operation": "audio processing",
        }

        try:
            # First try to check the dependency
            check_dependency("sox")
        except DependencyError as e:
            # Then add context to the exception
            e.context = error_context
            # Re-raise the exception
            with pytest.raises(DependencyError) as excinfo:
                raise e

            # Check that the exception has the expected context
            assert excinfo.value.context == error_context
            assert "dependency=sox" in str(excinfo.value)
            assert "required_version=14.4.2" in str(excinfo.value)
            assert "operation=audio processing" in str(excinfo.value)
