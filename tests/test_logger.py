#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name
# pylint: disable=protected-access
# pylint: disable=unspecified-encoding
"""
SPDX-License-Identifier: MIT
SPDX-PackageName: DrumGizmo kits generator
SPDX-PackageHomePage: https://github.com/e-picas/drumgizmo-kits-generator
SPDX-FileCopyrightText: 2025 Pierre Cassat (Picas)

Tests for the logger module of the DrumGizmo kit generator.
"""

import re
import sys

import pytest

from drumgizmo_kits_generator import logger


@pytest.fixture
def reset_logger():
    """Reset logger state before each test."""
    # Save current state
    original_verbose = logger._logger.verbose_mode
    original_raw_output = logger._logger.raw_output

    # Reset to default state
    logger._logger.verbose_mode = False
    logger._logger.raw_output = False

    # Save original stdout and stderr
    original_stdout = sys.stdout
    original_stderr = sys.stderr

    # Yield to allow test to run
    yield

    # Restore original stdout and stderr
    sys.stdout = original_stdout
    sys.stderr = original_stderr
    # Restore original state
    logger._logger.verbose_mode = original_verbose
    logger._logger.raw_output = original_raw_output


def test_set_verbose():
    """Test setting verbose mode."""
    # Initially verbose should be False
    assert not logger._logger.verbose_mode

    # Set verbose to True
    logger.set_verbose(True)
    assert logger._logger.verbose_mode

    # Set verbose back to False
    logger.set_verbose(False)
    assert not logger._logger.verbose_mode


def test_is_raw_output():
    """Test the is_raw_output function."""
    test_logger = logger.Logger()
    # By défaut, raw_output doit être désactivé
    assert test_logger.is_raw_output() is False
    # Active raw_output
    test_logger.set_raw_output(True)
    assert test_logger.is_raw_output() is True
    # Désactive raw_output
    test_logger.set_raw_output(False)
    assert test_logger.is_raw_output() is False


def test_is_verbose():
    """Test the is_verbose function."""
    # Create a new Logger instance to avoid affecting other tests
    test_logger = logger.Logger()

    # By default, verbose mode should be disabled
    assert test_logger.is_verbose() is False

    # Enable verbose mode
    test_logger.set_verbose(True)
    assert test_logger.is_verbose() is True

    # Disable verbose mode
    test_logger.set_verbose(False)
    assert test_logger.is_verbose() is False


def test_is_raw_output_module_function():
    """Test the is_raw_output function at the module level."""
    # Sauvegarde l'état courant
    original_state = logger.is_raw_output()
    try:
        logger.set_raw_output(False)
        assert logger.is_raw_output() is False
        logger.set_raw_output(True)
        assert logger.is_raw_output() is True
    finally:
        logger.set_raw_output(original_state)


def test_is_verbose_module_function():
    """Test the is_verbose function at the module level."""
    # Save the current state
    original_state = logger.is_verbose()

    try:
        # Set verbose mode to False
        logger.set_verbose(False)
        assert logger.is_verbose() is False

        # Set verbose mode to True
        logger.set_verbose(True)
        assert logger.is_verbose() is True
    finally:
        # Restore the original state
        logger.set_verbose(original_state)


def test_set_raw_output():
    """Test setting raw output mode."""
    # Initially raw_output should be False
    assert not logger._logger.raw_output

    # Set raw_output to True
    logger.set_raw_output(True)
    assert logger._logger.raw_output

    # Set raw_output back to False
    logger.set_raw_output(False)
    assert not logger._logger.raw_output


def test_info(capsys):
    """Test info function."""
    # Test with default end parameter
    logger.info("Test info message")
    captured = capsys.readouterr()
    assert captured.out == "Test info message\n"

    # Test with custom end parameter
    logger.info("Test info message", end="")
    captured = capsys.readouterr()
    assert captured.out == "Test info message"


def test_debug_verbose_disabled(capsys):
    """Test debug function when verbose mode is disabled."""
    # Ensure verbose is disabled
    logger.set_verbose(False)

    # Call debug function
    logger.debug("Test debug message")

    # No output should be produced
    captured = capsys.readouterr()
    assert captured.out == ""


def test_debug_verbose_enabled(capsys):
    """Test debug function when verbose mode is enabled."""
    # Enable verbose mode
    logger.set_verbose(True)

    # Call debug function
    logger.debug("Test debug message")

    # Output should include DEBUG prefix
    captured = capsys.readouterr()
    assert captured.out == "DEBUG: Test debug message\n"

    # Test with custom end parameter
    logger.debug("Test debug message", end="")
    captured = capsys.readouterr()
    assert captured.out == "DEBUG: Test debug message"


def test_warning(capsys):
    """Test warning function."""
    # Call warning function
    logger.warning("Test warning message")

    # Output should include WARNING prefix with ANSI color codes
    captured = capsys.readouterr()
    assert "WARNING: Test warning message" in captured.err

    # Test with custom end parameter
    logger.warning("Test warning message", end="")
    captured = capsys.readouterr()
    assert "WARNING: Test warning message" in captured.err


def test_error(capsys):
    """Test error function."""
    # Call error function
    logger.error("Test error message")

    # Output should include ERROR prefix with ANSI color codes
    captured = capsys.readouterr()
    assert "ERROR - Test error message" in captured.err


def test_message(capsys):
    """Test message function."""
    # Call message function
    logger.message("Test message")

    # Output should include the message with ANSI color codes
    captured = capsys.readouterr()
    assert "Test message" in captured.out

    # Test with custom end parameter
    logger.message("Test message", end="")
    captured = capsys.readouterr()
    assert "Test message" in captured.out


def test_section(capsys):
    """Test section function."""
    # Call section function
    title = "Test Section"
    logger.section(title)

    # Expected output with simplified format
    expected_output = "\n=== Test Section ===\n"

    # Verify output
    captured = capsys.readouterr()
    assert captured.out == expected_output


def test_raw_output_info(capsys):
    """Test info function with raw output enabled."""
    # Enable raw output
    logger.set_raw_output(True)

    # Test with a message that contains color codes
    test_msg = f"{logger.RED}Test message{logger.RESET}"
    logger.info(test_msg)
    captured = capsys.readouterr()
    assert captured.out == "Test message\n"

    # Disable raw output for other tests
    logger.set_raw_output(False)


def test_raw_output_warning(capsys):
    """Test warning function with raw output enabled."""
    # Enable raw output
    logger.set_raw_output(True)

    logger.warning("Test warning")
    captured = capsys.readouterr()
    assert captured.err == "WARNING: Test warning\n"

    # Disable raw output for other tests
    logger.set_raw_output(False)


def test_raw_output_error(capsys):
    """Test error function with raw output enabled."""
    # Enable raw output
    logger.set_raw_output(True)

    logger.error("Test error")
    captured = capsys.readouterr()
    # Vérifie que le message d'erreur commence par "ERROR: Test error"
    assert captured.err.startswith("ERROR - Test error\n")

    # Disable raw output for other tests
    logger.set_raw_output(False)


def test_raw_output_message(capsys):
    """Test message function with raw output enabled."""
    # Enable raw output
    logger.set_raw_output(True)

    logger.message("Test message")
    captured = capsys.readouterr()
    assert captured.out == "Test message\n"

    # Disable raw output for other tests
    logger.set_raw_output(False)


def test_raw_output_section(capsys):
    """Test section function with raw output enabled."""
    # Enable raw output
    logger.set_raw_output(True)

    logger.section("Test Section")
    captured = capsys.readouterr()
    assert captured.out == "\n=== Test Section ===\n"

    # Disable raw output for other tests
    logger.set_raw_output(False)


def test_print_action_start(capsys):
    """Test print_action_start outputs the correct message with ellipsis."""
    logger.print_action_start("Traitement")
    captured = capsys.readouterr()
    assert captured.out == "Traitement...\n"


def test_print_action_end_default(capsys):
    """Test print_action_end outputs OK by default."""
    logger.print_action_end()
    captured = capsys.readouterr()
    assert captured.out == "OK\n"


def test_print_action_end_custom(capsys):
    """Test print_action_end outputs a custom message."""
    logger.print_action_end("Terminé")
    captured = capsys.readouterr()
    assert captured.out == "Terminé\n"


def test_logging_with_logging_module(tmp_path):
    """Test that logging messages are written to file using the logging module."""
    log_file = tmp_path / "test_log.log"
    logger.set_log_file(str(log_file))

    # Test different log levels
    logger.log("INFO", "Test info message")
    logger.log("DEBUG", "Test debug message")
    logger.log("WARNING", "Test warning message")
    logger.log("ERROR", "Test error message")

    # Check that the log file exists and contains the messages
    assert log_file.exists()

    with open(log_file, "r") as f:
        content = f.read()

    # Verify the content of the log file
    assert "INFO - Test info message" in content
    assert "DEBUG - Test debug message" in content
    assert "WARNING - Test warning message" in content
    assert "ERROR - Test error message" in content


def test_logging_with_raw_output(tmp_path):
    """Test logging with raw output enabled."""
    log_file = tmp_path / "test_log_raw.log"
    logger.set_log_file(str(log_file))
    logger.set_raw_output(True)

    logger.log("INFO", "Test info message with raw output")
    logger.log("WARNING", "Test warning message with raw output")
    logger.log("ERROR", "Test error message with raw output")

    assert log_file.exists()

    with open(log_file, "r") as f:
        content = f.read()

    # Verify the content of the log file
    assert "INFO - Test info message with raw output" in content
    assert "WARNING - Test warning message with raw output" in content
    assert "ERROR - Test error message with raw output" in content
    # Verify no ANSI color codes in raw output
    assert "\033" not in content


def test_logging_change_log_file(tmp_path):
    """Test changing the log file."""
    # Create first log file
    log_file1 = tmp_path / "test_log1.log"
    logger.set_log_file(str(log_file1))
    logger.log("INFO", "Message in first log file")

    # Create second log file
    log_file2 = tmp_path / "test_log2.log"
    logger.set_log_file(str(log_file2))
    logger.log("INFO", "Message in second log file")

    # Verify first log file
    assert log_file1.exists()
    with open(log_file1, "r") as f:
        content = f.read()
        assert "Message in first log file" in content
        assert "Message in second log file" not in content

    # Verify second log file
    assert log_file2.exists()
    with open(log_file2, "r") as f:
        content = f.read()
        assert "Message in second log file" in content
        assert "Message in first log file" not in content


def test_logging_format(tmp_path):
    """Test the format of log messages."""
    log_file = tmp_path / "test_log_format.log"
    logger.set_log_file(str(log_file))

    # Log a message and check its format
    logger.log("INFO", "Test format message")

    assert log_file.exists()
    with open(log_file, "r") as f:
        line = f.readline()
        # Verify the format: timestamp - level - message
        assert re.match(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} - INFO - Test format message", line)


def test_logging_error_with_exception(tmp_path):
    """Test logging an error with an exception."""
    log_file = tmp_path / "test_log_error.log"
    logger.set_log_file(str(log_file))

    try:
        raise ValueError("Test error")
    except ValueError as e:
        logger.log("ERROR", "An error occurred", exc=e)

    assert log_file.exists()
    with open(log_file, "r") as f:
        content = f.read()
        assert "ERROR - An error occurred" in content
        assert "ValueError: Test error" in content


def test_info_with_write_log(tmp_path):
    """Test info function with write_log parameter."""
    log_file = tmp_path / "test_log_info.log"
    logger.set_log_file(str(log_file))

    # Test with write_log=True (default)
    logger.info("Message with write_log=True")

    # Test with write_log=False
    logger.info("Message with write_log=False", write_log=False)

    assert log_file.exists()
    with open(log_file, "r") as f:
        content = f.read()
        assert "Message with write_log=True" in content
        assert "Message with write_log=False" not in content


def test_debug_with_write_log(tmp_path):
    """Test debug function with write_log parameter."""
    log_file = tmp_path / "test_log_debug.log"
    logger.set_log_file(str(log_file))
    logger.set_verbose(True)  # Enable verbose mode for debug messages

    # Test with write_log=True (default)
    logger.debug("Debug message with write_log=True")

    # Test with write_log=False
    logger.debug("Debug message with write_log=False", write_log=False)

    assert log_file.exists()
    with open(log_file, "r") as f:
        content = f.read()
        assert "Debug message with write_log=True" in content
        assert "Debug message with write_log=False" not in content


def test_warning_with_write_log(tmp_path):
    """Test warning function with write_log parameter."""
    log_file = tmp_path / "test_log_warning.log"
    logger.set_log_file(str(log_file))

    # Test with write_log=True (default)
    logger.warning("Warning message with write_log=True")

    # Test with write_log=False
    logger.warning("Warning message with write_log=False", write_log=False)

    assert log_file.exists()
    with open(log_file, "r") as f:
        content = f.read()
        assert "Warning message with write_log=True" in content
        assert "Warning message with write_log=False" not in content


def test_error_with_write_log(tmp_path):
    """Test error function with write_log parameter."""
    log_file = tmp_path / "test_log_error.log"
    logger.set_log_file(str(log_file))

    # Test with write_log=True (default)
    logger.error("Error message with write_log=True")

    # Test with write_log=False
    logger.error("Error message with write_log=False", write_log=False)

    assert log_file.exists()
    with open(log_file, "r") as f:
        content = f.read()
        assert "Error message with write_log=True" in content
        assert "Error message with write_log=False" not in content
