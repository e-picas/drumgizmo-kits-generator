# DrumGizmo Kits Generator

A Python tool for generating drum kits for [DrumGizmo](https://drumgizmo.org/), a multichannel drum sampler, from a directory of audio sources.

[![GitHub Release](https://img.shields.io/github/v/release/e-picas/drumgizmo-kits-generator)](https://github.com/e-picas/drumgizmo-kits-generator/releases)
[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/e-picas/drumgizmo-kits-generator/quality.yml?branch=master)](https://github.com/e-picas/drumgizmo-kits-generator/actions?query=branch%3Amaster)
[![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Fe-picas%2Fdrumgizmo-kits-generator%2Frefs%2Fheads%2Fmaster%2Fpyproject.toml)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/e-picas/drumgizmo-kits-generator?tab=License-1-ov-file#readme)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=e-picas_drumgizmo-kits-generator&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=e-picas_drumgizmo-kits-generator)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=e-picas_drumgizmo-kits-generator&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=e-picas_drumgizmo-kits-generator)

[![DrumGizmo](https://img.shields.io/badge/DrumGizmo-%3E%3D0.9.20-orange)](https://drumgizmo.org/)

## Features (and table of contents)

- 🚀 **Generate [DrumGizmo kits from a set of audio samples](#generated-kit-structure)**
- 🎙️ **Support for [multiple audio formats](#note-about-audio-files-formats)**
- ⚡ **Automatic creation of [volume variations](#audio-samples-treatments) to manage velocity levels**
- 🧮 **[Alphabetical sorting of instruments](#original-audio-samples) and [assignment of consecutive MIDI notes](#midi-keys-repartition)**
- ⚙️ **[Read metadata](#kit-metadata) and [options](#options) from a [configuration file](#configuration-file)**
- 📥 **Copy additional files to the final kit**
- ⬛ **Complete [command-line interface](#command-line)**

## Generated kit structure

The kit will follow the [DrumGizmo file format documentation](https://drumgizmo.org/wiki/doku.php?id=documentation:file_formats).

>   For example, based on the following sources of audio samples:
>   ```
>   sources/
>   ├── Instrument1.wav
>   ├── Instrument2.wav
>   └── ...
>   ```
>   The generated kit will have the following structure:
>   ```
>   kit/
>   ├── drumkit.xml
>   ├── midimap.xml
>   ├── Instrument1/
>   │   ├── instrument.xml
>   │   └── samples/
>   │       ├── 1-Instrument1.wav
>   │       ├── 2-Instrument1.wav
>   │       └── ...
>   ├── Instrument2/
>   │   ├── instrument.xml
>   │   └── samples/
>   │       ├── 1-Instrument2.wav
>   │       ├── 2-Instrument2.wav
>   │       └── ...
>   └── ...
>   ```

>   **NOTE** - A full generated kit is available in the [`examples/target/`](https://github.com/e-picas/drumgizmo-kits-generator/tree/master/examples/target) directory, based on the [`examples/sources/`](https://github.com/e-picas/drumgizmo-kits-generator/tree/master/examples/sources) sources and using the [`examples/drumgizmo-kit-example.ini`](https://github.com/e-picas/drumgizmo-kits-generator/tree/master/examples/drumgizmo-kit-example.ini) configuration file.

### Original audio samples

Audio samples must be in the root directory of the [`source` option](#options) (no recursion is processed). They are treated alphabetically, so you can order them to fit your needs as they will be [distributed to pre-defined MIDI notes](#midi-keys-repartition).

### Target directory of the generated kit

The new kit is generated in the [`target` option](#options) directory. It will be created if it does not exist. Its contents are **deleted** before each run.

>   **NOTE** - You should probably use a temporary directory first or use the [`dry-run` mode](#command-line) to validate your kit data before actually generating it.

### Kit metadata

You may use the following [`metadata` options](#options) or [configuration](#configuration-file) to fit your needs: `name`, `version`, `license`, `description`, `logo`, `notes`, `author` and `website`.

>   The kit metadata block of the `drumkit.xml` file has the following structure:
>   ```xml
>   <drumkit version="2.4" name="Test Kit" samplerate="44100">
>     <metadata>
>       <title>Test Kit</title>
>       <description>This is a description</description>
>       <notes>DrumGizmo kit generated for testing purpose</notes>
>       <author>My name</author>
>       <version>2.4</version>
>       <license>Private license</license>
>       <samplerate>44100</samplerate>
>       <website>https://me.com/</website>
>       <logo src="my-logo.png"/>
>       <created>Generated on 2025-04-28 23:54:45 with drumgizmo-kits-generator v1.3.0 (https://github.com/e-picas/drumgizmo-kits-generator)</created>
>     </metadata>
>   ```

### Audio samples treatments

Each original audio sample is duplicated X times to finally get the [`velocity-levels`](#options) number of volume variations, assigned to corresponding "velocity" variations by setting the `power` entry of each sample.

>   For example, for a value of `velocity_levels=4`, we will have:
>   ```xml
>       <sample name="Sample-Original" power="1.000000" />
>       <sample name="Sample-Volume-0.75" power="0.750000" />
>       <sample name="Sample-Volume-0.5" power="0.500000" />
>       <sample name="Sample-Volume-0.25" power="0.250000" />
>   ```

The [`variations-method`](#options) option defines how the volume variations are calculated and can be one of the following:

*   **`linear`** (default): the volume variations are calculated on a linear basis: `1 - (actual_volume / total_levels) * 0.75`
    >   For example, for a value of `velocity_levels=4`, we would have:
    >   ```
    >   DEBUG: Created velocity variation 1/4 at 1.00 volume
    >   DEBUG: Created velocity variation 2/4 at 0.75 volume
    >   DEBUG: Created velocity variation 3/4 at 0.50 volume
    >   DEBUG: Created velocity variation 4/4 at 0.25 volume
    >   ```

*   **`logarithmic`**: the volume variations are calculated on a logarithmic basis: `0.25 + (log10(1 + 9 * (1 - actual_volume / total_levels)) * 0.75)`; this method is recommended for a more natural volume variation to human ears but may not be the best choice for all kits (it is not the default one)
    >   For example, for a value of `velocity_levels=4`, we would have:
    >   ```
    >   DEBUG: Created velocity variation 1/4 at 1.00 volume
    >   DEBUG: Created velocity variation 2/4 at 0.82 volume
    >   DEBUG: Created velocity variation 3/4 at 0.57 volume
    >   DEBUG: Created velocity variation 4/4 at 0.25 volume
    >   ```


### Samplerate

The [`samplerate`](#options) of the generated kit (which defaults to `44100`), defined in *Hz*, will be used for all samples and variations to ensure the kit uniformity.

### About samples channels

The app will alternately use each original sample "channels" and assign them to the global "channels" of the kit, which defaults to a simple stereo `[ left , right ]` list.

Use the [`channels`](#options) and [`main-channels`](#options) options to set them up to your needs.

>   For example, to use the channels defined in distributed [DSR kit](https://drumgizmo.org/wiki/doku.php?id=kits:drskit), you would use:
>   ```
>   channels = "AmbL,AmbR,Hihat,Kdrum_back,Kdrum_front,OHL,OHR,Ride,Snare_bottom,Snare_top,Tom1,Tom2,Tom3"
>   main_channels = "AmbL,AmbR,OHL,OHR"
>   ```
>   Which will result in the following `instrument` XML blocks:
>   ```xml
>        <instrument name="Sample" file="Sample/Sample.xml">
>         <channelmap in="AmbL" out="AmbL" main="true"/>
>         <channelmap in="AmbR" out="AmbR" main="true"/>
>         <channelmap in="Hihat" out="Hihat"/>
>         <channelmap in="Kdrum_back" out="Kdrum_back"/>
>         <channelmap in="Kdrum_front" out="Kdrum_front"/>
>         <channelmap in="OHL" out="OHL" main="true"/>
>         <channelmap in="OHR" out="OHR" main="true"/>
>         <channelmap in="Ride" out="Ride"/>
>         <channelmap in="Snare_bottom" out="Snare_bottom"/>
>         <channelmap in="Snare_top" out="Snare_top"/>
>         <channelmap in="Tom1" out="Tom1"/>
>         <channelmap in="Tom2" out="Tom2"/>
>         <channelmap in="Tom3" out="Tom3"/>
>       </instrument>
> ```

### MIDI keys repartition

The samples will all be attached to consecutive MIDI notes around the [`midi-note-median`](#options) with some limits set by the [`midi-note-min`](#options) and [`midi-note-max`](#options) options. A warning will be printed if your project has more samples than the allowed MIDI notes.

The notes are defined in a global `[0,127]` range and the default `midi-note-median` is set to `60`, which is the *C4* key of a MIDI keyboard.

>   For example, with a set of 3 audio samples and the default value `midi-note-median=60`, the final `midimap.xml` file would be:
>   ```xml
>     <map note="59" instr="Sample-1" />
>     <map note="60" instr="Sample-2" />
>     <map note="61" instr="Sample-3" />
>   ```

### Extra files

You can use the [`extra-files` option](#options) to set up a list of files to copy "as is" in the final kit (i.e. for a LICENSE file or a manual).

### Note about audio files formats

We use [SoX (Sound eXchange)](https://sourceforge.net/projects/sox/) for audio processing, which may not handle every audio files formats natively. You may need to install some third-party drivers in your system for particular needs (i.e. "mp3"). You can manage the audio files extensions with the [`extensions` option](#options).

## Installation & usage

### Prerequisites

- [Python 3.9](https://www.python.org/downloads/) or higher
- [SoX (Sound eXchange)](https://sourceforge.net/projects/sox/) for audio processing - Tested with version 14.4.2
- Some other Python dependencies installed with [`pip`](https://pip.pypa.io/en/stable/installation/)

### Installation

Download and extract [the latest release](https://github.com/e-picas/drumgizmo-kits-generator/releases), go to the release's directory with a terminal and install its dependencies:

```cli
pip install .
```

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

#### Execution flags

The following "special" options can be used to manage process output and run:

-  `-h` / `--help`: read the application documentation
-  `-v` / `--verbose`: increase process verbosity with some debugging information
-  `-x` / `--dry-run`: output the run data (options & audio samples found) but do not actually process the run - this can be used for validation
-  `-V` / `--app-version`: show the application version number and exit
-  `-r` / `--raw-output`: do not include ANSI characters in output (for automatic processing)

#### Options

| Option | Description | Default |
|----------------------|---------------------|-------------|
| `-s` / `--source` | The path of your [sources directory](#original-audio-samples) containing the audio samples | *REQUIRED* |
| `-t` / `--target` | The path of the [target directory](#target-directory-of-the-generated-kit) where the kit will be generated | *REQUIRED* |
| `-c` / `--config` | Path of a [configuration file](#configuration-file) to use | `drumgizmo-kit.ini` |
| `--author` | The author(s) of the generated kit - [`drumkit.xml`](#kit-metadata) metadata | - |
| `--channels` | Comma-separated list of [audio channels](#about-samples-channels) to use in the kit | `Left,Right` |
| `--description` | The description of the generated kit - [`drumkit.xml`](#kit-metadata) metadata | - |
| `--extensions` | Comma-separated list of [audio file extensions](#note-about-audio-files-formats) to process | `wav,WAV,flac,FLAC,ogg,OGG` |
| `--extra-files` | Comma-separated list of additional files to copy to the target directory - Local paths from the `source` directory | - |
| `--license` | The license of the generated kit - [`drumkit.xml`](#kit-metadata) metadata | `Private license` |
| `--logo` | Path of the kit logo filename - Local path from the `source` directory - [`drumkit.xml`](#kit-metadata) metadata | - |
| `--main-channels` | Comma-separated list of [**main** audio channels](#about-samples-channels) to use in the kit | - |
| `--midi-note-max` | Maximum [MIDI note](#midi-keys-repartition) allowed - [`midimap.xml`](#midi-keys-repartition) generation | `127` |
| `--midi-note-median` | Median [MIDI note](#midi-keys-repartition) for distributing instruments around - [`midimap.xml`](#midi-keys-repartition) generation | `60` |
| `--midi-note-min` | Minimum [MIDI note](#midi-keys-repartition) allowed - [`midimap.xml`](#midi-keys-repartition) generation | `0` |
| `--name` | The name of the generated kit - [`drumkit.xml`](#kit-metadata) metadata | `DrumGizmo Kit` |
| `--notes` | Additional notes about the kit - [`drumkit.xml`](#kit-metadata) metadata | - |
| `--samplerate` | [Sample rate](#samplerate) of the kit's samples (in *Hz*) - [`drumkit.xml`](#kit-metadata) metadata | `44100` |
| `--variations-method` | [Variations method](#audio-samples-treatments) to generate velocity variations in `[ linear , logarithmic ]` | `linear` |
| `--velocity-levels` | Total number of [velocity levels](#audio-samples-treatments) to generate in the target (including original sample) | `10` |
| `--version` | The version of the generated kit - You may use it to manage your kit's versions over time - [`drumkit.xml`](#kit-metadata) metadata | `1.0` |
| `--website` | The website of the generated kit - [`drumkit.xml`](#kit-metadata) metadata | - |

#### Configuration file

You can specify kit metadata and generation options in a configuration file, in [*INI* format](https://en.wikipedia.org/wiki/INI_file), and pass it as a `--config` parameter. If a file named `drumgizmo-kit.ini` is found in the sources directory, it will be loaded automatically.

All command-line options have equivalent configuration file settings which must be defined in a `[drumgizmo_kit_generator]` header block replacing *dashes* by *underscores*. The configuration file takes precedence over default values but command-line arguments override configuration file settings.

>   **NOTE** - For a full example, please see the [`examples/drumgizmo-kit-example.ini`](https://github.com/e-picas/drumgizmo-kits-generator/blob/master/examples/drumgizmo-kit-example.ini) file.

## Contributing

If you find a bug or want to request a new feature, just [open an issue](https://github.com/e-picas/drumgizmo-kits-generator/issues/new/choose) and it will be taken care of asap.

If you want to work on this project, please read the [CONTRIBUTING.md](CONTRIBUTING.md) file.

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

**NOTE** - The `.cascade-config` file is a config file to load to Claude.AI to prepare its work.
