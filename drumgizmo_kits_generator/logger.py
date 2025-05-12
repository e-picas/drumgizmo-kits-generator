#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SPDX-License-Identifier: MIT
SPDX-PackageName: DrumGizmo kits generator
SPDX-PackageHomePage: https://github.com/e-picas/drumgizmo-kits-generator
SPDX-FileCopyrightText: 2025 Pierre Cassat (Picas)

Logger module for DrumGizmo kit generator.
Contains functions to manage the logging: `info`, `debug` (to output only in verbose mode), `warning`.
"""

import logging
import sys
import traceback
from typing import Optional

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
        self.log_file = "drumgizmo_kit_generator.log"
        self._setup_logging()

    def _setup_logging(self) -> None:
        """Configure the Python logging system."""
        # Create logger
        self.logger = logging.getLogger("drumgizmo_kit_generator")
        self.logger.setLevel(logging.DEBUG)

        # Create formatter
        self.formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )

        # Create file handler
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(self.formatter)

        # Add handlers to logger
        self.logger.addHandler(file_handler)

    def log(self, level: str, msg: str, exc: Optional[Exception] = None) -> None:
        """
        Write a message to the log file using the logging module.

        Args:
            level (str): Log level (INFO, DEBUG, WARNING, ERROR)
            msg (str): Message to log
            exc (Optional[Exception]): Exception to log with the message
        """
        if exc:
            self.logger.log(getattr(logging, level), msg, exc_info=exc)
        else:
            self.logger.log(getattr(logging, level), msg)

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

    def set_log_file(self, log_file: str) -> None:
        """
        Set a new log file for the logger.

        Args:
            log_file (str): Path to the new log file
        """
        self.log_file = log_file
        # Remove existing handlers
        for handler in self.logger.handlers[:]:
            handler.close()
            self.logger.removeHandler(handler)

        # Add new handlers
        if self.log_file:
            file_handler = logging.FileHandler(self.log_file)
            file_handler.setFormatter(self.formatter)
            self.logger.addHandler(file_handler)

        # Always keep console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(self.formatter)
        self.logger.addHandler(console_handler)

    def info(self, msg: str, write_log: bool = True, end: str = "\n") -> None:
        """
        Print an information message to stdout.

        Args:
            msg: The message to print
            end: The string appended after the message (default: newline)
            write_log: If True, write the message to the log file (default: True)
        """
        if write_log:
            self.log("INFO", msg)
        if self.raw_output and any(code in msg for code in [RED, GREEN, RESET]):
            # Remove ANSI color codes if raw output is enabled
            msg = msg.replace(RED, "").replace(GREEN, "").replace(RESET, "")
        print(msg, end=end, file=sys.stdout)
        sys.stdout.flush()

    def debug(self, msg: str, write_log: bool = True, end: str = "\n") -> None:
        """
        Print a debug message to stdout only if verbose mode is enabled.

        Args:
            msg: The message to print
            end: The string appended after the message (default: newline)
            write_log: If True, write the message to the log file (default: True)
        """
        if write_log:
            self.log("DEBUG", msg)
        if self.verbose_mode:
            print(f"DEBUG: {msg}", end=end, file=sys.stdout)
            sys.stdout.flush()

    def warning(self, msg: str, write_log: bool = True, end: str = "\n") -> None:
        """
        Print a warning message to stderr in red color.

        Args:
            msg: The message to print
            end: The string appended after the message (default: newline)
            write_log: If True, write the message to the log file (default: True)
        """
        if write_log:
            self.log("WARNING", msg)
        if self.raw_output:
            print(f"WARNING: {msg}", end=end, file=sys.stderr)
        else:
            print(f"{RED}WARNING: {msg}{RESET}", end=end, file=sys.stderr)
        sys.stderr.flush()

    def error(self, msg: str, exc: Optional[Exception] = None, write_log: bool = True) -> None:
        """
        Print an error message to stderr in red color. Optionally print exception traceback.

        Args:
            msg: The error message to print
            exc: The exception object to print (optional)
            write_log: If True, write the message to the log file (default: True)
        """
        if write_log:
            self.log("ERROR", msg, exc)
        if exc is not None:
            error_type = type(exc).__name__ + ": "
        else:
            error_type = ""

        if self.raw_output:
            print(f"ERROR - {error_type}{msg}", file=sys.stderr)
        else:
            print(f"{RED}ERROR - {error_type}{msg}{RESET}", file=sys.stderr)

        if exc is not None and self.verbose_mode:
            traceback.print_exc(file=sys.stderr)

        sys.stderr.flush()

    def section(self, title: str) -> None:
        """
        Print a section title with separator lines for better visual organization.

        Args:
            title: The title of the section
        """
        self.info(f"\n=== {title} ===", write_log=False)

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

    def is_raw_output(self) -> bool:
        """
        Check if raw output mode is enabled.

        Returns:
            bool: True if raw output mode is enabled, False otherwise
        """
        return self.raw_output

    def print_action_start(self, msg: str) -> None:
        """
        Print the start of an action with ellipsis.

        Args:
            msg: The message to display (e.g., "Generating XML")
        """
        self.log("INFO", f"{msg}...")
        print(f"{msg}...", flush=True)

    def print_action_end(self, msg: str = "OK") -> None:
        """
        Print the end of an action (default: OK).

        Args:
            msg: The message to display (default: "OK")
        """
        print(msg, flush=True)


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
is_raw_output = _logger.is_raw_output
print_action_start = _logger.print_action_start
print_action_end = _logger.print_action_end
log = _logger.log
set_log_file = _logger.set_log_file
