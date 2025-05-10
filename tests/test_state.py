#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for the RunData state object.
"""
from drumgizmo_kits_generator.state import RunData


def test_rundata_minimal_init():
    """Test minimal initialization of RunData."""
    rd = RunData(source_dir="/src", target_dir="/dst")
    assert rd.source_dir == "/src"
    assert rd.target_dir == "/dst"
    assert isinstance(rd.config, dict)
    assert isinstance(rd.audio_sources, dict)
    assert isinstance(rd.midi_mapping, dict)
    assert isinstance(rd.audio_processed, dict)
    assert rd.generation_time == 0.0


def test_rundata_full_init():
    """Test full initialization of RunData."""
    rd = RunData(
        source_dir="/src",
        target_dir="/dst",
        config={"foo": "bar"},
        audio_sources={"Kick": {"samplerate": 44100}},
        midi_mapping={"Kick": 36},
        audio_processed={"Kick": {"/dst/Kick.wav": {"volume": 1.0}}},
        generation_time=12.34,
    )
    assert rd.config["foo"] == "bar"
    assert rd.audio_sources["Kick"]["samplerate"] == 44100
    assert rd.midi_mapping["Kick"] == 36
    assert rd.audio_processed["Kick"]["/dst/Kick.wav"]["volume"] == 1.0
    assert rd.generation_time == 12.34


def test_rundata_mutability():
    """Test mutability of RunData."""
    rd = RunData(source_dir="/src", target_dir="/dst")
    rd.config["test"] = 123
    rd.audio_sources["Snare"] = {"samplerate": 48000}
    rd.midi_mapping["Snare"] = 38
    rd.audio_processed["Snare"] = {"/dst/Snare.wav": {"volume": 0.9}}
    rd.generation_time = 5.67
    assert rd.config["test"] == 123
    assert rd.audio_sources["Snare"]["samplerate"] == 48000
    assert rd.midi_mapping["Snare"] == 38
    assert rd.audio_processed["Snare"]["/dst/Snare.wav"]["volume"] == 0.9
    assert rd.generation_time == 5.67


def test_rundata_repr_and_eq():
    """Test representation and equality of RunData."""
    rd1 = RunData(source_dir="/src", target_dir="/dst")
    rd2 = RunData(source_dir="/src", target_dir="/dst")
    assert rd1 == rd2
    assert "RunData" in repr(rd1)
