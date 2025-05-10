#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name
# pylint: disable=R0801 # code duplication
"""
SPDX-License-Identifier: MIT
SPDX-PackageName: DrumGizmo kits generator
SPDX-PackageHomePage: https://github.com/e-picas/drumgizmo-kits-generator
SPDX-FileCopyrightText: 2025 Pierre Cassat (Picas)

Tests for the CLI module.
"""

import argparse
from unittest import mock

import pytest

from drumgizmo_kits_generator import cli, constants


@pytest.fixture
def mock_logger():
    """Mock logger functions."""
    with mock.patch("drumgizmo_kits_generator.logger.info") as mock_info, mock.patch(
        "drumgizmo_kits_generator.logger.debug"
    ) as mock_debug, mock.patch(
        "drumgizmo_kits_generator.logger.warning"
    ) as mock_warning, mock.patch(
        "drumgizmo_kits_generator.logger.error"
    ) as mock_error, mock.patch(
        "drumgizmo_kits_generator.logger.section"
    ) as mock_section, mock.patch(
        "drumgizmo_kits_generator.logger.message"
    ) as mock_message, mock.patch(
        "drumgizmo_kits_generator.logger.set_verbose"
    ) as mock_set_verbose, mock.patch(
        "drumgizmo_kits_generator.logger.set_raw_output"
    ) as mock_set_raw_output:
        yield {
            "info": mock_info,
            "debug": mock_debug,
            "warning": mock_warning,
            "error": mock_error,
            "section": mock_section,
            "message": mock_message,
            "set_verbose": mock_set_verbose,
            "set_raw_output": mock_set_raw_output,
        }


class TestParseArguments:
    """Tests for the parse_arguments function."""

    @mock.patch(
        "sys.argv", ["drumgizmo_kits_generator", "-s", "/path/to/source", "-t", "/path/to/target"]
    )
    def test_parse_arguments_minimal(self):
        """Test parse_arguments with minimal required arguments."""
        args = cli.parse_arguments()
        assert args.source == "/path/to/source"
        assert args.target == "/path/to/target"
        assert args.config == constants.DEFAULT_CONFIG_FILE
        assert not args.verbose
        assert not args.dry_run

    @mock.patch(
        "sys.argv",
        [
            "drumgizmo_kits_generator",
            "-s",
            "/path/to/source",
            "-t",
            "/path/to/target",
            "-c",
            "/path/to/config.ini",
            "-v",
            "-x",
            "--name",
            "Custom Kit",
            "--version",
            "2.0",
            "--description",
            "Custom description",
            "--notes",
            "Custom notes",
            "--author",
            "Custom Author",
            "--license",
            "MIT",
            "--website",
            "https://custom.com",
            "--logo",
            "custom-logo.png",
            "--samplerate",
            "96000",
            "--extra-files",
            "file1.txt,file2.pdf",
            "--velocity-levels",
            "5",
            "--midi-note-min",
            "10",
            "--midi-note-max",
            "100",
            "--midi-note-median",
            "55",
            "--extensions",
            "wav,aiff",
            "--channels",
            "Ch1,Ch2",
            "--main-channels",
            "Ch1",
        ],
    )
    def test_parse_arguments_full(self):
        """Test parse_arguments with all possible arguments."""
        args = cli.parse_arguments()
        assert args.source == "/path/to/source"
        assert args.target == "/path/to/target"
        assert args.config == "/path/to/config.ini"
        assert args.verbose
        assert args.dry_run
        assert args.name == "Custom Kit"
        assert args.version == "2.0"
        assert args.description == "Custom description"
        assert args.notes == "Custom notes"
        assert args.author == "Custom Author"
        assert args.license == "MIT"
        assert args.website == "https://custom.com"
        assert args.logo == "custom-logo.png"
        assert args.samplerate == "96000"
        assert args.extra_files == "file1.txt,file2.pdf"
        assert args.velocity_levels == "5"
        assert args.midi_note_min == "10"
        assert args.midi_note_max == "100"
        assert args.midi_note_median == "55"
        assert args.extensions == "wav,aiff"
        assert args.channels == "Ch1,Ch2"
        assert args.main_channels == "Ch1"

    @mock.patch("sys.exit")
    @mock.patch("builtins.print")
    @mock.patch("argparse.ArgumentParser.parse_known_args")
    def test_app_version_option(self, mock_parse_known_args, mock_print, mock_exit):
        """Test that --app-version option displays version and exits."""
        # Mock parse_known_args to return a namespace with app_version=True
        args = argparse.Namespace()
        args.app_version = True
        args.raw_output = False
        mock_parse_known_args.return_value = (args, [])

        # Call the function
        cli.parse_arguments()

        # Verify that print was called with the correct version string
        mock_print.assert_called_once_with(f"{constants.APP_NAME} v{constants.APP_VERSION}")

        # Verify that sys.exit was called with 0
        assert mock_exit.call_count > 0
        assert mock_exit.call_args_list[0] == mock.call(0)

    @mock.patch("sys.argv", ["drumgizmo_kits_generator", "-V"])
    @mock.patch("sys.exit")
    @mock.patch("builtins.print")
    def test_app_version_short_option(self, mock_print, mock_exit):
        """Test that -V option displays version and exits."""
        # Call the function
        cli.parse_arguments()

        # Verify that print was called with the correct version string
        mock_print.assert_called_once_with(f"{constants.APP_NAME} v{constants.APP_VERSION}")

        # Verify that sys.exit was called with 0
        assert mock_exit.call_count > 0
        assert mock_exit.call_args_list[0] == mock.call(0)
