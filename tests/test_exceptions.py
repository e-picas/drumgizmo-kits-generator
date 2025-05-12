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


def test_drumgizmo_error_base_class():
    """Test the base DrumGizmoError class with context functionality."""
    # Test without context
    error = DrumGizmoError("Base error message")
    assert error.message == "Base error message"
    assert error.context == {}
    assert str(error) == "Base error message"

    # Test with simple context
    error_with_context = DrumGizmoError(
        "Error with context", context={"key1": "value1", "key2": 42}
    )
    assert error_with_context.message == "Error with context"
    assert error_with_context.context == {"key1": "value1", "key2": 42}
    assert str(error_with_context) == "Error with context [Context: key1=value1, key2=42]"

    # Test with nested context
    nested_context = {"outer": "value", "nested": {"inner1": 1, "inner2": "two"}, "list": [1, 2, 3]}
    error_nested = DrumGizmoError("Error with nested context", context=nested_context)
    assert error_nested.message == "Error with nested context"
    assert error_nested.context == nested_context
    assert "Error with nested context [Context:" in str(error_nested)
    assert "outer=value" in str(error_nested)

    # Test with None context (should default to empty dict)
    error_none_context = DrumGizmoError("Error with None context", context=None)
    assert error_none_context.message == "Error with None context"
    assert error_none_context.context == {}
    assert str(error_none_context) == "Error with None context"


def test_directory_error():
    """Test the DirectoryError exception."""
    # Create a DirectoryError instance
    error = DirectoryError("Test DirectoryError")

    # Verify that it's an instance of DirectoryError and DrumGizmoError
    assert isinstance(error, DirectoryError)
    assert isinstance(error, DrumGizmoError)

    # Verify the error message
    assert str(error) == "Test DirectoryError"

    # Test with context
    error_with_context = DirectoryError(
        "Directory error with context", context={"path": "/tmp/test", "operation": "create"}
    )
    assert isinstance(error_with_context, DirectoryError)
    assert error_with_context.message == "Directory error with context"
    assert error_with_context.context == {"path": "/tmp/test", "operation": "create"}
    assert (
        str(error_with_context)
        == "Directory error with context [Context: path=/tmp/test, operation=create]"
    )


def test_dependency_error():
    """Test the DependencyError exception."""
    # Create a DependencyError instance
    error = DependencyError("Test DependencyError")

    # Verify that it's an instance of DependencyError and DrumGizmoError
    assert isinstance(error, DependencyError)
    assert isinstance(error, DrumGizmoError)

    # Verify the error message
    assert str(error) == "Test DependencyError"

    # Test with context
    error_with_context = DependencyError(
        "Missing dependency", context={"dependency": "sox", "required_version": "14.4.2"}
    )
    assert isinstance(error_with_context, DependencyError)
    assert error_with_context.message == "Missing dependency"
    assert error_with_context.context == {"dependency": "sox", "required_version": "14.4.2"}
    assert (
        str(error_with_context)
        == "Missing dependency [Context: dependency=sox, required_version=14.4.2]"
    )


def test_audio_processing_error():
    """Test the AudioProcessingError exception."""
    # Create an AudioProcessingError instance
    error = AudioProcessingError("Test AudioProcessingError")

    # Verify that it's an instance of AudioProcessingError and DrumGizmoError
    assert isinstance(error, AudioProcessingError)
    assert isinstance(error, DrumGizmoError)

    # Verify the error message
    assert str(error) == "Test AudioProcessingError"

    # Test with context
    error_with_context = AudioProcessingError(
        "Failed to convert sample rate",
        context={
            "file": "kick.wav",
            "source_rate": "48000",
            "target_rate": "44100",
            "error": "SoX processing failed",
        },
    )
    assert isinstance(error_with_context, AudioProcessingError)
    assert error_with_context.message == "Failed to convert sample rate"
    assert error_with_context.context == {
        "file": "kick.wav",
        "source_rate": "48000",
        "target_rate": "44100",
        "error": "SoX processing failed",
    }
    assert "Failed to convert sample rate [Context:" in str(error_with_context)
    assert "file=kick.wav" in str(error_with_context)
    assert "source_rate=48000" in str(error_with_context)
    assert "target_rate=44100" in str(error_with_context)
    assert "error=SoX processing failed" in str(error_with_context)


def test_validation_error():
    """Test the ValidationError exception."""
    # Create a ValidationError instance
    error = ValidationError("Test ValidationError")

    # Verify that it's an instance of ValidationError and DrumGizmoError
    assert isinstance(error, ValidationError)
    assert isinstance(error, DrumGizmoError)

    # Verify the error message
    assert str(error) == "Test ValidationError"

    # Test with context
    error_with_context = ValidationError(
        "Invalid configuration value",
        context={
            "parameter": "midi_note_min",
            "value": 130,
            "allowed_range": "0-127",
            "rule": "Must be <= 127",
        },
    )
    assert isinstance(error_with_context, ValidationError)
    assert error_with_context.message == "Invalid configuration value"
    assert error_with_context.context == {
        "parameter": "midi_note_min",
        "value": 130,
        "allowed_range": "0-127",
        "rule": "Must be <= 127",
    }
    assert "Invalid configuration value [Context:" in str(error_with_context)
    assert "parameter=midi_note_min" in str(error_with_context)
    assert "value=130" in str(error_with_context)


def test_configuration_error():
    """Test the ConfigurationError exception."""
    # Create a ConfigurationError instance
    error = ConfigurationError("Test ConfigurationError")

    # Verify that it's an instance of ConfigurationError and DrumGizmoError
    assert isinstance(error, ConfigurationError)
    assert isinstance(error, DrumGizmoError)

    # Verify the error message
    assert str(error) == "Test ConfigurationError"

    # Test with context
    error_with_context = ConfigurationError(
        "Configuration file not found",
        context={"file_path": "/path/to/config.ini", "section": "drumgizmo_kit_generator"},
    )
    assert isinstance(error_with_context, ConfigurationError)
    assert error_with_context.message == "Configuration file not found"
    assert error_with_context.context == {
        "file_path": "/path/to/config.ini",
        "section": "drumgizmo_kit_generator",
    }
    assert (
        str(error_with_context)
        == "Configuration file not found [Context: file_path=/path/to/config.ini, section=drumgizmo_kit_generator]"
    )


def test_xml_generation_error():
    """Test the XMLGenerationError exception."""
    # Create an XMLGenerationError instance
    error = XMLGenerationError("Test XMLGenerationError")

    # Verify that it's an instance of XMLGenerationError and DrumGizmoError
    assert isinstance(error, XMLGenerationError)
    assert isinstance(error, DrumGizmoError)

    # Verify the error message
    assert str(error) == "Test XMLGenerationError"

    # Test with context
    error_with_context = XMLGenerationError(
        "Failed to generate XML file",
        context={"file": "drumkit.xml", "reason": "Invalid instrument data"},
    )
    assert isinstance(error_with_context, XMLGenerationError)
    assert error_with_context.message == "Failed to generate XML file"
    assert error_with_context.context == {
        "file": "drumkit.xml",
        "reason": "Invalid instrument data",
    }
    assert (
        str(error_with_context)
        == "Failed to generate XML file [Context: file=drumkit.xml, reason=Invalid instrument data]"
    )
