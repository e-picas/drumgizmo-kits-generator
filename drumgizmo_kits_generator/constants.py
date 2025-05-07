#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SPDX-License-Identifier: MIT
SPDX-PackageName: DrumGizmo kits generator
SPDX-PackageHomePage: https://github.com/e-picas/drumgizmo-kits-generator
SPDX-FileCopyrightText: 2025 Pierre Cassat (Picas)

Constants module for DrumGizmo kit generator.
Contains global constants used across the application.
All configuration entries default values are written here.
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

# Default values for command line arguments and configuration
DEFAULT_EXTENSIONS = "wav,WAV,flac,FLAC,ogg,OGG"
DEFAULT_VELOCITY_LEVELS = 10
DEFAULT_MIDI_NOTE_MIN = 0
DEFAULT_MIDI_NOTE_MAX = 127
DEFAULT_MIDI_NOTE_MEDIAN = 60
DEFAULT_NAME = "DrumGizmo Kit"
DEFAULT_VERSION = "1.0"
DEFAULT_LICENSE = "Private license"
DEFAULT_SAMPLERATE = 44100
DEFAULT_CHANNELS = "Left,Right"
DEFAULT_MAIN_CHANNELS = ""

# Default values for audio processing
DEFAULT_VELOCITY_VOLUME_MIN = 0.25  # Minimum volume factor (25%)
DEFAULT_VELOCITY_VOLUME_MAX = 1.0  # Maximum volume factor (100%)
DEFAULT_VELOCITY_FILENAME_FORMAT = (
    "{level}-{instrument}{ext}"  # Format for velocity variation filenames
)
DEFAULT_TEMP_DIR_PREFIX = "drumgizmo_"  # Prefix for temporary directories

# Default paths for instrument structure
DEFAULT_SAMPLES_DIR = "samples"  # Default name for samples directory within instrument directory

# Default configuration file name
DEFAULT_CONFIG_FILE = "drumgizmo-kit.ini"

# Default configuration object
DEFAULT_CONFIG_DATA = {
    "name": DEFAULT_NAME,
    "version": DEFAULT_VERSION,
    "license": DEFAULT_LICENSE,
    "samplerate": DEFAULT_SAMPLERATE,
    "extensions": DEFAULT_EXTENSIONS,
    "velocity_levels": DEFAULT_VELOCITY_LEVELS,
    "midi_note_min": DEFAULT_MIDI_NOTE_MIN,
    "midi_note_max": DEFAULT_MIDI_NOTE_MAX,
    "midi_note_median": DEFAULT_MIDI_NOTE_MEDIAN,
    "channels": DEFAULT_CHANNELS,
    "main_channels": DEFAULT_MAIN_CHANNELS,
    "description": None,
    "notes": None,
    "author": None,
    "website": None,
    "logo": None,
    "extra_files": None,
}
