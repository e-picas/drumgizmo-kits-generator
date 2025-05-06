#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for the constants module.
"""

import os

from drumgizmo_kits_generator import constants


def test_app_constants_exist():
    """Test that application constants exist."""
    assert hasattr(constants, "APP_NAME")
    assert hasattr(constants, "APP_VERSION")
    assert hasattr(constants, "APP_LINK")

    # Verify they are not empty
    assert constants.APP_NAME
    assert constants.APP_VERSION
    assert constants.APP_LINK


def test_default_constants_exist():
    """Test that all default constants exist."""
    # Check for existence of all default constants
    default_constants = [
        "DEFAULT_EXTENSIONS",
        "DEFAULT_VELOCITY_LEVELS",
        "DEFAULT_MIDI_NOTE_MIN",
        "DEFAULT_MIDI_NOTE_MAX",
        "DEFAULT_MIDI_NOTE_MEDIAN",
        "DEFAULT_NAME",
        "DEFAULT_VERSION",
        "DEFAULT_LICENSE",
        "DEFAULT_SAMPLERATE",
        "DEFAULT_CHANNELS",
        "DEFAULT_MAIN_CHANNELS",
        "DEFAULT_CONFIG_FILE",
    ]

    for const in default_constants:
        assert hasattr(constants, const), f"Constant {const} is missing"


def test_default_constants_types():
    """Test that default constants have the correct types."""
    # Integer constants
    assert isinstance(constants.DEFAULT_VELOCITY_LEVELS, int)
    assert isinstance(constants.DEFAULT_MIDI_NOTE_MIN, int)
    assert isinstance(constants.DEFAULT_MIDI_NOTE_MAX, int)
    assert isinstance(constants.DEFAULT_MIDI_NOTE_MEDIAN, int)
    assert isinstance(constants.DEFAULT_SAMPLERATE, int)

    # String constants
    assert isinstance(constants.DEFAULT_EXTENSIONS, str)
    assert isinstance(constants.DEFAULT_NAME, str)
    assert isinstance(constants.DEFAULT_VERSION, str)
    assert isinstance(constants.DEFAULT_LICENSE, str)
    assert isinstance(constants.DEFAULT_CHANNELS, str)
    assert isinstance(constants.DEFAULT_MAIN_CHANNELS, str)
    assert isinstance(constants.DEFAULT_CONFIG_FILE, str)


def test_midi_note_constraints():
    """Test that MIDI note constants have correct relationships."""
    # MIDI notes should be in the range [0, 127]
    assert 0 <= constants.DEFAULT_MIDI_NOTE_MIN <= 127
    assert 0 <= constants.DEFAULT_MIDI_NOTE_MAX <= 127
    assert 0 <= constants.DEFAULT_MIDI_NOTE_MEDIAN <= 127

    # MIDI note relationships
    assert constants.DEFAULT_MIDI_NOTE_MIN < constants.DEFAULT_MIDI_NOTE_MAX
    assert constants.DEFAULT_MIDI_NOTE_MIN <= constants.DEFAULT_MIDI_NOTE_MEDIAN
    assert constants.DEFAULT_MIDI_NOTE_MEDIAN <= constants.DEFAULT_MIDI_NOTE_MAX


def test_velocity_levels_positive():
    """Test that velocity levels is a positive integer."""
    assert constants.DEFAULT_VELOCITY_LEVELS > 0


def test_project_root_exists():
    """Test that PROJECT_ROOT points to an existing directory."""
    assert os.path.isdir(constants.PROJECT_ROOT)


def test_pyproject_path_exists():
    """Test that PYPROJECT_PATH points to an existing file."""
    assert os.path.isfile(constants.PYPROJECT_PATH)


def test_main_channels_subset_of_channels():
    """Test that DEFAULT_MAIN_CHANNELS is a subset of DEFAULT_CHANNELS."""
    # Skip test if DEFAULT_MAIN_CHANNELS is empty
    if not constants.DEFAULT_MAIN_CHANNELS:
        return

    main_channels = constants.DEFAULT_MAIN_CHANNELS.split(",")
    all_channels = constants.DEFAULT_CHANNELS.split(",")

    for channel in main_channels:
        assert (
            channel in all_channels
        ), f"Channel {channel} in DEFAULT_MAIN_CHANNELS is not in DEFAULT_CHANNELS"
