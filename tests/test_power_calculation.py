#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument
# pylint: disable=R0801 # code duplication
"""
SPDX-License-Identifier: MIT
SPDX-PackageName: DrumGizmo kits generator
SPDX-PackageHomePage: https://github.com/e-picas/drumgizmo-kits-generator
SPDX-FileCopyrightText: 2025 Pierre Cassat (Picas)

Tests for the power calculation in the xml_generator module.
"""

import os
import shutil
import tempfile
import xml.etree.ElementTree as ET
from unittest import mock

import pytest

from drumgizmo_kits_generator import xml_generator


@pytest.fixture
def mock_logger():
    """Mock logger functions."""
    with mock.patch("drumgizmo_kits_generator.logger.info") as mock_info, mock.patch(
        "drumgizmo_kits_generator.logger.debug"
    ) as mock_debug, mock.patch(
        "drumgizmo_kits_generator.logger.warning"
    ) as mock_warning, mock.patch(
        "drumgizmo_kits_generator.logger.error"
    ) as mock_error:
        yield {"info": mock_info, "debug": mock_debug, "warning": mock_warning, "error": mock_error}


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Clean up
    shutil.rmtree(temp_dir, ignore_errors=True)


def test_power_calculation_for_different_velocity_levels(temp_dir, mock_logger):
    """Test that power values are correctly calculated for different velocity levels."""
    # Test with different velocity levels
    velocity_levels_to_test = [3, 5, 10]

    for velocity_levels in velocity_levels_to_test:
        # Create metadata with specific velocity levels
        metadata = {
            "name": f"Test Kit {velocity_levels}",
            "version": "1.0",
            "samplerate": "44100",
            "velocity_levels": velocity_levels,
            "channels": ["Left", "Right"],
            "main_channels": ["Left", "Right"],
        }

        instrument_name = "TestInstrument"

        # Create instrument directory
        instrument_dir = os.path.join(temp_dir, instrument_name)
        os.makedirs(instrument_dir, exist_ok=True)

        # Generate instrument XML
        xml_generator.generate_instrument_xml(temp_dir, instrument_name, metadata, [])

        # Check that the file was created
        xml_path = os.path.join(instrument_dir, f"{instrument_name}.xml")
        assert os.path.exists(xml_path)

        # Parse the XML and check power values
        tree = ET.parse(xml_path)
        root = tree.getroot()

        # Get all sample elements
        sample_elems = root.findall(".//sample")
        assert len(sample_elems) == velocity_levels

        # Check power values follow the correct formula: (velocity_levels - i + 1) / velocity_levels
        expected_powers = [
            (velocity_levels - i + 1) / velocity_levels for i in range(1, velocity_levels + 1)
        ]
        actual_powers = [float(sample.get("power")) for sample in sample_elems]

        # Check that the first sample has power=1.0
        assert actual_powers[0] == 1.0

        # Check that the last sample has power=1/velocity_levels
        assert abs(actual_powers[-1] - (1.0 / velocity_levels)) < 0.000001

        # Check that all power values match expected values
        for actual, expected in zip(actual_powers, expected_powers):
            assert abs(actual - expected) < 0.000001


def test_power_values_decrease_linearly(temp_dir, mock_logger):
    """Test that power values decrease linearly from 1.0 to 1/velocity_levels."""
    # Create metadata with 10 velocity levels
    metadata = {
        "name": "Test Kit Linear",
        "version": "1.0",
        "samplerate": "44100",
        "velocity_levels": 10,
        "channels": ["Left", "Right"],
        "main_channels": ["Left", "Right"],
    }

    instrument_name = "LinearTest"

    # Create instrument directory
    instrument_dir = os.path.join(temp_dir, instrument_name)
    os.makedirs(instrument_dir, exist_ok=True)

    # Generate instrument XML
    xml_generator.generate_instrument_xml(temp_dir, instrument_name, metadata, [])

    # Check that the file was created
    xml_path = os.path.join(instrument_dir, f"{instrument_name}.xml")
    assert os.path.exists(xml_path)

    # Parse the XML and check power values
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Get all sample elements
    sample_elems = root.findall(".//sample")
    assert len(sample_elems) == 10

    # Get power values
    power_values = [float(sample.get("power")) for sample in sample_elems]

    # Check that power values decrease linearly
    # The difference between consecutive power values should be constant
    differences = [power_values[i] - power_values[i + 1] for i in range(len(power_values) - 1)]
    expected_difference = 0.1  # For 10 velocity levels, the difference should be 0.1

    for diff in differences:
        assert abs(diff - expected_difference) < 0.000001
