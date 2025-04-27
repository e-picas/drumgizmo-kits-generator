#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Constants module for DrumGizmo kit generator.
Contains global constants used across the application.
"""

import os

import tomlkit

# Get the absolute path to the project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Path to the pyproject.toml file
PYPROJECT_PATH = os.path.join(PROJECT_ROOT, "pyproject.toml")

# Read the pyproject.toml file
with open(PYPROJECT_PATH, "r", encoding="utf-8") as f:
    PYPROJECT = tomlkit.parse(f.read())

# Application information from pyproject.toml
APP_NAME = PYPROJECT["project"]["name"]
APP_VERSION = PYPROJECT["project"]["version"]
APP_LINK = PYPROJECT["project"]["urls"]["Homepage"]
