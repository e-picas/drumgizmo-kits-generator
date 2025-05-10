#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SPDX-License-Identifier: MIT
SPDX-PackageName: DrumGizmo kits generator
SPDX-PackageHomePage: https://github.com/e-picas/drumgizmo-kits-generator
SPDX-FileCopyrightText: 2025 Pierre Cassat (Picas)

Test script to verify the exception system of the DrumGizmo kit generator.
"""

from drumgizmo_kits_generator.exceptions import (
    AudioProcessingError,
    ConfigurationError,
    DependencyError,
    DirectoryError,
    DrumGizmoError,
    ValidationError,
    XMLGenerationError,
)


def test_drumgizmo_error_hierarchy():
    """Test the DrumGizmo exception hierarchy."""
    # Verify that all exceptions inherit from DrumGizmoError
    assert issubclass(DirectoryError, DrumGizmoError)
    assert issubclass(DependencyError, DrumGizmoError)
    assert issubclass(ConfigurationError, DrumGizmoError)
    assert issubclass(AudioProcessingError, DrumGizmoError)
    assert issubclass(ValidationError, DrumGizmoError)
    assert issubclass(XMLGenerationError, DrumGizmoError)

    # Verify that DrumGizmoError inherits from Exception
    assert issubclass(DrumGizmoError, Exception)


def test_directory_error():
    """Test the DirectoryError exception."""
    # Create a DirectoryError instance
    error = DirectoryError("Test DirectoryError")

    # Verify that it's an instance of DirectoryError and DrumGizmoError
    assert isinstance(error, DirectoryError)
    assert isinstance(error, DrumGizmoError)

    # Verify the error message
    assert str(error) == "Test DirectoryError"


def test_dependency_error():
    """Test the DependencyError exception."""
    # Create a DependencyError instance
    error = DependencyError("Test DependencyError")

    # Verify that it's an instance of DependencyError and DrumGizmoError
    assert isinstance(error, DependencyError)
    assert isinstance(error, DrumGizmoError)

    # Verify the error message
    assert str(error) == "Test DependencyError"


def test_audio_processing_error():
    """Test the AudioProcessingError exception."""
    # Create an AudioProcessingError instance
    error = AudioProcessingError("Test AudioProcessingError")

    # Verify that it's an instance of AudioProcessingError and DrumGizmoError
    assert isinstance(error, AudioProcessingError)
    assert isinstance(error, DrumGizmoError)

    # Verify the error message
    assert str(error) == "Test AudioProcessingError"


def test_validation_error():
    """Test the ValidationError exception."""
    # Create a ValidationError instance
    error = ValidationError("Test ValidationError")

    # Verify that it's an instance of ValidationError and DrumGizmoError
    assert isinstance(error, ValidationError)
    assert isinstance(error, DrumGizmoError)

    # Verify the error message
    assert str(error) == "Test ValidationError"


def test_configuration_error():
    """Test the ConfigurationError exception."""
    # Create a ConfigurationError instance
    error = ConfigurationError("Test ConfigurationError")

    # Verify that it's an instance of ConfigurationError and DrumGizmoError
    assert isinstance(error, ConfigurationError)
    assert isinstance(error, DrumGizmoError)

    # Verify the error message
    assert str(error) == "Test ConfigurationError"


def test_xml_generation_error():
    """Test the XMLGenerationError exception."""
    # Create an XMLGenerationError instance
    error = XMLGenerationError("Test XMLGenerationError")

    # Verify that it's an instance of XMLGenerationError and DrumGizmoError
    assert isinstance(error, XMLGenerationError)
    assert isinstance(error, DrumGizmoError)

    # Verify the error message
    assert str(error) == "Test XMLGenerationError"
