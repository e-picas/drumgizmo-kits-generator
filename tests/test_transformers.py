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

    # Test with invalid value - should return default (10)
    assert transformers.transform_velocity_levels("invalid") == 10

    # Test with None - should return default (10)
    assert transformers.transform_velocity_levels(None) == 10


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
    assert transformers.transform_samplerate(44100) == 44100

    # Test with string
    assert transformers.transform_samplerate("48000") == 48000

    # Test with None - should return default (44100)
    assert transformers.transform_samplerate(None) == 44100


def test_transform_extensions():
    """Test the transform_extensions function."""
    # Test with comma-separated string
    assert transformers.transform_extensions("wav,WAV,flac") == ["wav", "WAV", "flac"]

    # Test with string with spaces
    assert transformers.transform_extensions("wav, WAV, flac") == ["wav", "WAV", "flac"]

    # Test with list
    assert transformers.transform_extensions(["wav", "WAV", "flac"]) == ["wav", "WAV", "flac"]

    # Test with empty string - should return default extensions
    default_extensions = ["wav", "WAV", "flac", "FLAC", "ogg", "OGG"]
    assert transformers.transform_extensions("") == default_extensions

    # Test with None - should return default extensions
    assert transformers.transform_extensions(None) == default_extensions


def test_transform_extensions_with_quotes():
    """Test transform_extensions with quoted values."""
    # Test with quotes
    assert transformers.transform_extensions('"wav,flac,ogg"') == ["wav", "flac", "ogg"]

    # Test with empty string - should return default extensions
    default_extensions = ["wav", "WAV", "flac", "FLAC", "ogg", "OGG"]
    assert transformers.transform_extensions("") == default_extensions

    # Test with None - should return default extensions
    assert transformers.transform_extensions(None) == default_extensions

    # Test with non-string value - should return default extensions
    assert transformers.transform_extensions(123) == default_extensions


def test_transform_channels():
    """Test the transform_channels function."""
    # Test with comma-separated string
    assert transformers.transform_channels("Kick,Snare,HiHat") == ["Kick", "Snare", "HiHat"]

    # Test with string with spaces
    assert transformers.transform_channels("Kick, Snare, HiHat") == ["Kick", "Snare", "HiHat"]

    # Test with list
    assert transformers.transform_channels(["Kick", "Snare", "HiHat"]) == ["Kick", "Snare", "HiHat"]

    # Test with empty string
    assert transformers.transform_channels("") == ["Left", "Right"]

    # Test with None
    assert transformers.transform_channels(None) == ["Left", "Right"]


def test_transform_channels_with_quotes():
    """Test transform_channels with quoted values."""
    # Test with quotes
    assert transformers.transform_channels('"Left,Right,Overhead"') == ["Left", "Right", "Overhead"]

    # Test with empty string
    assert transformers.transform_channels("") == ["Left", "Right"]

    # Test with non-string value
    assert transformers.transform_channels(None) == ["Left", "Right"]
    assert transformers.transform_channels(123) == ["Left", "Right"]


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


def test_transform_name():
    """Test the transform_name function."""
    # Test with string
    assert transformers.transform_name("My Kit") == "My Kit"

    # Test with string with quotes
    assert transformers.transform_name('"My Kit"') == "My Kit"

    # Test with None
    assert transformers.transform_name(None) == "DrumGizmo Kit"

    # Test with non-string value
    assert transformers.transform_name(123) == "123"


def test_transform_version():
    """Test the transform_version function."""
    # Test with string
    assert transformers.transform_version("2.0") == "2.0"

    # Test with string with quotes
    assert transformers.transform_version('"2.0"') == "2.0"

    # Test with None
    assert transformers.transform_version(None) == "1.0"

    # Test with non-string value
    assert transformers.transform_version(2.0) == "2.0"


def test_transform_description():
    """Test the transform_description function."""
    # Test with string
    assert transformers.transform_description("A great drum kit") == "A great drum kit"

    # Test with string with quotes
    assert transformers.transform_description('"A great drum kit"') == "A great drum kit"

    # Test with None
    assert transformers.transform_description(None) == ""

    # Test with non-string value
    assert transformers.transform_description(123) == "123"


def test_transform_notes():
    """Test the transform_notes function."""
    # Test with string
    assert transformers.transform_notes("Recorded in studio A") == "Recorded in studio A"

    # Test with string with quotes
    assert transformers.transform_notes('"Recorded in studio A"') == "Recorded in studio A"

    # Test with None
    assert transformers.transform_notes(None) == ""

    # Test with non-string value
    assert transformers.transform_notes(123) == "123"


def test_transform_author():
    """Test the transform_author function."""
    # Test with string
    assert transformers.transform_author("John Doe") == "John Doe"

    # Test with string with quotes
    assert transformers.transform_author('"John Doe"') == "John Doe"

    # Test with None
    assert transformers.transform_author(None) == ""

    # Test with non-string value
    assert transformers.transform_author(123) == "123"


def test_transform_license():
    """Test the transform_license function."""
    # Test with string
    assert transformers.transform_license("MIT") == "MIT"

    # Test with string with quotes
    assert transformers.transform_license('"GPL-3.0"') == "GPL-3.0"

    # Test with None
    assert transformers.transform_license(None) == "Private license"

    # Test with non-string value
    assert transformers.transform_license(123) == "123"


def test_transform_website():
    """Test the transform_website function."""
    # Test with string
    assert transformers.transform_website("https://example.com") == "https://example.com"

    # Test with string with quotes
    assert transformers.transform_website('"https://example.com"') == "https://example.com"

    # Test with None
    assert transformers.transform_website(None) == ""

    # Test with non-string value
    assert transformers.transform_website(123) == "123"


def test_transform_logo():
    """Test the transform_logo function."""
    # Test with string
    assert transformers.transform_logo("logo.png") == "logo.png"

    # Test with string with quotes
    assert transformers.transform_logo('"logo.png"') == "logo.png"

    # Test with None
    assert transformers.transform_logo(None) == ""

    # Test with non-string value
    assert transformers.transform_logo(123) == "123"
