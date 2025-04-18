#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main script for DrumGizmo kit generation.
Uses the config, audio, xml_generator and utils modules to create a complete kit.
"""

import os
import sys
import argparse
import datetime
import shutil

# Import local modules
from config import read_config_file, CHANNELS, MAIN_CHANNELS
from audio import create_volume_variations, copy_sample_file, find_audio_files
from xml_generator import create_xml_file, create_drumkit_xml, create_midimap_xml
from utils import (
    prepare_target_directory, 
    prepare_instrument_directory, 
    get_timestamp, 
    extract_instrument_name,
    get_file_extension,
    print_summary
)

def parse_arguments():
    """
    Parse command line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(description='Create a DrumGizmo kit from audio samples')
    
    parser.add_argument('-s', '--source', required=True, help='Source directory containing audio samples')
    parser.add_argument('-t', '--target', required=True, help='Target directory for the DrumGizmo kit')
    parser.add_argument('-c', '--config', help='Configuration file path')
    parser.add_argument('-e', '--extensions', default='wav,WAV,flac,FLAC,ogg,OGG', 
                        help='Comma-separated list of audio file extensions to process (default: wav,WAV,flac,FLAC,ogg,OGG)')
    
    # Arguments for metadata (can be overridden by the configuration file)
    parser.add_argument('--name', help='Kit name')
    parser.add_argument('--version', default='1.0', help='Kit version (default: 1.0)')
    parser.add_argument('--description', default='Kit automatically created with 10 velocity levels', 
                       help='Kit description (default: Kit automatically created with 10 velocity levels)')
    parser.add_argument('--notes', help='Additional notes about the kit')
    parser.add_argument('--author', help='Kit author')
    parser.add_argument('--license', default='CC-BY-SA', help='Kit license (default: CC-BY-SA)')
    parser.add_argument('--website', help='Kit website')
    parser.add_argument('--logo', help='Kit logo filename')
    parser.add_argument('--samplerate', default='44100', help='Sample rate in Hz (default: 44100)')
    parser.add_argument('--instrument-prefix', help='Prefix for instrument names')
    
    return parser.parse_args()

def prepare_metadata(args):
    """
    Prepare kit metadata by combining command line arguments and configuration file.
    
    Args:
        args (argparse.Namespace): Command line arguments
        
    Returns:
        dict: Kit metadata
    """
    metadata = {}
    
    # Read configuration file if specified
    if args.config:
        config_metadata = read_config_file(args.config)
        metadata.update(config_metadata)
        print(f"Metadata loaded from config file: {config_metadata}", file=sys.stderr)
    
    # Override with command line arguments if specified
    if args.name:
        metadata['name'] = args.name
    elif 'name' not in metadata:
        metadata['name'] = 'DrumGizmoKit'
        
    if args.version:
        metadata['version'] = args.version
    elif 'version' not in metadata:
        metadata['version'] = '1.0'
        
    if args.description:
        metadata['description'] = args.description
    elif 'description' not in metadata:
        metadata['description'] = 'Kit automatically created with 10 velocity levels'
        
    if args.notes:
        metadata['notes'] = args.notes
    elif 'notes' not in metadata:
        # Use source directory name as sample information
        source_name = os.path.basename(os.path.abspath(args.source))
        metadata['notes'] = f"DrumGizmo kit generated from royalty free samples '{source_name}'"
        
    if args.author:
        metadata['author'] = args.author
    elif 'author' not in metadata:
        metadata['author'] = os.environ.get('USER', 'Unknown')
        
    if args.license:
        metadata['license'] = args.license
    elif 'license' not in metadata:
        metadata['license'] = 'CC-BY-SA'
        
    if args.website:
        metadata['website'] = args.website
        
    if args.logo:
        metadata['logo'] = args.logo
        
    if args.samplerate:
        metadata['samplerate'] = args.samplerate
    elif 'samplerate' not in metadata:
        metadata['samplerate'] = '44100'
        
    if args.instrument_prefix:
        metadata['instrument_prefix'] = args.instrument_prefix
        
    # Add date and script name to the description
    timestamp = get_timestamp()
    if 'notes' in metadata and metadata['notes']:
        # Don't modify notes if they already exist, except to add the date
        if " - Generated with create_drumgizmo_kit.py at " not in metadata['notes']:
            metadata['notes'] = f"{metadata['notes']} - Generated with create_drumgizmo_kit.py at {timestamp}"
    else:
        metadata['notes'] = f"Generated with create_drumgizmo_kit.py at {timestamp}"
    
    # Display final metadata for debugging
    print("\nFinal metadata after processing:", file=sys.stderr)
    for key, value in metadata.items():
        print(f"  {key}: {value}", file=sys.stderr)
    print("", file=sys.stderr)
        
    return metadata

def main():
    """
    Main function of the script.
    """
    # Parse arguments
    args = parse_arguments()
    
    # Prepare metadata
    metadata = prepare_metadata(args)
    
    # Prepare target directory
    if not prepare_target_directory(args.target):
        sys.exit(1)
    
    # Search for samples in the source directory
    extensions = args.extensions.split(',')
    samples = find_audio_files(args.source, extensions)
    
    print(f"Searching for samples in: {args.source}", file=sys.stderr)
    print(f"Number of samples found: {len(samples)}", file=sys.stderr)
    
    if not samples:
        print("Error: No audio samples found in the source directory", file=sys.stderr)
        sys.exit(1)
    
    # Process each sample
    instruments = []
    
    for sample in samples:
        # Extract instrument name
        instrument = extract_instrument_name(sample)
        instruments.append(instrument)
        
        # Get file extension
        extension = get_file_extension(sample)
        
        # Prepare directory for the instrument
        if not prepare_instrument_directory(instrument, args.target):
            continue
        
        # Copy original sample
        samples_dir = os.path.join(args.target, instrument, "samples")
        dest_file = os.path.join(samples_dir, f"1-{instrument}{extension}")
        
        if not copy_sample_file(sample, dest_file):
            continue
        
        # Create volume variations
        create_volume_variations(instrument, args.target, extension)
        
        # Create XML file for the instrument
        create_xml_file(instrument, args.target, metadata['version'], extension)
    
    # Create drumkit.xml file
    create_drumkit_xml(instruments, args.target, metadata)
    
    # Create midimap.xml file
    create_midimap_xml(instruments, args.target, metadata)
    
    # Copy logo if specified
    if 'logo' in metadata and metadata['logo']:
        logo_source = os.path.join(args.source, metadata['logo'])
        logo_dest = os.path.join(args.target, metadata['logo'])
        
        if os.path.exists(logo_source):
            try:
                shutil.copy2(logo_source, logo_dest)
            except Exception as e:
                print(f"Warning: Could not copy logo file: {e}", file=sys.stderr)
    
    # Display summary
    print_summary(metadata, instruments, args.target)

if __name__ == "__main__":
    main()
