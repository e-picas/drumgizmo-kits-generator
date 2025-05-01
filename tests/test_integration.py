#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=broad-exception-caught
# pylint: disable=import-outside-toplevel,wrong-import-position
# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
"""
Integration test for the DrumGizmo kit generator.

This module contains tests that verify the complete processing pipeline
by comparing the generated output with the expected reference output.
"""

import difflib
import os
import re
import shutil
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET


class TestDrumGizmoKitIntegration(unittest.TestCase):
    """Integration tests for the DrumGizmo kit generator."""

    def setUp(self):
        """Initialize before each test by creating test directories."""
        self.source_dir = os.path.join(os.path.dirname(__file__), "sources")
        # Use the sources directory directly as the audio samples directory
        self.audio_samples_dir = self.source_dir
        self.reference_dir = os.path.join(os.path.dirname(__file__), "target")
        self.temp_dir = tempfile.mkdtemp()
        self.config_file = os.path.join(self.source_dir, "drumgizmo-kit.ini")

    def tearDown(self):
        """Clean up after each test by removing temporary directories."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def compare_xml_files(self, file1, file2):
        """Compare two XML files ignoring dates and versions."""
        try:
            with open(file1, "r", encoding="utf-8") as f1, open(file2, "r", encoding="utf-8") as f2:
                content1 = f1.read()
                content2 = f2.read()

                # Replace dates and versions with constant values
                # to allow comparison
                date_pattern = r"Generated on \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"
                content1 = re.sub(date_pattern, "Generated on DATE", content1)
                content2 = re.sub(date_pattern, "Generated on DATE", content2)

                date_pattern2 = (
                    r"Generated with create_drumgizmo_kit.py at \d{4}-\d{2}-\d{2} \d{2}:\d{2}"
                )
                content1 = re.sub(
                    date_pattern2, "Generated with create_drumgizmo_kit.py at DATE", content1
                )
                content2 = re.sub(
                    date_pattern2, "Generated with create_drumgizmo_kit.py at DATE", content2
                )

                # Parse XML files for detailed comparison
                try:
                    root1 = ET.fromstring(content1)
                    root2 = ET.fromstring(content2)

                    # Compare metadata elements
                    metadata1 = root1.find(".//metadata")
                    metadata2 = root2.find(".//metadata")

                    if metadata1 is not None and metadata2 is not None:
                        print(
                            f"\nComparing metadata in {os.path.basename(file1)} and {os.path.basename(file2)}:"
                        )

                        for child1 in metadata1:
                            tag = child1.tag
                            child2 = metadata2.find(f"./{tag}")

                            if child2 is not None:
                                if child1.text != child2.text and tag not in ["notes", "created"]:
                                    print(
                                        f"  Difference in {tag}: '{child1.text}' vs '{child2.text}'"
                                    )

                    # Compare channels
                    channels1 = [ch.attrib["name"] for ch in root1.findall(".//channels/channel")]
                    channels2 = [ch.attrib["name"] for ch in root2.findall(".//channels/channel")]

                    print(f"\nChannels in {os.path.basename(file1)}: {channels1}")
                    print(f"Channels in {os.path.basename(file2)}: {channels2}")

                    if len(channels1) != len(channels2):
                        print(f"Different number of channels: {len(channels1)} vs {len(channels2)}")

                    # Find channels that are in one file but not in the other
                    only_in_file1 = [ch for ch in channels1 if ch not in channels2]
                    if only_in_file1:
                        print(f"Channels only in {os.path.basename(file1)}: {only_in_file1}")

                    only_in_file2 = [ch for ch in channels2 if ch not in channels1]
                    if only_in_file2:
                        print(f"Channels only in {os.path.basename(file2)}: {only_in_file2}")

                    # Compare instruments
                    instruments1 = [
                        (instr.attrib["name"], instr.attrib["file"])
                        for instr in root1.findall(".//instruments/instrument")
                    ]
                    instruments2 = [
                        (instr.attrib["name"], instr.attrib["file"])
                        for instr in root2.findall(".//instruments/instrument")
                    ]

                    print(f"\nInstruments in {os.path.basename(file1)}:")
                    for name, file in instruments1:
                        print(f"  {name}: {file}")

                    print(f"\nInstruments in {os.path.basename(file2)}:")
                    for name, file in instruments2:
                        print(f"  {name}: {file}")

                    if len(instruments1) != len(instruments2):
                        print(
                            f"Different number of instruments: {len(instruments1)} vs {len(instruments2)}"
                        )

                except ET.ParseError as e:
                    print(f"Error parsing XML: {e}")

                # Compare contents
                if content1 != content2:
                    diff = difflib.unified_diff(
                        content1.splitlines(),
                        content2.splitlines(),
                        fromfile=file1,
                        tofile=file2,
                        lineterm="",
                    )
                    print("\nDifferences in XML files:")
                    for line in diff:
                        print(line)
                    return False
                return True
        except Exception as e:
            print(f"Error comparing XML files: {e}")
            return False

    def compare_directories(self, dir1, dir2):
        """Compare two directories to ensure they contain the same files."""
        files1 = set()
        for root, _, files in os.walk(dir1):
            for file in files:
                rel_path = os.path.relpath(os.path.join(root, file), dir1)
                files1.add(rel_path)

        files2 = set()
        for root, _, files in os.walk(dir2):
            for file in files:
                rel_path = os.path.relpath(os.path.join(root, file), dir2)
                files2.add(rel_path)

        # Check if the file sets are identical
        if files1 != files2:
            print("\nDifferences in files:")
            print(f"Files only in {dir1}: {files1 - files2}")
            print(f"Files only in {dir2}: {files2 - files1}")
            return False

        # Compare the contents of XML files
        for file in files1:
            if file.endswith(".xml"):
                file1_path = os.path.join(dir1, file)
                file2_path = os.path.join(dir2, file)
                if not self.compare_xml_files(file1_path, file2_path):
                    return False

        return True

    def test_full_integration(self):
        """Test the full integration of the DrumGizmo kit generator."""
        # Run the application with the specified parameters
        script_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "create_drumgizmo_kit.py")
        )

        command = [
            "python3",
            script_path,
            "-s",
            self.audio_samples_dir,
            "-t",
            self.temp_dir,
            "-c",
            self.config_file,
        ]

        try:
            result = subprocess.run(
                command,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            print(f"Application output:\n{result.stdout}")
            if result.stderr:
                print(f"Application errors:\n{result.stderr}")
        except subprocess.CalledProcessError as e:
            self.fail(f"Application execution failed with code {e.returncode}:\n{e.stderr}")

        # Compare directories
        self.assertTrue(
            self.compare_directories(self.temp_dir, self.reference_dir),
            "Generated directories do not match reference directories",
        )

    def test_command_output_matches_reference(self):
        """
        Test that the command output matches the reference output file.

        This test executes the command:
        python create_drumgizmo_kit.py -s tests/sources/ -t tests/target_test/ -c tests/sources/drumgizmo-kit.ini
        and compares its output with the content of tests/mocks/generate-target-test-output.txt
        """
        # Get paths
        script_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "create_drumgizmo_kit.py")
        )
        target_dir = os.path.join(os.path.dirname(__file__), "target_test")
        source_dir = os.path.join(os.path.dirname(__file__), "sources")
        config_file = os.path.join(source_dir, "drumgizmo-kit.ini")
        reference_output_file = os.path.join(
            os.path.dirname(__file__), "mocks", "generate-target-test-output.txt"
        )

        # Create target directory if it doesn't exist
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        else:
            # Clean the target directory
            for item in os.listdir(target_dir):
                item_path = os.path.join(target_dir, item)
                if os.path.isfile(item_path):
                    os.unlink(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)

        # Run the command
        command = [
            "python3",
            script_path,
            "-s",
            source_dir,
            "-t",
            target_dir,
            "-c",
            config_file,
        ]

        try:
            result = subprocess.run(
                command,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            # Combine stdout and stderr as the reference file contains both
            command_output = result.stderr
            if result.stdout:
                command_output += result.stdout

            # Read the reference output
            with open(reference_output_file, "r", encoding="utf-8") as f:
                reference_output = f.read()

            # Normalize paths in command output
            # Replace absolute paths with relative paths
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

            # Normalize paths in command output
            command_output = command_output.replace(base_dir + "/", "")

            # Normaliser les fins de chemins (ajouter des slashes finaux pour correspondre au fichier de référence)
            command_output = re.sub(r"tests/sources(?![\w/])", r"tests/sources/", command_output)
            command_output = re.sub(
                r"tests/target_test(?![\w/])", r"tests/target_test/", command_output
            )
            command_output = re.sub(
                r"Copying extra files to tests/target_test:",
                r"Copying extra files to tests/target_test/:",
                command_output,
            )
            command_output = re.sub(
                r"DrumGizmo kit successfully created in: tests/target_test(?![\w/])",
                r"DrumGizmo kit successfully created in: tests/target_test/",
                command_output,
            )

            # Replace date/time patterns in both outputs
            date_pattern = (
                r"Generated with create_drumgizmo_kit\.py at \d{4}-\d{2}-\d{2} \d{2}:\d{2}"
            )
            command_output = re.sub(
                date_pattern, "Generated with create_drumgizmo_kit.py at DATE_TIME", command_output
            )
            reference_output = re.sub(
                date_pattern,
                "Generated with create_drumgizmo_kit.py at DATE_TIME",
                reference_output,
            )

            # Compare the outputs
            if command_output != reference_output:
                # Create a diff for better visualization
                diff = difflib.unified_diff(
                    reference_output.splitlines(),
                    command_output.splitlines(),
                    fromfile="reference_output",
                    tofile="command_output",
                    lineterm="",
                )

                # Print the diff
                diff_text = "\n".join(diff)
                self.fail(f"Command output does not match reference output:\n{diff_text}")

        except subprocess.CalledProcessError as e:
            self.fail(f"Command execution failed with code {e.returncode}:\n{e.stderr}")
        finally:
            # Clean up the target directory
            if os.path.exists(target_dir):
                shutil.rmtree(target_dir)


if __name__ == "__main__":
    unittest.main()
