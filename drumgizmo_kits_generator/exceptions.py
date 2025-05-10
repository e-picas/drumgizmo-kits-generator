#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SPDX-License-Identifier: MIT
SPDX-PackageName: DrumGizmo kits generator
SPDX-PackageHomePage: https://github.com/e-picas/drumgizmo-kits-generator
SPDX-FileCopyrightText: 2025 Pierre Cassat (Picas)

Custom exceptions for the DrumGizmo kit generator.
"""


class DrumGizmoError(Exception):
    """Base class for all DrumGizmo kit generator exceptions."""


class DirectoryError(DrumGizmoError):
    """Exception raised for directory-related errors."""


class DependencyError(DrumGizmoError):
    """Exception raised when an external dependency is missing."""


class ConfigurationError(DrumGizmoError):
    """Exception raised for configuration errors."""


class AudioProcessingError(DrumGizmoError):
    """Exception raised during audio file processing."""


class ValidationError(DrumGizmoError):
    """Exception raised during data validation."""


class XMLGenerationError(DrumGizmoError):
    """Exception raised during XML file generation."""
