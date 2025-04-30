#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Base test class for DrumGizmo Kit Generator tests.
"""
import os
import shutil
import tempfile
import unittest
from io import StringIO
from unittest.mock import patch


class BaseTestCase(unittest.TestCase):
    """Base test case for DrumGizmo Kit Generator tests."""

    def setUp(self):
        """Initialize before each test."""
        # Create a temporary directory for testing
        self.temp_dir = tempfile.mkdtemp()

        # Create a mock for sys.stderr to capture output
        self.stderr_patcher = patch("sys.stderr", new_callable=StringIO)
        self.mock_stderr = self.stderr_patcher.start()

    def tearDown(self):
        """Clean up after each test."""
        # Stop the stderr patcher
        self.stderr_patcher.stop()

        # Remove the temporary directory
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def clean_temp_dir_recursively(self):
        """Remove all files and subdirectories in the temporary directory."""
        if os.path.exists(self.temp_dir):
            # Remove all files and subdirectories
            for root, dirs, files in os.walk(self.temp_dir, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
