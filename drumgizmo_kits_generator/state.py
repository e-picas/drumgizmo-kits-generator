#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SPDX-License-Identifier: MIT
SPDX-PackageName: DrumGizmo kits generator
SPDX-PackageHomePage: https://github.com/e-picas/drumgizmo-kits-generator
SPDX-FileCopyrightText: 2025 Pierre Cassat (Picas)

DrumGizmo Kit Generator - State module
"""
from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class RunData:
    """
    Central state object for DrumGizmo Kit Generator.
    Holds all relevant paths, configuration, and processing data.
    Keys for audio_sources, midi_mapping, and audio_processed are instrument names.
    """

    source_dir: str
    target_dir: str

    """
    All configuration data like `config_name: val`
    All entries should be transformed and validated, ready to be used
    """
    config: Dict[str, Any] = field(default_factory=dict)

    """
    All audio sources like
    ```
    instrument_name: {
        'bits': int,
        'channels': int,
        'duration': float,
        'samplerate': int,
        'source_path': str
    }
    ```
    """
    audio_sources: Dict[str, Any] = field(default_factory=dict)

    """
    All MIDI mappings like `instrument_name: midi_note`
    """
    midi_mapping: Dict[str, Any] = field(default_factory=dict)

    """
    All processed audio files like `instrument_name: {"file_path": {"volume": float}}`
    """
    audio_processed: Dict[str, Any] = field(default_factory=dict)

    """
    Total kit generation time in seconds (set at the end of the process)
    """
    generation_time: float = 0.0
