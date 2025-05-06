#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Logger module for DrumGizmo kit generator.
Contains functions to manage the logging: `info`, `debug` (to output only in verbose mode), `warning`.
"""

import sys
import traceback

# ANSI color codes
RED = "\033[91m"
GREEN = "\033[92m"
RESET = "\033[0m"


class Logger:
    """Logger class for DrumGizmo kit generator."""

    def __init__(self):
        """Initialize the logger with verbose mode disabled and raw output disabled."""
        self.verbose_mode = False
        self.raw_output = False

    def set_verbose(self, verbose: bool) -> None:
        """
        Set the verbose mode for logging.

        Args:
            verbose: Boolean indicating whether verbose mode is enabled
        """
        self.verbose_mode = verbose

    def set_raw_output(self, raw_output: bool) -> None:
        """
        Set the raw output mode for logging.

        Args:
            raw_output: If True, disables ANSI color codes in output
        """
        self.raw_output = raw_output

    def info(self, msg: str, end: str = "\n") -> None:
        """
        Print an information message to stdout.

        Args:
            msg: The message to print
            end: The string appended after the message (default: newline)
        """
        if self.raw_output and any(code in msg for code in [RED, GREEN, RESET]):
            # Remove ANSI color codes if raw output is enabled
            msg = msg.replace(RED, "").replace(GREEN, "").replace(RESET, "")
        print(msg, end=end, file=sys.stdout)
        sys.stdout.flush()

    def debug(self, msg: str, end: str = "\n") -> None:
        """
        Print a debug message to stdout only if verbose mode is enabled.

        Args:
            msg: The message to print
            end: The string appended after the message (default: newline)
        """
        if self.verbose_mode:
            print(f"DEBUG: {msg}", end=end, file=sys.stdout)
            sys.stdout.flush()

    def warning(self, msg: str, end: str = "\n") -> None:
        """
        Print a warning message to stderr in red color.

        Args:
            msg: The message to print
            end: The string appended after the message (default: newline)
        """
        if self.raw_output:
            print(f"WARNING: {msg}", end=end, file=sys.stderr)
        else:
            print(f"{RED}WARNING: {msg}{RESET}", end=end, file=sys.stderr)
        sys.stderr.flush()

    def error(self, msg: str) -> None:
        """
        Print an error message to stderr in red color.

        Args:
            msg: The error message to print
        """
        if self.raw_output:
            print(f"ERROR: {msg}", file=sys.stderr)
        else:
            print(f"{RED}ERROR: {msg}{RESET}", file=sys.stderr)
        if self.verbose_mode:
            traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()

    def section(self, title: str) -> None:
        """
        Print a section title with separator lines for better visual organization.

        Args:
            title: The title of the section
        """
        self.info(f"\n=== {title} ===")

    def message(self, msg: str, end: str = "\n") -> None:
        """
        Print a message to stdout in green color.

        Args:
            msg: The message to print
            end: The string appended after the message (default: newline)
        """
        if self.raw_output:
            print(msg, end=end, file=sys.stdout)
        else:
            print(f"{GREEN}{msg}{RESET}", end=end, file=sys.stdout)
        sys.stdout.flush()

    def is_verbose(self) -> bool:
        """
        Check if verbose mode is enabled.

        Returns:
            bool: True if verbose mode is enabled, False otherwise
        """
        return self.verbose_mode


# Create a singleton instance of the Logger
_logger = Logger()

# Export the logger methods as module-level functions
set_verbose = _logger.set_verbose
set_raw_output = _logger.set_raw_output
info = _logger.info
debug = _logger.debug
warning = _logger.warning
error = _logger.error
section = _logger.section
message = _logger.message
is_verbose = _logger.is_verbose
