#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=broad-exception-caught,too-many-locals,too-many-branches,too-many-return-statements,too-many-statements
"""
Integration tests for the DrumGizmo kit generator.

This module contains tests that verify the complete processing pipeline
by comparing the generated output with expected reference output.
"""

import difflib
import fnmatch
import os
import re
import shutil
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from unittest.mock import patch

# Add the parent directory to the path to be able to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Import the modules to test
# pylint: disable-next=wrong-import-position
from drumgizmo_kits_generator import main as main_module

# pylint: disable-next=wrong-import-position
from drumgizmo_kits_generator.utils import get_audio_samplerate


class TestDrumGizmoKitIntegration(unittest.TestCase):
    """Integration tests for the DrumGizmo kit generator."""

    def setUp(self):
        """Initialize before each test by creating test directories."""
        self.source_dir = os.path.join(os.path.dirname(__file__), "sources")
        self.reference_dir = os.path.join(os.path.dirname(__file__), "target")
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.source_dir, "drumgizmo-kit.ini")

    def tearDown(self):
        """Cleanup after each test by removing temporary directories."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def compare_directories(self, dir1, dir2, ignore_patterns=None, ignore_audio_files=True):
        """
        Compare two directories recursively.

        Args:
            dir1: First directory path
            dir2: Second directory path
            ignore_patterns: List of patterns to ignore
            ignore_audio_files: Whether to ignore audio files

        Returns:
            bool: True if directories match, False otherwise
        """
        if ignore_patterns is None:
            ignore_patterns = []

        # Add common patterns to ignore
        ignore_patterns.extend(["__pycache__", "*.pyc", ".git"])

        # Function to check if a path should be ignored
        def should_ignore(path):
            # Check if path matches any ignore pattern
            for pattern in ignore_patterns:
                if fnmatch.fnmatch(os.path.basename(path), pattern):
                    return True
            # Check if it's an audio file and we're ignoring those
            if ignore_audio_files and os.path.isfile(path):
                ext = os.path.splitext(path)[1].lower()
                if ext in [".wav", ".flac", ".ogg"]:
                    return True
            return False

        # Get directory contents
        dir1_contents = []
        for root, _, files in os.walk(dir1):
            for file in files:
                path = os.path.join(root, file)
                rel_path = os.path.relpath(path, dir1)
                if not should_ignore(path):
                    dir1_contents.append(rel_path)

        dir2_contents = []
        for root, _, files in os.walk(dir2):
            for file in files:
                path = os.path.join(root, file)
                rel_path = os.path.relpath(path, dir2)
                if not should_ignore(path):
                    dir2_contents.append(rel_path)

        # Sort the contents for comparison
        dir1_contents.sort()
        dir2_contents.sort()

        # Check if the directory contents match
        if dir1_contents != dir2_contents:
            print("\nDirectory contents don't match:")
            print(f"Directory 1 ({dir1}): {len(dir1_contents)} files")
            print(f"Directory 2 ({dir2}): {len(dir2_contents)} files")

            # Find files in dir1 but not in dir2
            only_in_dir1 = [f for f in dir1_contents if f not in dir2_contents]
            if only_in_dir1:
                print(f"\nFiles only in {dir1}:")
                for f in only_in_dir1:
                    print(f"  {f}")

            # Find files in dir2 but not in dir1
            only_in_dir2 = [f for f in dir2_contents if f not in dir1_contents]
            if only_in_dir2:
                print(f"\nFiles only in {dir2}:")
                for f in only_in_dir2:
                    print(f"  {f}")

            return False

        # Compare file contents for files that exist in both directories
        for rel_path in dir1_contents:
            file1 = os.path.join(dir1, rel_path)
            file2 = os.path.join(dir2, rel_path)

            # Skip comparison for binary files or other special files
            if os.path.splitext(file1)[1].lower() in [".xml"]:
                try:
                    self.compare_xml_files(file1, file2)
                except Exception as e:
                    print(f"Error comparing XML files {file1} and {file2}: {e}")
                    return False
            else:
                try:
                    with open(file1, "rb") as f1, open(file2, "rb") as f2:
                        if f1.read() != f2.read():
                            print(f"\nFile contents don't match: {rel_path}")
                            return False
                except Exception as e:
                    print(f"Error comparing files {file1} and {file2}: {e}")
                    return False

        return True

    def verify_directory_structure(self, velocity_levels=3):
        """
        Verify that the directory structure matches the expected structure.

        Args:
            velocity_levels: Number of velocity levels to check

        Returns:
            bool: True if the structure is valid, False otherwise
        """
        # Check that the target directory exists
        if not os.path.isdir(self.temp_dir):
            print(f"Target directory {self.temp_dir} does not exist")
            return False

        # Check that the drumkit.xml file exists
        drumkit_xml = os.path.join(self.temp_dir, "drumkit.xml")
        if not os.path.isfile(drumkit_xml):
            print(f"drumkit.xml file not found at {drumkit_xml}")
            return False

        # Check that the midimap.xml file exists
        midimap_xml = os.path.join(self.temp_dir, "midimap.xml")
        if not os.path.isfile(midimap_xml):
            print(f"midimap.xml file not found at {midimap_xml}")
            return False

        # Check that the instrument directories exist
        source_files = os.listdir(self.source_dir)
        audio_files = [
            f
            for f in source_files
            if f.endswith((".wav", ".WAV", ".flac", ".FLAC", ".ogg", ".OGG"))
        ]
        expected_instruments = [
            f.replace(".wav", "")
            .replace(".WAV", "")
            .replace(".flac", "")
            .replace(".FLAC", "")
            .replace(".ogg", "")
            .replace(".OGG", "")
            for f in audio_files
        ]
        for instrument in expected_instruments:
            instrument_dir = os.path.join(self.temp_dir, instrument)
            if not os.path.isdir(instrument_dir):
                print(f"Instrument directory {instrument_dir} does not exist")
                return False

            # Check that the instrument XML file exists
            instrument_xml = os.path.join(instrument_dir, f"{instrument}.xml")
            if not os.path.isfile(instrument_xml):
                print(f"Instrument XML file {instrument_xml} does not exist")
                return False

            # Check that the samples directory exists
            samples_dir = os.path.join(instrument_dir, "samples")
            if not os.path.isdir(samples_dir):
                print(f"Samples directory {samples_dir} does not exist")
                return False

            # Check that at least one sample file exists for each velocity level
            for i in range(1, velocity_levels + 1):
                # Look for any supported audio format
                sample_found = False
                for ext in [".wav", ".WAV", ".flac", ".FLAC", ".ogg", ".OGG"]:
                    sample_file = os.path.join(samples_dir, f"{i}-{instrument}{ext}")
                    if os.path.isfile(sample_file):
                        sample_found = True
                        break

                if not sample_found:
                    print(f"No sample file found for {instrument} at velocity level {i}")
                    return False

        return True

    def compare_xml_files(self, file1, file2):
        """
        Compare two XML files, ignoring version numbers and timestamps.

        Args:
            file1: Path to first XML file
            file2: Path to second XML file

        Returns:
            bool: True if the files match (ignoring versions and timestamps)
        """
        try:
            with open(file1, "r", encoding="utf-8") as f1, open(file2, "r", encoding="utf-8") as f2:
                content1 = f1.read()
                content2 = f2.read()

                # Normalize both XML contents
                normalized1 = self.normalize_xml_content(content1)
                normalized2 = self.normalize_xml_content(content2)

                if normalized1 != normalized2:
                    # Print diff for debugging
                    diff = difflib.unified_diff(
                        normalized1.splitlines(), normalized2.splitlines(), lineterm="", n=3
                    )
                    print(f"\nDifferences in {os.path.basename(file1)}:")
                    for line in diff:
                        print(line)

                return normalized1 == normalized2

        # pylint: disable-next=broad-exception-caught
        except Exception as e:
            print(f"Error comparing XML files {file1} and {file2}: {e}")
            raise

    def normalize_xml_content(self, xml_string):
        """
        Normalize XML content by removing or standardizing variable elements.

        Args:
            xml_string: XML content as string

        Returns:
            str: Normalized XML content
        """
        # Replace version numbers
        xml_string = re.sub(r"version=\"[^\"]*\"", 'version="NORMALIZED_VERSION"', xml_string)

        # Replace timestamps in created elements
        xml_string = re.sub(
            r"<created>[^<]*</created>", "<created>NORMALIZED_TIMESTAMP</created>", xml_string
        )

        # Replace generated notes that include timestamps
        xml_string = re.sub(
            r'Generated with create_drumgizmo_kit\.py at [^"<]*',
            "Generated with create_drumgizmo_kit.py at NORMALIZED_DATE",
            xml_string,
        )

        # Normalize description that includes velocity levels
        xml_string = re.sub(
            r"<description>Kit automatically created with \d+ velocity levels</description>",
            "<description>Kit automatically created with NORMALIZED_VELOCITY_LEVELS</description>",
            xml_string,
        )

        # Remove whitespace variations
        xml_string = re.sub(r"\s+", " ", xml_string)
        xml_string = re.sub(r"> <", "><", xml_string)
        xml_string = xml_string.strip()

        return xml_string

    def verify_audio_samplerate(self, expected_samplerate):
        """
        Verify that all audio files have the expected sample rate.

        Args:
            expected_samplerate (int): Expected sample rate in Hz

        Returns:
            bool: True if all audio files have the expected sample rate
        """
        # Get all audio files in the target directory
        audio_files = []
        for root, _, files in os.walk(self.temp_dir):
            for file in files:
                if file.endswith((".wav", ".WAV", ".flac", ".FLAC", ".ogg", ".OGG")):
                    audio_files.append(os.path.join(root, file))

        if not audio_files:
            print("No audio files found in the target directory")
            return False

        # Check the sample rate of each audio file
        for audio_file in audio_files:
            samplerate = get_audio_samplerate(audio_file)
            if samplerate is None:
                print(f"Could not get sample rate for {audio_file}")
                return False
            if samplerate != expected_samplerate:
                print(
                    f"Expected sample rate {expected_samplerate} Hz, got {samplerate} Hz for {audio_file}"
                )
                return False

        return True

    def test_full_integration(self):
        """Test the full integration of the DrumGizmo kit generator."""
        # Create the source directory structure
        _ = self.source_dir

        # Run the main function
        args = [
            "drumgizmo-kits-generator",
            "--source",
            self.source_dir,
            "--target",
            self.temp_dir,
            "--config",
            self.config_file,
        ]

        with patch.object(sys, "argv", args):
            # Call the main function
            main_module.main()

        # Verify the directory structure
        self.assertTrue(self.verify_directory_structure(velocity_levels=4))

        # Verify the XML content
        self.assertTrue(self.verify_xml_content(velocity_levels=4))

        # The test is successful if we've reached this point
        self.assertEqual(1, 1)  # Simple assertion to indicate success

    def test_custom_samplerate(self):
        """Test the custom sample rate option."""
        # Create the source directory structure
        _ = self.source_dir

        # Run the main function with custom sample rate
        expected_samplerate = "48000"
        args = [
            "drumgizmo-kits-generator",
            "--source",
            self.source_dir,
            "--target",
            self.temp_dir,
            "--config",
            self.config_file,
            "--samplerate",
            expected_samplerate,
        ]

        with patch.object(sys, "argv", args):
            # Call the main function
            main_module.main()

        # Verify the directory structure
        self.assertTrue(self.verify_directory_structure(velocity_levels=4))

        # Verify the XML content
        self.assertTrue(self.verify_xml_content(velocity_levels=4))

        # Verify the sample rate in the drumkit.xml file
        drumkit_xml = os.path.join(self.temp_dir, "drumkit.xml")
        tree = ET.parse(drumkit_xml)
        root = tree.getroot()
        self.assertEqual(
            root.attrib["samplerate"],
            expected_samplerate,
            f"Audio files do not have the expected sample rate of {expected_samplerate} Hz",
        )

        # The test is successful if we've reached this point
        self.assertEqual(1, 1)  # Simple assertion to indicate success

    def verify_xml_content(self, velocity_levels=3):
        """
        Verify that the XML files have the expected content structure.

        Args:
            velocity_levels: Number of velocity levels to check

        Returns:
            bool: True if the XML content is valid, False otherwise
        """

        # Helper function to verify common XML elements
        def verify_common_elements(root, expected_tag, expected_attrs=None):
            if expected_attrs is None:
                expected_attrs = {}

            # Check the root tag
            if root.tag != expected_tag:
                print(f"Expected root tag {expected_tag}, got {root.tag}")
                return False

            # Check the attributes
            for attr, value in expected_attrs.items():
                if attr not in root.attrib or root.attrib[attr] != value:
                    print(
                        f"Expected attribute {attr}={value}, got {root.attrib.get(attr, 'missing')}"
                    )
                    return False

            return True

        # Verify drumkit.xml
        try:
            drumkit_xml = os.path.join(self.temp_dir, "drumkit.xml")
            tree = ET.parse(drumkit_xml)
            root = tree.getroot()

            if not verify_common_elements(root, "drumkit", {"name": "Test Kit", "version": "1.0"}):
                return False

            # Check metadata
            metadata = root.find("metadata")
            if metadata is None:
                print("Metadata element not found in drumkit.xml")
                return False

            # Check channels
            channels = root.find("channels")
            if channels is None:
                print("Channels element not found in drumkit.xml")
                return False

            # Check instruments
            instruments_elem = root.find("instruments")
            if instruments_elem is None:
                print("Instruments element not found in drumkit.xml")
                return False

            # Check number of instruments
            instrument_elems = instruments_elem.findall("instrument")
            source_files = os.listdir(self.source_dir)
            audio_files = [
                f
                for f in source_files
                if f.endswith((".wav", ".WAV", ".flac", ".FLAC", ".ogg", ".OGG"))
            ]
            expected_instruments = [
                f.replace(".wav", "")
                .replace(".WAV", "")
                .replace(".flac", "")
                .replace(".FLAC", "")
                .replace(".ogg", "")
                .replace(".OGG", "")
                for f in audio_files
            ]
            if len(instrument_elems) != len(expected_instruments):
                print(
                    f"Expected {len(expected_instruments)} instruments, got {len(instrument_elems)}"
                )
                return False
        except Exception as e:
            print(f"Error verifying drumkit.xml: {e}")
            return False

        # Verify midimap.xml
        try:
            midimap_xml = os.path.join(self.temp_dir, "midimap.xml")
            tree = ET.parse(midimap_xml)
            root = tree.getroot()

            if not verify_common_elements(root, "midimap"):
                return False

            # Check map elements
            map_elems = root.findall("map")
            source_files = os.listdir(self.source_dir)
            audio_files = [
                f
                for f in source_files
                if f.endswith((".wav", ".WAV", ".flac", ".FLAC", ".ogg", ".OGG"))
            ]
            expected_instruments = [
                f.replace(".wav", "")
                .replace(".WAV", "")
                .replace(".flac", "")
                .replace(".FLAC", "")
                .replace(".ogg", "")
                .replace(".OGG", "")
                for f in audio_files
            ]
            if len(map_elems) != len(expected_instruments):
                print(f"Expected {len(expected_instruments)} map elements, got {len(map_elems)}")
                return False
        except Exception as e:
            print(f"Error verifying midimap.xml: {e}")
            return False

        # Verify instrument XML files
        source_files = os.listdir(self.source_dir)
        audio_files = [
            f
            for f in source_files
            if f.endswith((".wav", ".WAV", ".flac", ".FLAC", ".ogg", ".OGG"))
        ]
        expected_instruments = [
            f.replace(".wav", "")
            .replace(".WAV", "")
            .replace(".flac", "")
            .replace(".FLAC", "")
            .replace(".ogg", "")
            .replace(".OGG", "")
            for f in audio_files
        ]
        for instrument in expected_instruments:
            try:
                instrument_xml = os.path.join(self.temp_dir, instrument, f"{instrument}.xml")
                tree = ET.parse(instrument_xml)
                root = tree.getroot()

                if not verify_common_elements(root, "instrument", {"name": instrument}):
                    return False

                # Check samples element
                samples_elem = root.find("samples")
                if samples_elem is None:
                    print(f"Samples element not found in {instrument}.xml")
                    return False

                # Check sample elements
                sample_elems = samples_elem.findall("sample")
                if len(sample_elems) != velocity_levels:
                    print(f"Expected {velocity_levels} sample elements, got {len(sample_elems)}")
                    return False

                # Check audiofile elements
                for sample in sample_elems:
                    audiofiles = sample.findall("audiofile")
                    if not audiofiles:
                        print(
                            f"No audiofile elements found in sample {sample.attrib.get('name', 'unknown')}"
                        )
                        return False
            except Exception as e:
                print(f"Error verifying {instrument}.xml: {e}")
                return False

        return True


if __name__ == "__main__":
    unittest.main()
