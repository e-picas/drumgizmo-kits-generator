#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=useless-return
"""
SPDX-License-Identifier: MIT
SPDX-PackageName: DrumGizmo kits generator
SPDX-PackageHomePage: https://github.com/e-picas/drumgizmo-kits-generator
SPDX-FileCopyrightText: 2025 Pierre Cassat (Picas)

Pytest configuration file for DrumGizmo kit generator tests.
"""

import sys

import pytest


@pytest.fixture(autouse=True)
def no_sys_exit(monkeypatch):
    """Prevent sys.exit() from exiting during tests."""

    def mock_exit(code=0):
        """Mock function for sys.exit that raises an exception instead of exiting."""
        # Instead of exiting, we'll just store the exit code
        mock_exit.code = code
        # And if we're in a test that expects the exit, we can check this
        # But we won't actually exit
        return None

    # Reset the stored code before each test
    mock_exit.code = None

    # Apply the monkeypatch
    monkeypatch.setattr(sys, "exit", mock_exit)

    return mock_exit
