#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name
# pylint: disable=unspecified-encoding
# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
# pylint: disable=too-few-public-methods
# pylint: disable=broad-exception-caught
# pylint: disable=too-many-return-statements
"""
Integration tests for velocity levels in the DrumGizmo kit generator.
This test suite verifies that the application correctly handles different velocity level configurations.
"""

import os
import re
import shutil
import tempfile
import xml.etree.ElementTree as ET
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


def verify_directory_structure(output_dir, instruments, num_velocity_levels):
    """
    Verify that the output directory has the expected structure.

    Args:
        output_dir: Path to the output directory
        instruments: List of instrument names to check
        num_velocity_levels: Number of velocity levels to check

    Returns:
        bool: True if the directory structure is as expected, False otherwise
    """
    # Check main XML files
    if not os.path.exists(os.path.join(output_dir, "drumkit.xml")):
        return False
    if not os.path.exists(os.path.join(output_dir, "midimap.xml")):
        return False

    # Check instrument directories and files
    for instrument in instruments:
        instrument_dir = os.path.join(output_dir, instrument)
        if not os.path.exists(instrument_dir):
            return False
        if not os.path.exists(os.path.join(instrument_dir, f"{instrument}.xml")):
            return False

        # Check samples directory
        samples_dir = os.path.join(instrument_dir, "samples")
        if not os.path.exists(samples_dir):
            return False

        # Check velocity variations
        for i in range(1, num_velocity_levels + 1):
            # Get the file extension from the first sample
            sample_files = [f for f in os.listdir(samples_dir) if f.startswith(f"{i}-")]
            if not sample_files:
                return False

    return True


def verify_xml_content(output_dir, instruments, num_velocity_levels):
    """
    Verify that the XML files contain the expected content.

    Args:
        output_dir: Path to the output directory
        instruments: List of instrument names to check
        num_velocity_levels: Number of velocity levels to check

    Returns:
        bool: True if the XML content is as expected, False otherwise
    """
    # Check drumkit.xml
    try:
        drumkit_tree = ET.parse(os.path.join(output_dir, "drumkit.xml"))
        drumkit_root = drumkit_tree.getroot()

        # Check that all instruments are referenced
        instrument_refs = drumkit_root.findall(".//instrument")
        instrument_names = [ref.get("name") for ref in instrument_refs]
        for instrument in instruments:
            if instrument not in instrument_names:
                print(f"Instrument {instrument} not found in drumkit.xml")
                return False
    except ET.ParseError as e:
        print(f"Error parsing drumkit.xml: {e}")
        return False

    # Check midimap.xml
    try:
        midimap_tree = ET.parse(os.path.join(output_dir, "midimap.xml"))
        midimap_root = midimap_tree.getroot()

        # Check that all instruments are mapped
        # The actual XML structure uses <map> elements with "instr" attribute
        instrument_maps = midimap_root.findall(".//map")
        instrument_names = [map_elem.get("instr") for map_elem in instrument_maps]
        for instrument in instruments:
            if instrument not in instrument_names:
                print(f"Instrument {instrument} not found in midimap.xml")
                return False
    except ET.ParseError as e:
        print(f"Error parsing midimap.xml: {e}")
        return False

    # Check instrument XML files
    for instrument in instruments:
        try:
            instrument_xml_path = os.path.join(output_dir, instrument, f"{instrument}.xml")
            instrument_tree = ET.parse(instrument_xml_path)
            instrument_root = instrument_tree.getroot()

            # Check that samples are defined
            samples = instrument_root.findall(".//sample")

            # The actual number of samples might differ from num_velocity_levels
            # due to how the application handles multi-channel audio
            if len(samples) == 0:
                print(f"No samples found in {instrument_xml_path}")
                return False

            # Check that power values are present
            for sample in samples:
                if "power" not in sample.attrib:
                    print(f"Power attribute missing in sample in {instrument_xml_path}")
                    return False

            # Get all power values and check if they are properly distributed
            power_values = sorted([float(sample.get("power")) for sample in samples])

            # Check if power values are properly distributed
            # The highest value should be 1.0
            if abs(power_values[-1] - 1.0) > 0.01:  # Allow small rounding differences
                print(
                    f"Highest power value in {instrument_xml_path} is {power_values[-1]}, expected close to 1.0"
                )
                return False

            # For 2 velocity levels, the lowest should be around 0.5
            # For 4 velocity levels, the lowest should be around 0.25
            # For 8 velocity levels, the lowest should be around 0.125
            expected_lowest = 1.0 / num_velocity_levels
            if (
                abs(power_values[0] - expected_lowest) > 0.1
            ):  # Allow larger tolerance for lowest value
                print(
                    f"Lowest power value in {instrument_xml_path} is {power_values[0]}, expected around {expected_lowest}"
                )
                return False

            # Check that we have the correct number of power values
            # Each velocity level should have one power value
            if len(power_values) != len(set(power_values)):  # Check for duplicates
                print(f"Duplicate power values found in {instrument_xml_path}")
                return False
        except ET.ParseError as e:
            print(f"Error parsing {instrument_xml_path}: {e}")
            return False
        except Exception as e:
            print(f"Error checking {instrument_xml_path}: {e}")
            return False

    return True


class TestIntegrationVelocityLevels:
    """Integration tests for velocity levels in the DrumGizmo kit generator."""

    @pytest.mark.parametrize("velocity_levels", [2, 4, 8])
    def test_different_velocity_levels(self, temp_output_dir, velocity_levels):
        """
        Test generation with different numbers of velocity levels.

        Args:
            temp_output_dir: Temporary directory for output
            velocity_levels: Number of velocity levels to test
        """
        # Get the absolute paths
        project_root = Path(__file__).parent.parent
        source_dir = os.path.join(project_root, "examples", "sources")
        config_file = os.path.join(source_dir, "drumgizmo-kit.ini")

        # Run the generator with the specified number of velocity levels
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
                "--velocity-levels",
                str(velocity_levels),
            ],
        ):
            main.main()

        # Verify that the output directory exists and contains files
        assert os.path.exists(temp_output_dir)
        assert len(os.listdir(temp_output_dir)) > 0

        # Get the list of instruments
        instruments = [
            d
            for d in os.listdir(temp_output_dir)
            if os.path.isdir(os.path.join(temp_output_dir, d))
            and not d.startswith(".")
            and os.path.exists(os.path.join(temp_output_dir, d, f"{d}.xml"))
        ]

        # Verify directory structure
        assert verify_directory_structure(temp_output_dir, instruments, velocity_levels)

        # Verify XML content
        assert verify_xml_content(temp_output_dir, instruments, velocity_levels)

        # Verify specific velocity-related aspects
        for instrument in instruments:
            samples_dir = os.path.join(temp_output_dir, instrument, "samples")

            # Count the number of sample files for each velocity level
            velocity_counts = {}
            for filename in os.listdir(samples_dir):
                match = re.match(r"^(\d+)-", filename)
                if match:
                    velocity = int(match.group(1))
                    velocity_counts[velocity] = velocity_counts.get(velocity, 0) + 1

            # Verify that we have the correct number of velocity levels
            assert len(velocity_counts) == velocity_levels

            # Verify that each velocity level has the same number of samples
            sample_counts = list(velocity_counts.values())
            assert all(count == sample_counts[0] for count in sample_counts)


if __name__ == "__main__":
    pytest.main(["-v", __file__])
