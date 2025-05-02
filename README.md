# DrumGizmo Kits Generator

A Python tool for generating drum kits for [DrumGizmo](https://drumgizmo.org/), a multichannel drum sampler, from a directory of audio sources.

[![GitHub Release](https://img.shields.io/github/v/release/e-picas/drumgizmo-kits-generator)](https://github.com/e-picas/drumgizmo-kits-generator/releases)
[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/e-picas/drumgizmo-kits-generator/quality.yml?branch=master)](https://github.com/e-picas/drumgizmo-kits-generator/actions?query=branch%3Amaster)
[![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Fe-picas%2Fdrumgizmo-kits-generator%2Frefs%2Fheads%2Fmaster%2Fpyproject.toml)](https://www.python.org/)
[![GitHub License](https://img.shields.io/github/license/e-picas/drumgizmo-kits-generator)](https://github.com/e-picas/drumgizmo-kits-generator?tab=MIT-1-ov-file#readme)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=e-picas_drumgizmo-kits-generator&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=e-picas_drumgizmo-kits-generator)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=e-picas_drumgizmo-kits-generator&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=e-picas_drumgizmo-kits-generator)

[![DrumGizmo](https://img.shields.io/badge/DrumGizmo-%3E%3D0.9.20-orange)](https://drumgizmo.org/)

## Features (and table of contents)

- 🚀 **Generate [DrumGizmo kits from a set of audio samples](#generated-kit-structure)**
- 🎙️ **Support for [multiple audio formats](#note-about-audio-files-formats) (WAV, FLAC, OGG)**
- ⚡ **Automatic creation of [volume variations](#audio-samples-treatments) to manage velocity levels (10 by default)**
- 🧮 **[Alphabetical sorting of instruments](#original-audio-samples) and [assignment of consecutive MIDI notes](#midi-keys-repartition)**
- ⚙️ **[Read metadata](#kit-metadata) and options from a [configuration file](#configuration-file)**
- 📥 **Copy additional files to the final kit (see [options](#options))**
- ⬛ **Complete [command-line interface](#command-line)**

## Generated kit structure

The kit will follow the [DrumGizmo file format documentation](https://drumgizmo.org/wiki/doku.php?id=documentation:file_formats).

For example, based on the following sources of audio samples:

```
sources/
├── Instrument1.wav
├── Instrument2.wav
└── ...
```

The generated kit will have the following structure:

```
kit/
├── drumkit.xml
├── midimap.xml
├── Instrument1/
│   ├── instrument.xml
│   └── samples/
│       ├── 1-Instrument1.wav
│       ├── 2-Instrument1.wav
│       └── ...
├── Instrument2/
│   ├── instrument.xml
│   └── samples/
│       ├── 1-Instrument2.wav
│       ├── 2-Instrument2.wav
│       └── ...
└── ...
```

### Original audio samples

Audio samples must be in the root directory of the `source` (no recursion is processed). They are treated alphabetically, so you can order them to feet your needs as they will be [distributed to pre-defined MIDI notes](#midi-keys-repartition).

### Kit metadata

Based on yout options or configuration, the kit metadata will be something like the following:

```xml
  <metadata>
    <title>Test Kit</title>
    <description>This is a description</description>
    <notes>DrumGizmo kit generated for testing purpose - Generated with create_drumgizmo_kit.py at 2025-04-28 23:54</notes>
    <author>My name</author>
    <license>Private license</license>
    <samplerate>44100</samplerate>
    <website>https://me.com/</website>
    <logo src="my-logo.png"/>
    <created>Generated on 2025-04-28 23:54:45 with drumgizmo-kits-generator v1.3.0 (https://github.com/e-picas/drumgizmo-kits-generator)</created>
  </metadata>
```

### Audio samples treatments

Each original audio sample is duplicated X times to finally get the [`velocity-levels`](#options) number of volumes variations, assigned to corresponding "velocity" variations by setting the `power` entry of each sample on a cartesian formula based on 1 (1 / velocity-levels).

### Samplerate

The [`samplerate`](#options) of the generated kit (which defaults to `44100`) will be used for all samples and variations to assure the kit uniformity.

### About samples channels

The app will alternately use each original sample "channels" and assign them to the global "channels" of the kit (which defaults to the channels used by distributed [DSR kit](https://drumgizmo.org/wiki/doku.php?id=kits:drskit)):

```
"AmbL" (main)
"AmbR" (main)
"Hihat"
"Kdrum_back"
"Kdrum_front"
"Hihat"
"OHL" (main)
"OHR" (main)
"Ride"
"Snare_bottom"
"Snare_top"
"Tom1"
"Tom2"
"Tom3"
```

Use the [`channels`](#options) and [`main-channels`](#options) options to set them up to your needs.

### MIDI keys repartition

The samples will all be attached to consecutive MIDI notes around the [`midi-note-median`](#options) with some limits set by the [`midi-note-min`](#options) and [`midi-note-max`](#options) options. An error will be triggered if your project have more samples than the allowed MIDI notes.

For example, with a set of 3 audio samples and the default value `midi-note-median=60`, the final `midimap.xml` file would be:

```xml
  <map note="59" instr="Sample1" velmin="0" velmax="127"/>
  <map note="60" instr="Sample2" velmin="0" velmax="127"/>
  <map note="61" instr="Sample3" velmin="0" velmax="127"/>
```

### Note about audio files formats

We use [SoX (Sound eXchange)](https://sourceforge.net/projects/sox/) for audio processing, which may not handle every audio file formats natively. You may need to install some third-party drivers in your system for particular needs (i.e. "mp3" format). You can manage the audio files extensions with the [`extensions` option](#options).

## Installation & usage

### Prerequisites

- [Python 3.9](https://www.python.org/downloads/) or higher
- [SoX (Sound eXchange)](https://sourceforge.net/projects/sox/) for audio processing - Tested with version 14.4.2
- some other Python dependencies for development only

### Installation

Download and extract [the latest release](https://github.com/e-picas/drumgizmo-kits-generator/releases).

### Usage

#### Command Line

```cli
# basic usage:
python create_drumgizmo_kit.py -s /path/to/sources -t /path/to/target

# usage of a configuration file:
python create_drumgizmo_kit.py -s /path/to/sources -t /path/to/target -c /path/to/config.ini

# usage with some command line options:
python create_drumgizmo_kit.py -s /path/to/sources -t /path/to/target --name "Kit name" ...

# to read the doc:
python create_drumgizmo_kit.py -h
```

The following "special" options are in use to manage process output and actions:

-  `-h` / `--help`: read the application documentation
-  `-v` / `--verbose`: increase process verbosity with some debugging informations
-  `-x` / `--dry-run`: output the run data (options & audio samples found) but do not actually process the run - this can be used for validation.

#### Options

| Option | Description | Default |
|----------------------|---------------------|-------------|
| `-s` / `--source` | The path of your sources directory containing the audio samples - Samples must be in the root directory (no recursion) | *REQUIRED* |
| `-t` / `--target` | The path of the target directory where the kit will be generated - It will be created if it does not exist - Its contents are **deleted** before each run (you should probably use a temporary directory first) | *REQUIRED* |
| `-c` / `--config` | Path of a [configuration file](#configuration-file) to use | - |
| `--author` | The author(s) of the generated kit - [`drumkit.xml`](#kit-metadata) metadata | - |
| `--channels` | Comma-separated list of [audio channels](#about-samples-channels) to use in the kit | *see ["channels"](#about-samples-channels)* |
| `--description` | The description of the generated kit - [`drumkit.xml`](#kit-metadata) metadata | - |
| `--extensions` | Comma-separated list of [audio file extensions](#note-about-audio-files-formats) to process | `wav,WAV,flac,FLAC,ogg,OGG` |
| `--extra-files` | Comma-separated list of additional files to copy to the target directory - Local paths from the `source` directory | - |
| `--license` | The license of the generated kit - [`drumkit.xml`](#kit-metadata) metadata | `Private license` |
| `--logo` | Path of the kit logo filename - Local path from the `source` directory - [`drumkit.xml`](#kit-metadata) metadata | - |
| `--main-channels` | Comma-separated list of [**main** audio channels](#about-samples-channels) to use in the kit | *see ["channels"](#about-samples-channels)* |
| `--midi-note-max` | Maximum MIDI note allowed - [`midimap.xml`](#midi-keys-repartition) generation | `127` (<=127) |
| `--midi-note-median` | Median MIDI note for distributing instruments around - [`midimap.xml`](#midi-keys-repartition) generation | `60` (*C4* key) |
| `--midi-note-min` | Minimum MIDI note allowed - [`midimap.xml`](#midi-keys-repartition) generation | `1` (>=1) |
| `--name` | The name of the generated kit - [`drumkit.xml`](#kit-metadata) metadata | `DrumGizmo Kit` |
| `--notes` | Additional notes about the kit - An automatic string with the version of the python app and the generation date is suffixed - [`drumkit.xml`](#kit-metadata) metadata | - |
| `--samplerate` | [Sample rate](#samplerate) of the kit's samples (in *Hz*) - All generated samples will be changed to this rate including original - [`drumkit.xml`](#kit-metadata) metadata | `44100` |
| `--velocity-levels` | Total number of [velocity levels](#audio-samples-treatments) to generate in the target (the original sample + `velocity-levels`-1 automatically generated) | `10` |
| `--version` | The version of the generated kit - You may use it to manage your kit's versions over the time - [`drumkit.xml`](#kit-metadata) metadata | `1.0` |
| `--website` | The website of the generated kit - [`drumkit.xml`](#kit-metadata) metadata | - |

#### Configuration file

You can specify kit metadata and generation options in a configuration file (e.g., `drumgizmo-kit.ini`).
All command-line options have equivalent configuration file settings which must be defined in a `[drumgizmo_kit_generator]` header block. The configuration file takes precedence over default values but command-line arguments override configuration file settings.

```ini
[drumgizmo_kit_generator]
# General kit information
name = My Custom DrumGizmo Kit
version = 1.0
description = A custom drum kit for DrumGizmo
notes = Recorded with an acoustic drum kit in studio
author = Your Name
license = CC-BY-SA 4.0
website = https://example.com/my-drumgizmo-kit

# Additional files
logo = logo.png
extra_files = readme.txt,license.txt,credits.txt

# Audio parameters
samplerate = 48000
velocity_levels = 5

# MIDI configuration
midi_note_min = 35
midi_note_max = 81
midi_note_median = 60

# Audio file extensions to process
extensions = wav,WAV,flac,FLAC

# Audio channels configuration
channels = Kick,Snare,HiHat,Tom1,Tom2,Tom3,Ride,Crash,OHL,OHR,Room
main_channels = OHL,OHR,Room

```

## Contributing

If you find a bug or want to request a new feature, just [open an issue](https://github.com/e-picas/drumgizmo-kits-generator/issues/new/choose) and it will be taken care of asap.

### Development

To fix a bug or make a proposal in this app, you may commit to a personal branch, push it to the repo and then
[make a pull request](https://github.com/e-picas/drumgizmo-kits-generator/compare) explaining your modification.

#### Get the sources

Clone this repository:

```bash
git clone https://github.com/e-picas/drumgizmo-kits-generator.git
cd drumgizmo-kits-generator
```

#### Install the project

To install the dependencies and git hooks, run:

```bash
make install
```

#### Code guidelines & standards

The `pre-commit` hook will try to fix your code following some standards, run the linter and tests. It is automatically run by the hooks before each commit and validate that your commit message follows the [conventional commit format](https://www.conventionalcommits.org/en/v1.0.0/). These steps are run in the CI for validation.

#### Local single tasks

To format the code following the `.pre-commit-config.yaml`:

```bash
make format
```

To run the tests in `tests/` locally:

```bash
make test
```

To get the tests coverage levels:

```bash
make coverage
```

To check the code with pylint:

```bash
make lint
```

## Project info

### Releases

The releases are built manually with an automated process using [python-semantic-release](https://python-semantic-release.readthedocs.io/en/latest/).

### Security

Only the latest version of the project gets patched with security updates.

### License

This project is licensed under the [MIT](LICENSE) license.

### Authors

- This software is generated by [Claude 3.7 Sonnet](https://claude.ai/) guided by myself ^^
- "myself" is **[@e-Picas](https://github.com/e-picas)**

**NOTE** - The `.cascade-config` file is an auto-generated config file to load to Claude.AI to prepare its work.
