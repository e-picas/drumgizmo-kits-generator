#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SPDX-License-Identifier: MIT
SPDX-PackageName: DrumGizmo kits generator
SPDX-PackageHomePage: https://github.com/e-picas/drumgizmo-kits-generator
SPDX-FileCopyrightText: 2025 Pierre Cassat (Picas)

Custom exceptions for the DrumGizmo kit generator.
"""

from typing import Any, Dict, Optional


class DrumGizmoError(Exception):
    """Base class for all DrumGizmo kit generator exceptions.

    Attributes:
        message: The error message
        context: Additional context information about the error
    """

    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None):
        """Initialize the exception with a message and optional context.

        Args:
            message: The error message
            context: Additional context information about the error
        """
        self.message = message
        self.context = context or {}
        super().__init__(message)

    def __str__(self) -> str:
        """Return a string representation of the exception."""
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            return f"{self.message} [Context: {context_str}]"
        return self.message


class DirectoryError(DrumGizmoError):
    """Exception raised for directory-related errors.

    Examples:
        - Directory not found
        - Permission denied when accessing directory
        - Failed to create or delete directory
    """


class DependencyError(DrumGizmoError):
    """Exception raised when an external dependency is missing.

    Examples:
        - SoX not installed
        - Required command-line tool not found
        - Dependency version incompatible
    """


class ConfigurationError(DrumGizmoError):
    """Exception raised for configuration errors.

    Examples:
        - Configuration file not found
        - Invalid configuration format
        - Missing required configuration parameter
    """


class AudioProcessingError(DrumGizmoError):
    """Exception raised during audio file processing.

    Examples:
        - Failed to read audio file
        - Failed to convert sample rate
        - Failed to create velocity variations
    """


class ValidationError(DrumGizmoError):
    """Exception raised during data validation.

    Examples:
        - Invalid value for configuration parameter
        - Value out of allowed range
        - Inconsistent configuration values
    """


class XMLGenerationError(DrumGizmoError):
    """Exception raised during XML file generation.

    Examples:
        - Failed to create XML structure
        - Failed to write XML file
        - Invalid XML data
    """
