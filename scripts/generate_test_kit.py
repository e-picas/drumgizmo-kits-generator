#!/usr/bin/env python3
# pylint: disable=broad-exception-caught
# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
# pylint: disable=consider-using-with
# pylint: disable=too-many-function-args
# pylint: disable=subprocess-run-check
"""
Generate a test kit from `examples/sources/` to `tests/target_test/`
and compare its contents with those of `examples/target/`
and the output with `examples/target-generation-output.txt`
"""

import difflib
import filecmp
import os
import re
import shutil
import subprocess
import sys
import tempfile
from typing import Optional

# =============================================================================
# Constants
# =============================================================================

# ANSI color codes for terminal output
COLOR_GREEN = "\033[92m"
COLOR_RED = "\033[91m"
COLOR_GRAY = "\033[90m"
COLOR_RESET = "\033[0m"

# Directory and file paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXAMPLES_DIR = os.path.join(BASE_DIR, "examples", "")
TEMP_DIR = os.path.join(BASE_DIR, "tests", "target_test", "")

# Input paths
SOURCES_DIR = os.path.join(EXAMPLES_DIR, "sources", "")
TARGET_DIR = os.path.join(EXAMPLES_DIR, "target", "")

# Output file names
DRY_RUN_LOG = "output_dry_run.log"
NORMAL_LOG = "output.log"
NORMALIZED_OUTPUT = "normalized_output.log"

# Expected output files
EXPECTED_DRY_RUN_OUTPUT = os.path.join(EXAMPLES_DIR, "target-generation-output-dry-run.txt")
EXPECTED_NORMAL_OUTPUT = os.path.join(EXAMPLES_DIR, "target-generation-output.txt")

# =============================================================================
# Utility Functions
# =============================================================================


def print_green(text: str, suffix: str = "", **kwargs) -> None:
    """Print text in green color with optional suffix in default color.

    Args:
        text: Text to print in green
        suffix: Optional text to append in default color
        **kwargs: Additional arguments to pass to print()
    """
    print(f"{COLOR_GREEN}{text}{COLOR_RESET}{suffix}", **kwargs)


def print_red(text: str, suffix: str = "", **kwargs) -> None:
    """Print text in red color with optional suffix in default color.

    Args:
        text: Text to print in red
        suffix: Optional text to append in default color
        **kwargs: Additional arguments to pass to print()
    """
    print(f"{COLOR_RED}{text}{COLOR_RESET}{suffix}", **kwargs)


def print_gray(text: str, suffix: str = "", **kwargs) -> None:
    """Print text in gray color with optional suffix in default color.

    Args:
        text: Text to print in gray
        suffix: Optional text to append in default color
        **kwargs: Additional arguments to pass to print()
    """
    print(f"{COLOR_GRAY}{text}{COLOR_RESET}{suffix}", **kwargs)


def get_relative_path(path: str, base: str) -> str:
    """Return a relative path string from base to path."""
    try:
        return os.path.relpath(path, base)
    except ValueError:
        return path


def normalize_path_for_display(path: str) -> str:
    """Normalize path for display by removing base directory and normalizing slashes."""
    # Ensure path is a string
    path_str = str(path)

    # Remove base directory from path for cleaner output
    if path_str.startswith(BASE_DIR):
        path_str = path_str[len(BASE_DIR) :]
        if path_str.startswith(os.sep):
            path_str = path_str[1:]

    # Normalize slashes
    path_str = path_str.replace("\\", "/")

    return path_str


def is_binary_file(file_path: str) -> bool:
    """Check if a file is binary by reading the first 8000 bytes."""
    try:
        with open(file_path, "rb") as f:
            chunk = f.read(8000)
            return b"\0" in chunk
    except Exception:
        return False


def show_text_diff(file1: str, file2: str) -> None:
    """Show unified diff between two text files."""
    try:
        with open(file1, "r", encoding="utf-8") as f1, open(file2, "r", encoding="utf-8") as f2:
            diff = difflib.unified_diff(
                f1.readlines(),
                f2.readlines(),
                fromfile=file1,
                tofile=file2,
                n=3,  # Number of context lines
            )
            for line in diff:
                print(line, end="")
    except Exception as e:
        print(f"    Error generating diff: {e}")


def get_sample_rate(file_path: str) -> Optional[int]:
    """Get the sample rate of an audio file using SoX.

    Args:
        file_path: Path to the audio file

    Returns:
        Sample rate in Hz or None if not available
    """
    try:
        # Run SoX to get file info
        result = subprocess.run(
            ["sox", "--info", file_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        # Extract sample rate from output
        match = re.search(r"Sample Rate\s*:\s*(\d+)", result.stdout)
        if match:
            return int(match.group(1))

    except (subprocess.SubprocessError, FileNotFoundError) as e:
        print(f"    Error getting sample rate for {file_path}: {e}")

    return None


def compare_directories(dir1: str, dir2: str) -> None:
    """Compare two directories and print differences.

    Args:
        dir1: First directory to compare
        dir2: Second directory to compare
    """
    dir1 = os.path.abspath(dir1)
    dir2 = os.path.abspath(dir2)
    dirs_cmp = filecmp.dircmp(dir1, dir2)
    mismatch = []
    errors = []
    text_files = []
    audio_files = []

    # Compare files (excluding .log files)
    for name in dirs_cmp.common_files:
        if name.endswith(".log"):
            continue  # Skip .log files

        path1 = os.path.join(dir1, name)
        path2 = os.path.join(dir2, name)
        path_display = normalize_path_for_display(path1)
        try:
            if filecmp.cmp(path1, path2, shallow=False):
                print_green("OK", f" - {path_display}")
            else:
                mismatch.append(name)
                # Check if it's a text file
                if not is_binary_file(path1) and not is_binary_file(path2):
                    text_files.append((name, path1, path2))
                # Check if it's an audio file
                elif name.lower().endswith((".wav", ".flac", ".ogg", ".aif", ".aiff", ".mp3")):
                    audio_files.append((name, path1, path2))
        except (OSError, RuntimeError):
            errors.append(name)

    # Print comparison results with clear OK/KO indicators
    dir1_display = normalize_path_for_display(dir1)
    dir2_display = normalize_path_for_display(dir2)

    # Print OK for matching files (already handled in the first loop)

    # Print KO for files only in one directory
    for name in dirs_cmp.left_only:
        if not name.endswith(".log"):  # Skip .log files
            path = normalize_path_for_display(os.path.join(dir1, name))
            print_red("KO !!", f" - File {path} only in {dir1_display}")
    for name in dirs_cmp.right_only:
        if not name.endswith(".log"):  # Skip .log files
            path = normalize_path_for_display(os.path.join(dir2, name))
            print_red("KO !!", f" - File {path} only in {dir2_display}")

    # Print KO for files that differ
    for name in mismatch:
        path1 = os.path.join(dir1, name)
        path2 = os.path.join(dir2, name)
        path1_display = normalize_path_for_display(path1)
        path2_display = normalize_path_for_display(path2)
        print_red("KO !!", f" - Files {path1_display} and {path2_display} differ")

        # Show diff for text files
        for text_name, text_path1, text_path2 in text_files:
            if text_name == name:
                print("  Differences:")
                show_text_diff(text_path1, text_path2)
                print()  # Add empty line after diff

        # Show sample rate for audio files if they differ
        for audio_name, audio_path1, audio_path2 in audio_files:
            if audio_name == name:
                rate1 = get_sample_rate(audio_path1)
                rate2 = get_sample_rate(audio_path2)
                if rate1 is not None and rate2 is not None:
                    if rate1 != rate2:
                        print(f"  Sample rates differ: {rate1} Hz vs {rate2} Hz")
                break  # No need to check other audio files

    # Print errors
    for name in errors:
        path1 = normalize_path_for_display(os.path.join(dir1, name))
        path2 = normalize_path_for_display(os.path.join(dir2, name))
        print_red("KO !!", f" - Error comparing {path1} and {path2}")

    # Recurse into subdirectories
    for common_dir in dirs_cmp.common_dirs:
        compare_directories(os.path.join(dir1, common_dir), os.path.join(dir2, common_dir))


def normalize_and_compare(actual_file: str, expected_file: str) -> bool:
    """Normalize and compare two files, handling path differences.

    Args:
        actual_file: Path to the actual file
        expected_file: Path to the expected file
        temp_dir: Temporary directory path
        target_dir: Target directory path

    Returns:
        bool: True if files are identical after normalization, False otherwise
    """
    # Normalize the actual file content
    try:
        with open(actual_file, "r", encoding="utf-8") as f:
            actual_content = f.read()
    except UnicodeDecodeError:
        print_red("KO !!", f" - Could not decode {actual_file} as text")
        return False

    # Normalize paths in the content
    normalized_lines = []
    for line in actual_content.splitlines():
        # Split the line into parts that might contain paths
        if ":" in line and any(sep in line for sep in ("/", "\\")):
            prefix, path = line.split(":", 1)
            path = path.strip()
            if path:
                line = f"{prefix}: {normalize_path_for_display(path)}"
        normalized_lines.append(line)

    normalized_content = "\n".join(normalized_lines)

    # Normalize test directory paths to match expected output
    normalized_content = normalized_content.replace(
        os.path.join("tests", "target_test").replace("\\", "/"),
        os.path.join("examples", "target").replace("\\", "/"),
    )

    # Remove any remaining absolute paths
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + os.sep
    normalized_content = normalized_content.replace(base_path, "")

    # Write normalized content to a file in the target directory
    normalized_file = os.path.join(os.path.dirname(actual_file), "normalized_output.log")
    with open(normalized_file, "w", encoding="utf-8") as f:
        f.write(normalized_content)

    # Read and compare with expected content
    try:
        with open(expected_file, "r", encoding="utf-8") as f:
            expected_content = f.read()

        if normalized_content == expected_content:
            print_green("OK", f" - {normalize_path_for_display(actual_file)}")
            return True

        print_red("KO !!", f" - {normalize_path_for_display(actual_file)}")
        print("  Differences:")

        # Compare line by line
        diff = difflib.unified_diff(
            normalized_content.splitlines(keepends=True),
            expected_content.splitlines(keepends=True),
            fromfile=normalize_path_for_display(normalized_file),
            tofile=normalize_path_for_display(expected_file),
        )
        sys.stdout.writelines(diff)
        return False

    except FileNotFoundError:
        print_red(
            "KO !!", f" - Expected file not found: {normalize_path_for_display(expected_file)}"
        )
        return False


def generate_and_compare_dry_run() -> str:
    """Generate test kit in dry-run mode and compare with expected output.

    Returns:
        str: Path to the generated log file
    """
    # Create output directory and log file
    os.makedirs(TEMP_DIR, exist_ok=True)
    output_log = os.path.join(TEMP_DIR, DRY_RUN_LOG)

    print_gray(f"Generating kit in directory: {normalize_path_for_display(TEMP_DIR)}")
    print_gray(f"Output will be saved to: {normalize_path_for_display(output_log)}")
    print_gray(f"Log file will be saved to: {normalize_path_for_display(output_log)}")

    # Store content in memory first
    output_content = []

    # Also create the output file
    with open(output_log, "w", encoding="utf-8") as f:
        pass  # Just create the file

    try:
        # Build the command with --dry-run flag
        cmd = [
            sys.executable,
            os.path.join(BASE_DIR, "create_drumgizmo_kit.py"),
            "-s",
            SOURCES_DIR,
            "-t",
            TEMP_DIR,
            "-r",
            "--dry-run",
        ]

        # Run the command and capture output
        print_green("\nGenerating kit with dry-run mode enabled ...")
        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8"
        )

        # Process output in real-time
        for line in process.stdout:
            # Remove base_dir from the output
            clean_line = line.replace(BASE_DIR + os.sep, "")
            sys.stdout.write(clean_line)
            output_content.append(clean_line)

        process.wait()

        # Write all content to file
        with open(output_log, "w", encoding="utf-8") as f:
            f.writelines(output_content)

        # Compare output with expected dry-run output
        print_green("\nComparing output with expected ...")
        normalize_and_compare(output_log, EXPECTED_DRY_RUN_OUTPUT)

        print_gray(f"\nDry-run log saved to: {normalize_path_for_display(output_log)}")
        return output_log

    except Exception as e:
        print_red(f"Error during dry-run: {e}")
        raise


def generate_and_compare() -> str:
    """Generate test kit and compare with expected output.

    Returns:
        str: Path to the generated log file
    """
    # Create output directory and log file
    os.makedirs(TEMP_DIR, exist_ok=True)
    output_log = os.path.join(TEMP_DIR, NORMAL_LOG)

    # Store content in memory first
    output_content = []

    # Also create the output file
    with open(output_log, "w", encoding="utf-8") as f:
        pass  # Just create the file

    try:
        # Clean up previous run
        if os.path.exists(TEMP_DIR):
            shutil.rmtree(TEMP_DIR)
        os.makedirs(TEMP_DIR, exist_ok=True)

        print_gray(f"Generating kit in directory: {normalize_path_for_display(TEMP_DIR)}")
        print_gray(f"Output will be saved to: {normalize_path_for_display(output_log)}")
        print_gray(f"Log file will be saved to: {normalize_path_for_display(output_log)}")

        # Generate the kit
        cmd = [
            sys.executable,
            os.path.join(BASE_DIR, "create_drumgizmo_kit.py"),
            "-s",
            SOURCES_DIR,
            "-t",
            TEMP_DIR,
            "-r",
        ]

        # Run the command and capture output
        print_green("\nGenerating kit ...")
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

        # Stream output to both console and file
        for line in process.stdout:
            # Remove base_dir from the output
            clean_line = line.replace(BASE_DIR + os.sep, "")
            sys.stdout.write(clean_line)
            output_content.append(clean_line)

        process.wait()

        # Write all content to file
        with open(output_log, "w", encoding="utf-8") as f:
            f.writelines(output_content)

        # Compare directory structure
        print_green("\nComparing directory structure with expected ...")
        print_gray(
            "Audio files are binary contents and may always differ. Samplerate differences will be written."
        )
        compare_directories(TEMP_DIR, TARGET_DIR)

        # Compare output with expected
        print_green("\nComparing output with expected ...")
        normalize_and_compare(output_log, EXPECTED_NORMAL_OUTPUT)

        print_gray(f"\nKit generated in: {normalize_path_for_display(TEMP_DIR)}")
        print_gray(f"Log file saved to: {normalize_path_for_display(output_log)}")

        return output_log

    except Exception as e:
        print_red(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    """Main entry point for the script."""
    dry_run_log = None
    temp_log = None

    try:
        print_green("\n=== Running in dry-run mode ===")
        dry_run_log = generate_and_compare_dry_run()

        # Save dry-run log to a temporary file outside the target directory
        if dry_run_log and os.path.exists(dry_run_log):
            temp_dir = tempfile.gettempdir()
            temp_log = os.path.join(temp_dir, f"drumgizmo_kit_{os.getpid()}.log")
            shutil.copy2(dry_run_log, temp_log)

        print_green("\n=== Running in normal mode ===")
        generate_and_compare()

    except Exception as e:
        print_red(f"Error: {e}")
        sys.exit(1)
    finally:
        # If we have a temporary log file, copy it to the final location
        if temp_log and os.path.exists(temp_log):
            shutil.copy2(temp_log, dry_run_log)
            print_gray(f"Dry-run log saved to: {normalize_path_for_display(dry_run_log)}")

            # Clean up temporary log file if it exists
            if temp_log and os.path.exists(temp_log):
                try:
                    os.unlink(temp_log)
                except Exception as e:
                    print_red(f"Warning: Could not remove temporary log file {temp_log}: {e}")


if __name__ == "__main__":
    main()
