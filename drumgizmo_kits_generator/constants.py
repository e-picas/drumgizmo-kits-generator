#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Constants module for DrumGizmo kit generator.
Contains global constants used across the application.
"""

import os
from typing import List

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

# Default values for command line arguments and configuration
DEFAULT_EXTENSIONS = "wav,WAV,flac,FLAC,ogg,OGG"
DEFAULT_VELOCITY_LEVELS = 10
DEFAULT_MIDI_NOTE_MIN = 0
DEFAULT_MIDI_NOTE_MAX = 127
DEFAULT_MIDI_NOTE_MEDIAN = 60
DEFAULT_NAME = "DrumGizmo Kit"
DEFAULT_VERSION = "1.0"
DEFAULT_LICENSE = "Private license"
DEFAULT_SAMPLERATE = "44100"

# Default audio channels
DEFAULT_CHANNELS: List[str] = [
    "AmbL",
    "AmbR",
    "Kick",
    "Snare",
    "Tom1",
    "Tom2",
    "Tom3",
    "HiHat",
    "Ride",
    "OHL",
    "OHR",
    "Room1",
    "Room2",
    "Bleed",
]

# Default main channels
DEFAULT_MAIN_CHANNELS: List[str] = ["AmbL", "AmbR", "OHL", "OHR"]
