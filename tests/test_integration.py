#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name
# pylint: disable=unspecified-encoding
# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
# pylint: disable=too-few-public-methods
"""
SPDX-License-Identifier: MIT
SPDX-PackageName: DrumGizmo kits generator
SPDX-PackageHomePage: https://github.com/e-picas/drumgizmo-kits-generator
SPDX-FileCopyrightText: 2025 Pierre Cassat (Picas)

Integration test for the DrumGizmo kit generator.
This test performs a complete generation from examples/sources/ to a temporary directory
and compares the results with examples/target/.
"""

import filecmp
import os
import re
import shutil
import tempfile
from pathlib import Path
from unittest import mock

import pytest

from drumgizmo_kits_generator import main


@pytest.fixture
def temp_output_dir():
    """Create a temporary directory for the test output."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Clean up
    shutil.rmtree(temp_dir, ignore_errors=True)


def normalize_xml_for_comparison(xml_content):
    """
    Normalize XML content for comparison by removing or standardizing parts that may differ
    between runs (like timestamps, version strings, etc.)
    """
    # Remove or standardize timestamps and dates
    xml_content = re.sub(
        r"Generated on \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", "Generated on DATE_TIME", xml_content
    )
    xml_content = re.sub(
        r"Generated at \d{4}-\d{2}-\d{2} \d{2}:\d{2}", "Generated at DATE_TIME", xml_content
    )

    # Normalize version strings
    xml_content = re.sub(
        r"with drumgizmo-kits-generator v\d+\.\d+\.\d+",
        "with drumgizmo-kits-generator vX.Y.Z",
        xml_content,
    )

    # Remove any other variable content that might change between runs
    # For example, absolute paths, temporary directory names, etc.

    return xml_content


def compare_xml_files(file1, file2):
    """
    Compare two XML files, ignoring differences in timestamps or other variable content.

    Args:
        file1: Path to the first XML file
        file2: Path to the second XML file

    Returns:
        bool: True if the files are equivalent, False otherwise
    """
    # Read and normalize both files
    with open(file1, "r") as f1, open(file2, "r") as f2:
        content1 = normalize_xml_for_comparison(f1.read())
        content2 = normalize_xml_for_comparison(f2.read())

    # Compare normalized content
    return content1 == content2


def compare_directories(dir1, dir2, ignore_patterns=None):
    """
    Compare two directories recursively.

    Args:
        dir1: Path to the first directory
        dir2: Path to the second directory
        ignore_patterns: List of regex patterns to ignore in the comparison

    Returns:
        tuple: (success, differences) where differences is a list of differences found
    """
    if ignore_patterns is None:
        ignore_patterns = []

    # Compile ignore patterns
    ignore_regexes = [re.compile(pattern) for pattern in ignore_patterns]

    differences = []

    # Get all files in both directories recursively
    dir1_files = set()
    for root, _, files in os.walk(dir1):
        rel_root = os.path.relpath(root, dir1)
        for file in files:
            rel_path = os.path.normpath(os.path.join(rel_root, file))
            # Skip files matching ignore patterns
            if not any(regex.search(rel_path) for regex in ignore_regexes):
                dir1_files.add(rel_path)

    dir2_files = set()
    for root, _, files in os.walk(dir2):
        rel_root = os.path.relpath(root, dir2)
        for file in files:
            rel_path = os.path.normpath(os.path.join(rel_root, file))
            # Skip files matching ignore patterns
            if not any(regex.search(rel_path) for regex in ignore_regexes):
                dir2_files.add(rel_path)

    # Check for missing files
    missing_in_dir2 = dir1_files - dir2_files
    for file in missing_in_dir2:
        differences.append(f"File missing in target directory: {file}")

    extra_in_dir2 = dir2_files - dir1_files
    for file in extra_in_dir2:
        differences.append(f"Extra file in target directory: {file}")

    # Compare common files
    common_files = dir1_files.intersection(dir2_files)
    for file in common_files:
        file1 = os.path.join(dir1, file)
        file2 = os.path.join(dir2, file)

        # Special handling for XML files
        if file.endswith(".xml"):
            if not compare_xml_files(file1, file2):
                differences.append(f"XML files differ: {file}")
        # Skip binary comparison for audio files (they will differ due to SoX processing)
        elif any(file.endswith(ext) for ext in [".wav", ".flac", ".ogg"]):
            # Just check that the file exists, which we already did
            pass
        else:
            # For non-XML and non-audio files, use standard file comparison
            if not filecmp.cmp(file1, file2, shallow=False):
                differences.append(f"Files differ: {file}")

    return len(differences) == 0, differences


def compare_output(output, reference_file, temp_dir=None, reference_dir=None):
    """
    Compare the output of the generation with a reference file.

    Args:
        output: The output string from the generation process
        reference_file: Path to the reference output file
        temp_dir: Temporary directory path used in the output (to be replaced)
        reference_dir: Reference directory path to replace temp_dir in the output

    Returns:
        tuple: (success, differences) where differences is a list of differences found
    """
    # Read the reference output
    with open(reference_file, "r", encoding="utf-8") as f:
        reference_output = f.read()

    # Replace paths if needed
    if temp_dir and reference_dir:
        output = output.replace(temp_dir, reference_dir)

    # Replace any date/time references which will differ between runs
    date_pattern = r"Generated with create_drumgizmo_kit\.py at [\d-]+ [\d:]+(?:\.\d+)?"
    output = re.sub(date_pattern, "Generated with create_drumgizmo_kit.py at DATE_TIME", output)
    reference_output = re.sub(
        date_pattern, "Generated with create_drumgizmo_kit.py at DATE_TIME", reference_output
    )

    # Compare the outputs line by line, ignoring empty lines and whitespace
    output_lines = [line.strip() for line in output.split("\n") if line.strip()]
    reference_lines = [line.strip() for line in reference_output.split("\n") if line.strip()]

    # Check if the outputs are the same length
    if len(output_lines) != len(reference_lines):
        return False, [
            f"Output has {len(output_lines)} lines, reference has {len(reference_lines)} lines"
        ]

    # Compare each line
    differences = []
    for i, (output_line, reference_line) in enumerate(zip(output_lines, reference_lines)):
        if output_line != reference_line:
            differences.append(
                f"Line {i+1} differs:\nOutput: {output_line}\nReference: {reference_line}"
            )

    return len(differences) == 0, differences


class TestIntegration:
    """Integration tests for the DrumGizmo kit generator."""

    def test_full_generation(self, temp_output_dir):
        """
        Test a full generation from examples/sources/ to a temporary directory
        and compare the results with examples/target/.
        """
        # Get the absolute paths
        project_root = Path(__file__).parent.parent
        source_dir = os.path.join(project_root, "examples", "sources")
        config_file = os.path.join(project_root, "examples", "drumgizmo-kit-example.ini")
        reference_dir = os.path.join(project_root, "examples", "target")

        # Run the generator directly with the appropriate arguments
        with mock.patch(
            "sys.argv",
            [
                "drumgizmo_kits_generator",
                "-s",
                source_dir,
                "-t",
                temp_output_dir,
                "-c",
                config_file,
            ],
        ):
            main.main()

        # Verify that the output directory exists and contains files
        assert os.path.exists(temp_output_dir)
        assert len(os.listdir(temp_output_dir)) > 0

        # Compare the output with the reference directory
        # Ignore patterns for files that might differ between runs
        ignore_patterns = [
            # Add patterns for files that should be ignored in the comparison
            # For example, temporary files, logs, etc.
            r"\.DS_Store$",  # macOS metadata files
            r"Thumbs\.db$",  # Windows thumbnail cache
            r"desktop\.ini$",  # Windows folder settings
        ]

        success, differences = compare_directories(temp_output_dir, reference_dir, ignore_patterns)

        # Print differences for debugging
        if not success:
            for diff in differences:
                print(diff)

        assert (
            success
        ), f"Generated output differs from reference: {len(differences)} differences found"

        # Verify specific important files
        assert os.path.exists(os.path.join(temp_output_dir, "drumkit.xml"))
        assert os.path.exists(os.path.join(temp_output_dir, "midimap.xml"))

        # Verify instrument directories and files
        for instrument in ["E-Mu-Proteus-FX-Wacky-Snare", "Example", "gs-16b-1c-44100hz"]:
            instrument_dir = os.path.join(temp_output_dir, instrument)
            assert os.path.exists(instrument_dir)
            assert os.path.exists(os.path.join(instrument_dir, f"{instrument}.xml"))

            # Verify samples directory and velocity variations
            samples_dir = os.path.join(instrument_dir, "samples")
            assert os.path.exists(samples_dir)

            # Check for velocity variations (1 to 4)
            for i in range(1, 5):
                # For Example.ogg, the extension should be preserved
                if instrument == "Example":
                    assert os.path.exists(os.path.join(samples_dir, f"{i}-{instrument}.ogg"))
                # For gs-16b-1c-44100hz.flac, the extension should be preserved
                elif instrument == "gs-16b-1c-44100hz":
                    assert os.path.exists(os.path.join(samples_dir, f"{i}-{instrument}.flac"))
                # For other instruments, the extension should be .wav
                else:
                    assert os.path.exists(os.path.join(samples_dir, f"{i}-{instrument}.wav"))

        # Verify extra files were copied
        assert os.path.exists(os.path.join(temp_output_dir, "Lorem Ipsum.pdf"))
        assert os.path.exists(
            os.path.join(temp_output_dir, "pngtree-music-notes-png-image_8660757.png")
        )


if __name__ == "__main__":
    pytest.main(["-v", __file__])
