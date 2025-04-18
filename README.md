# DrumGizmo Kits Generator

A modular tool for generating percussion kits for DrumGizmo from audio samples.

## Description

This project transforms a collection of audio samples into a complete DrumGizmo kit with multiple velocity levels. It automatically generates all necessary XML files and organizes the samples according to the structure expected by DrumGizmo.

## Project Structure

The project is organized into several modules for better readability and maintainability:

- `create_drumgizmo_kit.py`: Main entry script
- `main.py`: Main program logic
- `config.py`: Configuration and global variables
- `audio.py`: Audio file processing
- `xml_generator.py`: XML file generation
- `utils.py`: Various utility functions

## Prerequisites

- Python 3.6+
- SoX (Sound eXchange) for audio processing

## Usage

```bash
./create_drumgizmo_kit.py -s <source_directory> -t <target_directory> [-c <config_file>] [options]
```

### Options

- `-s, --source`: Source directory containing audio samples (required)
- `-t, --target`: Target directory for the DrumGizmo kit (required)
- `-c, --config`: Path to an INI configuration file
- `-e, --extensions`: List of audio file extensions to process (comma-separated)
- `--name`: Kit name
- `--version`: Kit version (default: 1.0)
- `--description`: Kit description
- `--notes`: Additional notes about the kit
- `--author`: Kit author
- `--license`: Kit license (default: CC-BY-SA)
- `--website`: Kit website
- `--logo`: Logo filename
- `--samplerate`: Sample rate in Hz (default: 44100)
- `--instrument-prefix`: Prefix for instrument names

## Configuration File

You can specify kit metadata in an INI configuration file:

```ini
KIT_NAME="Kit Name"
KIT_VERSION="1.0"
KIT_DESCRIPTION="Kit description"
KIT_NOTES="Additional notes"
KIT_AUTHOR="Author name"
KIT_LICENSE="CC-BY-SA"
KIT_WEBSITE="https://example.com/"
KIT_LOGO="logo.jpg"
KIT_SAMPLERATE="44100"
KIT_INSTRUMENT_PREFIX="Prefix"
```

## Audio Channels

The audio channels used are defined in `config.py`:

```python
CHANNELS = [
    "AmbL", "AmbR", "Hihat", "Kdrum_back", "Kdrum_front", 
    "OHL", "OHR", "Ride", "Snare_bottom", "Snare_top", 
    "Tom1", "Tom2", "Tom3"
]

MAIN_CHANNELS = ["AmbL", "AmbR", "OHL", "OHR", "Snare_top"]
```

To modify the channels used, simply edit these lists.

## Example Usage

```bash
./create_drumgizmo_kit.py -s Darbuka8514/ -t DarbukaKit_generated -c Darbuka8514/drumgizmo-kit.ini
```

## License

CC-BY-SA
