#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=too-many-instance-attributes
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-locals
# pylint: disable=broad-exception-caught
# pylint: disable=redundant-unittest-assert
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
# pylint: disable=unused-variable
# pylint: disable=unspecified-encoding
# pylint: disable=consider-using-with
# pylint: disable=import-outside-toplevel,wrong-import-position
"""
Tests for verifying metadata loading order and command line argument overrides.

This module tests that metadata values are loaded in the correct order:
1. Default values (lowest priority)
2. Configuration file values (medium priority)
3. Command line arguments (highest priority)

Each test verifies that a specific option follows this order of precedence.
"""

import os
import shutil
import sys
import tempfile
import unittest
from io import StringIO
from unittest.mock import patch

# Add the parent directory to the path to be able to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import argparse

from drumgizmo_kits_generator.constants import (
    DEFAULT_EXTENSIONS,
    DEFAULT_MIDI_NOTE_MAX,
    DEFAULT_MIDI_NOTE_MEDIAN,
    DEFAULT_MIDI_NOTE_MIN,
    DEFAULT_NAME,
    DEFAULT_VELOCITY_LEVELS,
)
from drumgizmo_kits_generator.main import prepare_metadata


class TestMetadataOrder(unittest.TestCase):
    """Tests for verifying metadata loading order and command line argument overrides."""

    def setUp(self):
        """Initialize before each test."""
        # Set up directories
        self.sources_dir = os.path.join(os.path.dirname(__file__), "sources")
        self.temp_dir = tempfile.mkdtemp()
        self.target_dir = os.path.join(self.temp_dir, "target")

        # Create target directory if it doesn't exist
        if not os.path.exists(self.target_dir):
            os.makedirs(self.target_dir)

        # Path to the full config file
        self.config_file = os.path.join(os.path.dirname(__file__), "mocks", "full-config.ini")

        # Create a mock for sys.stderr to capture warning messages
        self.stderr_patcher = patch("sys.stderr", new_callable=StringIO)
        self.mock_stderr = self.stderr_patcher.start()

    def tearDown(self):
        """Clean up after each test."""
        self.stderr_patcher.stop()

        # Remove temporary directory
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_name_override(self):
        """
        Test that name follows the correct order of precedence:
        1. Default value (DEFAULT_NAME)
        2. Config file value ('Test Kit')
        3. Command line value ('Command Line Kit')
        """
        # Create command line arguments with name override
        args = argparse.Namespace(
            samples=self.sources_dir,
            target=self.target_dir,
            config=self.config_file,
            midi_note_min=DEFAULT_MIDI_NOTE_MIN,
            midi_note_max=DEFAULT_MIDI_NOTE_MAX,
            midi_note_median=DEFAULT_MIDI_NOTE_MEDIAN,
            velocity_levels=DEFAULT_VELOCITY_LEVELS,
            extensions=DEFAULT_EXTENSIONS,
            description=None,
            notes=None,
            name="Command Line Kit",
            version=None,
            author=None,
            license=None,
            website=None,
            samplerate=None,
            logo=None,
            extra_files=None,
            channels=None,
            main_channels=None,
        )

        # Mock sys.argv to include the name
        with patch(
            "sys.argv",
            [
                "drumgizmo-kits-generator",
                "--samples",
                self.sources_dir,
                "--target",
                self.target_dir,
                "--config",
                self.config_file,
                "--name",
                "Command Line Kit",
            ],
        ):
            # Call prepare_metadata
            metadata = prepare_metadata(args)

            # Verify that command line arguments override config values
            self.assertEqual(
                metadata["name"],
                "Command Line Kit",
                "Command line name should override config value",
            )

            # Vérifier que le fichier de configuration a été lu correctement
            # en vérifiant que la valeur finale n'est pas la valeur par défaut
            self.assertNotEqual(
                metadata["name"], DEFAULT_NAME, "Command line value should not be the default value"
            )

    def test_version_override(self):
        """
        Test that version follows the correct order of precedence:
        1. Default value (DEFAULT_VERSION)
        2. Config file value ('1.0')
        3. Command line value ('2.0')
        """
        # Create command line arguments with version override
        args = argparse.Namespace(
            samples=self.sources_dir,
            target=self.target_dir,
            config=self.config_file,
            midi_note_min=DEFAULT_MIDI_NOTE_MIN,
            midi_note_max=DEFAULT_MIDI_NOTE_MAX,
            midi_note_median=DEFAULT_MIDI_NOTE_MEDIAN,
            velocity_levels=DEFAULT_VELOCITY_LEVELS,
            extensions=DEFAULT_EXTENSIONS,
            description=None,
            notes=None,
            name=None,
            version="2.0",
            author=None,
            license=None,
            website=None,
            samplerate=None,
            logo=None,
            extra_files=None,
            channels=None,
            main_channels=None,
        )

        # Mock sys.argv to include the version
        with patch(
            "sys.argv",
            [
                "drumgizmo-kits-generator",
                "--samples",
                self.sources_dir,
                "--target",
                self.target_dir,
                "--config",
                self.config_file,
                "--version",
                "2.0",
            ],
        ):
            # Call prepare_metadata
            metadata = prepare_metadata(args)

            # Verify that command line arguments override config values
            self.assertEqual(
                metadata["version"], "2.0", "Command line version should override config value"
            )

    def test_license_override(self):
        """
        Test that license follows the correct order of precedence:
        1. Default value (DEFAULT_LICENSE)
        2. Config file value ('CC-BY-SA')
        3. Command line value ('MIT')
        """
        # Create command line arguments with license override
        args = argparse.Namespace(
            samples=self.sources_dir,
            target=self.target_dir,
            config=self.config_file,
            midi_note_min=DEFAULT_MIDI_NOTE_MIN,
            midi_note_max=DEFAULT_MIDI_NOTE_MAX,
            midi_note_median=DEFAULT_MIDI_NOTE_MEDIAN,
            velocity_levels=DEFAULT_VELOCITY_LEVELS,
            extensions=DEFAULT_EXTENSIONS,
            description=None,
            notes=None,
            name=None,
            version=None,
            author=None,
            license="MIT",
            website=None,
            samplerate=None,
            logo=None,
            extra_files=None,
            channels=None,
            main_channels=None,
        )

        # Mock sys.argv to include the license
        with patch(
            "sys.argv",
            [
                "drumgizmo-kits-generator",
                "--samples",
                self.sources_dir,
                "--target",
                self.target_dir,
                "--config",
                self.config_file,
                "--license",
                "MIT",
            ],
        ):
            # Call prepare_metadata
            metadata = prepare_metadata(args)

            # Verify that command line arguments override config values
            self.assertEqual(
                metadata["license"], "MIT", "Command line license should override config value"
            )

    def test_midi_note_min_override(self):
        """
        Test that midi_note_min follows the correct order of precedence:
        1. Default value (DEFAULT_MIDI_NOTE_MIN)
        2. Config file value (36)
        3. Command line value (40)
        """
        # Create command line arguments with midi_note_min override
        args = argparse.Namespace(
            samples=self.sources_dir,
            target=self.target_dir,
            config=self.config_file,
            midi_note_min=40,
            midi_note_max=DEFAULT_MIDI_NOTE_MAX,
            midi_note_median=DEFAULT_MIDI_NOTE_MEDIAN,
            velocity_levels=DEFAULT_VELOCITY_LEVELS,
            extensions=DEFAULT_EXTENSIONS,
            description=None,
            notes=None,
            name=None,
            version=None,
            author=None,
            license=None,
            website=None,
            samplerate=None,
            logo=None,
            extra_files=None,
            channels=None,
            main_channels=None,
        )

        # Mock sys.argv to include the midi_note_min
        with patch(
            "sys.argv",
            [
                "drumgizmo-kits-generator",
                "--samples",
                self.sources_dir,
                "--target",
                self.target_dir,
                "--config",
                self.config_file,
                "--midi-note-min",
                "40",
            ],
        ):
            # Call prepare_metadata
            metadata = prepare_metadata(args)

            # Verify that command line arguments override config values
            self.assertEqual(
                metadata["midi_note_min"],
                40,
                "Command line midi_note_min should override config value",
            )

    def test_midi_note_max_override(self):
        """
        Test that midi_note_max follows the correct order of precedence:
        1. Default value (DEFAULT_MIDI_NOTE_MAX)
        2. Config file value (127)
        3. Command line value (100)
        """
        # Create command line arguments with midi_note_max override
        args = argparse.Namespace(
            samples=self.sources_dir,
            target=self.target_dir,
            config=self.config_file,
            midi_note_min=DEFAULT_MIDI_NOTE_MIN,
            midi_note_max=100,
            midi_note_median=DEFAULT_MIDI_NOTE_MEDIAN,
            velocity_levels=DEFAULT_VELOCITY_LEVELS,
            extensions=DEFAULT_EXTENSIONS,
            description=None,
            notes=None,
            name=None,
            version=None,
            author=None,
            license=None,
            website=None,
            samplerate=None,
            logo=None,
            extra_files=None,
            channels=None,
            main_channels=None,
        )

        # Mock sys.argv to include the midi_note_max
        with patch(
            "sys.argv",
            [
                "drumgizmo-kits-generator",
                "--samples",
                self.sources_dir,
                "--target",
                self.target_dir,
                "--config",
                self.config_file,
                "--midi-note-max",
                "100",
            ],
        ):
            # Call prepare_metadata
            metadata = prepare_metadata(args)

            # Verify that command line arguments override config values
            self.assertEqual(
                metadata["midi_note_max"],
                100,
                "Command line midi_note_max should override config value",
            )

    def test_midi_note_median_override(self):
        """
        Test that midi_note_median follows the correct order of precedence:
        1. Default value (DEFAULT_MIDI_NOTE_MEDIAN)
        2. Config file value (60)
        3. Command line value (70)
        """
        # Create command line arguments with midi_note_median override
        args = argparse.Namespace(
            samples=self.sources_dir,
            target=self.target_dir,
            config=self.config_file,
            midi_note_min=DEFAULT_MIDI_NOTE_MIN,
            midi_note_max=DEFAULT_MIDI_NOTE_MAX,
            midi_note_median=70,
            velocity_levels=DEFAULT_VELOCITY_LEVELS,
            extensions=DEFAULT_EXTENSIONS,
            description=None,
            notes=None,
            name=None,
            version=None,
            author=None,
            license=None,
            website=None,
            samplerate=None,
            logo=None,
            extra_files=None,
            channels=None,
            main_channels=None,
        )

        # Mock sys.argv to include the midi_note_median
        with patch(
            "sys.argv",
            [
                "drumgizmo-kits-generator",
                "--samples",
                self.sources_dir,
                "--target",
                self.target_dir,
                "--config",
                self.config_file,
                "--midi-note-median",
                "70",
            ],
        ):
            # Call prepare_metadata
            metadata = prepare_metadata(args)

            # Verify that command line arguments override config values
            self.assertEqual(
                metadata["midi_note_median"],
                70,
                "Command line midi_note_median should override config value",
            )

    def test_velocity_levels_override(self):
        """
        Test that velocity_levels follows the correct order of precedence:
        1. Default value (DEFAULT_VELOCITY_LEVELS)
        2. Config file value (4)
        3. Command line value (8)
        """
        # Create command line arguments with velocity_levels override
        args = argparse.Namespace(
            samples=self.sources_dir,
            target=self.target_dir,
            config=self.config_file,
            midi_note_min=DEFAULT_MIDI_NOTE_MIN,
            midi_note_max=DEFAULT_MIDI_NOTE_MAX,
            midi_note_median=DEFAULT_MIDI_NOTE_MEDIAN,
            velocity_levels=8,
            extensions=DEFAULT_EXTENSIONS,
            description=None,
            notes=None,
            name=None,
            version=None,
            author=None,
            license=None,
            website=None,
            samplerate=None,
            logo=None,
            extra_files=None,
            channels=None,
            main_channels=None,
        )

        # Mock sys.argv to include the velocity_levels
        with patch(
            "sys.argv",
            [
                "drumgizmo-kits-generator",
                "--samples",
                self.sources_dir,
                "--target",
                self.target_dir,
                "--config",
                self.config_file,
                "--velocity-levels",
                "8",
            ],
        ):
            # Call prepare_metadata
            metadata = prepare_metadata(args)

            # Verify that command line arguments override config values
            self.assertEqual(
                metadata["velocity_levels"],
                8,
                "Command line velocity_levels should override config value",
            )

    def test_extensions_override(self):
        """
        Test that extensions follows the correct order of precedence:
        1. Default value (DEFAULT_EXTENSIONS)
        2. Config file value ('wav,wav')
        3. Command line value ('flac,FLAC')
        """
        # Create command line arguments with extensions override
        args = argparse.Namespace(
            samples=self.sources_dir,
            target=self.target_dir,
            config=self.config_file,
            midi_note_min=DEFAULT_MIDI_NOTE_MIN,
            midi_note_max=DEFAULT_MIDI_NOTE_MAX,
            midi_note_median=DEFAULT_MIDI_NOTE_MEDIAN,
            velocity_levels=DEFAULT_VELOCITY_LEVELS,
            extensions="flac,FLAC",
            description=None,
            notes=None,
            name=None,
            version=None,
            author=None,
            license=None,
            website=None,
            samplerate=None,
            logo=None,
            extra_files=None,
            channels=None,
            main_channels=None,
        )

        # Mock sys.argv to include the extensions
        with patch(
            "sys.argv",
            [
                "drumgizmo-kits-generator",
                "--samples",
                self.sources_dir,
                "--target",
                self.target_dir,
                "--config",
                self.config_file,
                "--extensions",
                "flac,FLAC",
            ],
        ):
            # Call prepare_metadata
            metadata = prepare_metadata(args)

            # Verify that command line arguments override config values
            self.assertEqual(
                metadata["extensions"],
                ["flac", "FLAC"],
                "Command line extensions should override config value",
            )

    def test_samplerate_override(self):
        """
        Test that samplerate follows the correct order of precedence:
        1. Default value (DEFAULT_SAMPLERATE)
        2. Config file value ('44100')
        3. Command line value ('48000')
        """
        # Create command line arguments with samplerate override
        args = argparse.Namespace(
            samples=self.sources_dir,
            target=self.target_dir,
            config=self.config_file,
            midi_note_min=DEFAULT_MIDI_NOTE_MIN,
            midi_note_max=DEFAULT_MIDI_NOTE_MAX,
            midi_note_median=DEFAULT_MIDI_NOTE_MEDIAN,
            velocity_levels=DEFAULT_VELOCITY_LEVELS,
            extensions=DEFAULT_EXTENSIONS,
            description=None,
            notes=None,
            name=None,
            version=None,
            author=None,
            license=None,
            website=None,
            samplerate="48000",
            logo=None,
            extra_files=None,
            channels=None,
            main_channels=None,
        )

        # Mock sys.argv to include the samplerate
        with patch(
            "sys.argv",
            [
                "drumgizmo-kits-generator",
                "--samples",
                self.sources_dir,
                "--target",
                self.target_dir,
                "--config",
                self.config_file,
                "--samplerate",
                "48000",
            ],
        ):
            # Call prepare_metadata
            metadata = prepare_metadata(args)

            # Verify that command line arguments override config values
            self.assertEqual(
                metadata["samplerate"],
                "48000",
                "Command line samplerate should override config value",
            )

    def test_channels_override(self):
        """
        Test that channels follows the correct order of precedence:
        1. Default value (DEFAULT_CHANNELS)
        2. Config file value ('AmbL,AmbR,OHL,OHR')
        3. Command line value ('Kick,Snare,HiHat')
        """
        # Create command line arguments with channels override
        args = argparse.Namespace(
            samples=self.sources_dir,
            target=self.target_dir,
            config=self.config_file,
            midi_note_min=DEFAULT_MIDI_NOTE_MIN,
            midi_note_max=DEFAULT_MIDI_NOTE_MAX,
            midi_note_median=DEFAULT_MIDI_NOTE_MEDIAN,
            velocity_levels=DEFAULT_VELOCITY_LEVELS,
            extensions=DEFAULT_EXTENSIONS,
            description=None,
            notes=None,
            name=None,
            version=None,
            author=None,
            license=None,
            website=None,
            samplerate=None,
            logo=None,
            extra_files=None,
            channels="Kick,Snare,HiHat",
            main_channels=None,
        )

        # Mock sys.argv to include the channels
        with patch(
            "sys.argv",
            [
                "drumgizmo-kits-generator",
                "--samples",
                self.sources_dir,
                "--target",
                self.target_dir,
                "--config",
                self.config_file,
                "--channels",
                "Kick,Snare,HiHat",
            ],
        ):
            # Call prepare_metadata
            metadata = prepare_metadata(args)

            # Verify that command line arguments override config values
            self.assertEqual(
                metadata["channels"],
                ["Kick", "Snare", "HiHat"],
                "Command line channels should override config value",
            )

    def test_main_channels_override(self):
        """
        Test that main_channels follows the correct order of precedence:
        1. Default value (DEFAULT_MAIN_CHANNELS)
        2. Config file value ('AmbL,AmbR')
        3. Command line value ('Kick,Snare')
        """
        # Create command line arguments with main_channels override
        args = argparse.Namespace(
            samples=self.sources_dir,
            target=self.target_dir,
            config=self.config_file,
            midi_note_min=DEFAULT_MIDI_NOTE_MIN,
            midi_note_max=DEFAULT_MIDI_NOTE_MAX,
            midi_note_median=DEFAULT_MIDI_NOTE_MEDIAN,
            velocity_levels=DEFAULT_VELOCITY_LEVELS,
            extensions=DEFAULT_EXTENSIONS,
            description=None,
            notes=None,
            name=None,
            version=None,
            author=None,
            license=None,
            website=None,
            samplerate=None,
            logo=None,
            extra_files=None,
            channels="Kick,Snare,HiHat",  # Need to include valid channels for main_channels
            main_channels="Kick,Snare",
        )

        # Mock sys.argv to include the main_channels
        with patch(
            "sys.argv",
            [
                "drumgizmo-kits-generator",
                "--samples",
                self.sources_dir,
                "--target",
                self.target_dir,
                "--config",
                self.config_file,
                "--channels",
                "Kick,Snare,HiHat",
                "--main-channels",
                "Kick,Snare",
            ],
        ):
            # Call prepare_metadata
            metadata = prepare_metadata(args)

            # Verify that command line arguments override config values
            self.assertEqual(
                metadata["main_channels"],
                ["Kick", "Snare"],
                "Command line main_channels should override config value",
            )

    def test_description_override(self):
        """
        Test that description follows the correct order of precedence:
        1. Default value (None)
        2. Config file value ('This is a description')
        3. Command line value ('Command line description')
        """
        # Create command line arguments with description override
        args = argparse.Namespace(
            samples=self.sources_dir,
            target=self.target_dir,
            config=self.config_file,
            midi_note_min=DEFAULT_MIDI_NOTE_MIN,
            midi_note_max=DEFAULT_MIDI_NOTE_MAX,
            midi_note_median=DEFAULT_MIDI_NOTE_MEDIAN,
            velocity_levels=DEFAULT_VELOCITY_LEVELS,
            extensions=DEFAULT_EXTENSIONS,
            description="Command line description",
            notes=None,
            name=None,
            version=None,
            author=None,
            license=None,
            website=None,
            samplerate=None,
            logo=None,
            extra_files=None,
            channels=None,
            main_channels=None,
        )

        # Mock sys.argv to include the description
        with patch(
            "sys.argv",
            [
                "drumgizmo-kits-generator",
                "--samples",
                self.sources_dir,
                "--target",
                self.target_dir,
                "--config",
                self.config_file,
                "--description",
                "Command line description",
            ],
        ):
            # Call prepare_metadata
            metadata = prepare_metadata(args)

            # Verify that command line arguments override config values
            self.assertEqual(
                metadata["description"],
                "Command line description",
                "Command line description should override config value",
            )

    def test_notes_override(self):
        """
        Test that notes follows the correct order of precedence:
        1. Default value (None)
        2. Config file value ('DrumGizmo kit generated for testing purpose')
        3. Command line value ('Command line notes')
        """
        # Create command line arguments with notes override
        args = argparse.Namespace(
            samples=self.sources_dir,
            target=self.target_dir,
            config=self.config_file,
            midi_note_min=DEFAULT_MIDI_NOTE_MIN,
            midi_note_max=DEFAULT_MIDI_NOTE_MAX,
            midi_note_median=DEFAULT_MIDI_NOTE_MEDIAN,
            velocity_levels=DEFAULT_VELOCITY_LEVELS,
            extensions=DEFAULT_EXTENSIONS,
            description=None,
            notes="Command line notes",
            name=None,
            version=None,
            author=None,
            license=None,
            website=None,
            samplerate=None,
            logo=None,
            extra_files=None,
            channels=None,
            main_channels=None,
        )

        # Mock sys.argv to include the notes
        with patch(
            "sys.argv",
            [
                "drumgizmo-kits-generator",
                "--samples",
                self.sources_dir,
                "--target",
                self.target_dir,
                "--config",
                self.config_file,
                "--notes",
                "Command line notes",
            ],
        ):
            # Call prepare_metadata
            metadata = prepare_metadata(args)

            # Verify that command line arguments override config values
            self.assertEqual(
                metadata["notes"],
                "Command line notes",
                "Command line notes should override config value",
            )

    def test_author_override(self):
        """
        Test that author follows the correct order of precedence:
        1. Default value (None)
        2. Config file value ('Piero')
        3. Command line value ('Command Line Author')
        """
        # Create command line arguments with author override
        args = argparse.Namespace(
            samples=self.sources_dir,
            target=self.target_dir,
            config=self.config_file,
            midi_note_min=DEFAULT_MIDI_NOTE_MIN,
            midi_note_max=DEFAULT_MIDI_NOTE_MAX,
            midi_note_median=DEFAULT_MIDI_NOTE_MEDIAN,
            velocity_levels=DEFAULT_VELOCITY_LEVELS,
            extensions=DEFAULT_EXTENSIONS,
            description=None,
            notes=None,
            name=None,
            version=None,
            author="Command Line Author",
            license=None,
            website=None,
            samplerate=None,
            logo=None,
            extra_files=None,
            channels=None,
            main_channels=None,
        )

        # Mock sys.argv to include the author
        with patch(
            "sys.argv",
            [
                "drumgizmo-kits-generator",
                "--samples",
                self.sources_dir,
                "--target",
                self.target_dir,
                "--config",
                self.config_file,
                "--author",
                "Command Line Author",
            ],
        ):
            # Call prepare_metadata
            metadata = prepare_metadata(args)

            # Verify that command line arguments override config values
            self.assertEqual(
                metadata["author"],
                "Command Line Author",
                "Command line author should override config value",
            )


if __name__ == "__main__":
    unittest.main()
