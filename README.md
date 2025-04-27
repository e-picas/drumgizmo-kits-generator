# DrumGizmo Kits Generator

A Python tool for generating drum kits for [DrumGizmo](https://drumgizmo.org/), a multichannel drum sampler, from a directory of audio sources.

![GitHub Release](https://img.shields.io/github/v/release/e-picas/drumgizmo-kits-generator)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/e-picas/drumgizmo-kits-generator/quality.yml?branch=master)
![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Fe-picas%2Fdrumgizmo-kits-generator%2Frefs%2Fheads%2Fmaster%2Fpyproject.toml)
![GitHub License](https://img.shields.io/github/license/e-picas/drumgizmo-kits-generator)


## Features

- Generate DrumGizmo kits from audio samples
- Support for multiple audio formats (WAV, FLAC, OGG)
- Automatic creation of volume variations (10 levels)
- Alphabetical sorting of instruments and assignment of consecutive MIDI notes
- Read metadata from a configuration file
- Copy additional files to the final kit
- Complete command-line interface

## Prerequisites

- [Python 3.8](https://www.python.org/downloads/) or higher
- [SoX (Sound eXchange)](https://sourceforge.net/projects/sox/) for audio processing
- some other Python dependencies for development (see the `requirements-dev.txt` file)

## Installation

Download and extract [the latest release](https://github.com/e-picas/drumgizmo-kits-generator/releases).

## Usage

### Command Line

```bash
python create_drumgizmo_kit.py -s /path/to/sources -t /path/to/target -c /path/to/config.ini
```

### Options

```
options:
  -h, --help            show this help message and exit
  -s SOURCE, --source SOURCE
                        REQUIRED - Source directory containing audio samples
  -t TARGET, --target TARGET
                        REQUIRED - Target directory for the DrumGizmo kit
  -c CONFIG, --config CONFIG
                        Configuration file path (INI format)
  --extensions EXTENSIONS
                        Comma-separated list of audio file extensions to process (default: wav,WAV,flac,FLAC,ogg,OGG)
  --velocity-levels VELOCITY_LEVELS
                        Number of velocity levels to generate (default: 10)
  --midi-note-min MIDI_NOTE_MIN
                        Minimum MIDI note number allowed (default: 0)
  --midi-note-max MIDI_NOTE_MAX
                        Maximum MIDI note number allowed (default: 127)
  --midi-note-median MIDI_NOTE_MEDIAN
                        Median MIDI note for distributing instruments around (default: 60)
  --name NAME           Kit name
  --version VERSION     Kit version (default: 1.0)
  --description DESCRIPTION
                        Kit description
  --notes NOTES         Additional notes about the kit
  --author AUTHOR       Kit author
  --license LICENSE     Kit license (default: Private license)
  --website WEBSITE     Kit website
  --logo LOGO           Kit logo filename
  --samplerate SAMPLERATE
                        Sample rate in Hz (default: 44100)
  --instrument-prefix INSTRUMENT_PREFIX
                        Prefix for instrument names
  --extra-files EXTRA_FILES
                        Comma-separated list of additional files to copy to the target directory
```

### Configuration File

You can specify kit metadata and generation options in a configuration file (e.g., `drumgizmo-kit.ini`):

```ini
# Kit metadata
kit_name = "My Drum Kit"
kit_version = "1.0.0"
kit_description = "An acoustic drum kit"
kit_notes = "Recorded in a professional studio"
kit_author = "Your Name"
kit_license = "CC-BY-SA"
kit_website = "https://your-site.com"
kit_samplerate = "44100"
kit_instrument_prefix = "MyKit"
kit_logo = "logo.png"
kit_extra_files = "README.txt,LICENSE.txt,photo.jpg"

# Generation options
kit_velocity_levels = "10"
kit_midi_note_min = "0"
kit_midi_note_max = "127"
kit_midi_note_median = "60"
kit_extensions = "wav,WAV,flac,FLAC,ogg,OGG"
```

All command-line options have equivalent configuration file settings. The configuration file takes precedence over default values but command-line arguments override configuration file settings.

| Config file variable | Command-line option | Description |
|---------------------|---------------------|-------------|
| `kit_name` | `--name` | Kit name |
| `kit_version` | `--version` | Kit version |
| `kit_description` | `--description` | Kit description |
| `kit_notes` | `--notes` | Additional notes about the kit |
| `kit_author` | `--author` | Kit author |
| `kit_license` | `--license` | Kit license |
| `kit_website` | `--website` | Kit website |
| `kit_logo` | `--logo` | Kit logo filename |
| `kit_samplerate` | `--samplerate` | Sample rate in Hz |
| `kit_instrument_prefix` | `--instrument-prefix` | Prefix for instrument names |
| `kit_extra_files` | `--extra-files` | Additional files to copy |
| `kit_velocity_levels` | `--velocity-levels` | Number of velocity levels to generate |
| `kit_midi_note_min` | `--midi-note-min` | Minimum MIDI note number allowed |
| `kit_midi_note_max` | `--midi-note-max` | Maximum MIDI note number allowed |
| `kit_midi_note_median` | `--midi-note-median` | Median MIDI note for distributing instruments |
| `kit_extensions` | `--extensions` | Audio file extensions to process |

## Generated Kit Structure

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

## Development

To fix a bug or make a proposal in this app, you may commit to a personal branch, push it to the repo and then
make a "Pull request" explaining your modification.

### Get the sources

Clone this repository:

```bash
git clone https://github.com/e-picas/drumgizmo-kits-generator.git
cd drumgizmo-kits-generator
```

### Install the project

To install the dependencies and git hooks, run:

```bash
make install
```

The hooks will run the linter and tests before each commit and validate that your commit message follows the [conventional commit format](https://www.conventionalcommits.org/en/v1.0.0/). They are run in the CI for validation.

### Local validation

To run unit tests locally:

```bash
make test
```

To get the coverage levels:

```bash
make coverage
```

To check the code with pylint:

```bash
make lint
```

## License

This project is licensed under the [MIT](LICENSE) license.

## Author

- This software is generated by [Claude 3.7 Sonnet](https://claude.ai/) guided by myself ^^
- "myself" is e-Picas (<https://github.com/e-picas>)
