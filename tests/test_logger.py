#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name
# pylint: disable=protected-access
"""
Tests for the logger module of the DrumGizmo kit generator.
"""

import sys

import pytest

from drumgizmo_kits_generator import logger


@pytest.fixture
def reset_logger():
    """Reset logger state before each test."""
    # Reset verbose mode
    original_verbose = logger._logger.verbose_mode
    logger._logger.verbose_mode = False

    # Save original stdout and stderr
    original_stdout = sys.stdout
    original_stderr = sys.stderr

    # Yield to allow test to run
    yield

    # Restore original stdout and stderr
    sys.stdout = original_stdout
    sys.stderr = original_stderr
    # Restore original verbose mode
    logger._logger.verbose_mode = original_verbose


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
    assert "ERROR: Test error message" in captured.err


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
