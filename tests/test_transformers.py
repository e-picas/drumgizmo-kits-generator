#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for the transformers module.
"""

from drumgizmo_kits_generator import transformers


def test_transform_velocity_levels():
    """Test the transform_velocity_levels function."""
    # Test with integer
    assert transformers.transform_velocity_levels(5) == 5

    # Test with string
    assert transformers.transform_velocity_levels("10") == 10

    # Test with invalid value
    assert transformers.transform_velocity_levels("invalid") == 0

    # Test with None
    assert transformers.transform_velocity_levels(None) == 0


def test_transform_midi_note_min():
    """Test the transform_midi_note_min function."""
    # Test with integer
    assert transformers.transform_midi_note_min(10) == 10

    # Test with string
    assert transformers.transform_midi_note_min("20") == 20

    # Test with invalid value
    assert transformers.transform_midi_note_min("invalid") == 0

    # Test with None
    assert transformers.transform_midi_note_min(None) == 0


def test_transform_midi_note_max():
    """Test the transform_midi_note_max function."""
    # Test with integer
    assert transformers.transform_midi_note_max(100) == 100

    # Test with string
    assert transformers.transform_midi_note_max("120") == 120

    # Test with invalid value
    assert transformers.transform_midi_note_max("invalid") == 127

    # Test with None
    assert transformers.transform_midi_note_max(None) == 127


def test_transform_midi_note_median():
    """Test the transform_midi_note_median function."""
    # Test with integer
    assert transformers.transform_midi_note_median(50) == 50

    # Test with string
    assert transformers.transform_midi_note_median("70") == 70

    # Test with invalid value
    assert transformers.transform_midi_note_median("invalid") == 60

    # Test with None
    assert transformers.transform_midi_note_median(None) == 60


def test_transform_samplerate():
    """Test the transform_samplerate function."""
    # Test with integer
    assert transformers.transform_samplerate(44100) == "44100"

    # Test with string
    assert transformers.transform_samplerate("48000") == "48000"

    # Test with None
    assert transformers.transform_samplerate(None) == "None"


def test_transform_extensions():
    """Test the transform_extensions function."""
    # Test with comma-separated string
    assert transformers.transform_extensions("wav,WAV,flac") == ["wav", "WAV", "flac"]

    # Test with string with spaces
    assert transformers.transform_extensions("wav, WAV, flac") == ["wav", "WAV", "flac"]

    # Test with list
    assert transformers.transform_extensions(["wav", "WAV", "flac"]) == ["wav", "WAV", "flac"]

    # Test with empty string
    assert transformers.transform_extensions("") == []

    # Test with None
    assert transformers.transform_extensions(None) == []


def test_transform_extensions_with_quotes():
    """Test transform_extensions with quoted values."""
    # Test with quotes
    assert transformers.transform_extensions('"wav,flac,ogg"') == ["wav", "flac", "ogg"]

    # Test with empty string
    assert transformers.transform_extensions("") == []

    # Test with non-string value
    assert transformers.transform_extensions(None) == []
    assert transformers.transform_extensions(123) == []


def test_transform_channels():
    """Test the transform_channels function."""
    # Test with comma-separated string
    assert transformers.transform_channels("Kick,Snare,HiHat") == ["Kick", "Snare", "HiHat"]

    # Test with string with spaces
    assert transformers.transform_channels("Kick, Snare, HiHat") == ["Kick", "Snare", "HiHat"]

    # Test with list
    assert transformers.transform_channels(["Kick", "Snare", "HiHat"]) == ["Kick", "Snare", "HiHat"]

    # Test with empty string
    assert transformers.transform_channels("") == []

    # Test with None
    assert transformers.transform_channels(None) == []


def test_transform_channels_with_quotes():
    """Test transform_channels with quoted values."""
    # Test with quotes
    assert transformers.transform_channels('"Left,Right,Overhead"') == ["Left", "Right", "Overhead"]

    # Test with empty string
    assert transformers.transform_channels("") == []

    # Test with non-string value
    assert transformers.transform_channels(None) == []
    assert transformers.transform_channels(123) == []


def test_transform_main_channels():
    """Test the transform_main_channels function."""
    # Test with comma-separated string
    assert transformers.transform_main_channels("Kick,Snare") == ["Kick", "Snare"]

    # Test with string with spaces
    assert transformers.transform_main_channels("Kick, Snare") == ["Kick", "Snare"]

    # Test with list
    assert transformers.transform_main_channels(["Kick", "Snare"]) == ["Kick", "Snare"]

    # Test with empty string
    assert transformers.transform_main_channels("") == []

    # Test with None
    assert transformers.transform_main_channels(None) == []


def test_transform_main_channels_with_quotes():
    """Test transform_main_channels with quoted values."""
    # Test with quotes
    assert transformers.transform_main_channels('"Left,Right"') == ["Left", "Right"]

    # Test with empty string
    assert transformers.transform_main_channels("") == []

    # Test with non-string value
    assert transformers.transform_main_channels(None) == []
    assert transformers.transform_main_channels(123) == []


def test_transform_extra_files():
    """Test the transform_extra_files function."""
    # Test with comma-separated string
    assert transformers.transform_extra_files("file1.txt,file2.pdf") == ["file1.txt", "file2.pdf"]

    # Test with string with spaces
    assert transformers.transform_extra_files("file1.txt, file2.pdf") == ["file1.txt", "file2.pdf"]

    # Test with list
    assert transformers.transform_extra_files(["file1.txt", "file2.pdf"]) == [
        "file1.txt",
        "file2.pdf",
    ]

    # Test with empty string
    assert transformers.transform_extra_files("") == []

    # Test with None
    assert transformers.transform_extra_files(None) == []


def test_transform_extra_files_with_quotes():
    """Test transform_extra_files with quoted values."""
    # Test with quotes
    assert transformers.transform_extra_files('"file1.txt,file2.pdf"') == ["file1.txt", "file2.pdf"]

    # Test with empty string
    assert transformers.transform_extra_files("") == []

    # Test with non-string value
    assert transformers.transform_extra_files(None) == []
    assert transformers.transform_extra_files(123) == []
