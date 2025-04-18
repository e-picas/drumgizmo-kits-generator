#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuration module for DrumGizmo kit generator.
Contains global variables and constants used across the application.
"""

import os
import configparser

# Global variables
metadata = {}

# List of audio channels used in XML files
CHANNELS = [
    "AmbL",
    "AmbR",
    "Hihat",
    "Kdrum_back",
    "Kdrum_front",
    "OHL",
    "OHR",
    "Ride",
    "Snare_bottom",
    "Snare_top",
    "Tom1",
    "Tom2",
    "Tom3"
]

# List of main channels (with main="true" attribute)
MAIN_CHANNELS = ["AmbL", "AmbR", "OHL", "OHR", "Snare_top"]

# Mapping of channels to their filechannel
CHANNEL_TO_FILECHANNEL = {
    "AmbL": "1",
    "AmbR": "2",
    "Hihat": "3",
    "Kdrum_back": "4",
    "Kdrum_front": "5",
    "OHL": "6",
    "OHR": "7",
    "Ride": "8",
    "Snare_bottom": "9",
    "Snare_top": "10",
    "Tom1": "11",
    "Tom2": "12",
    "Tom3": "13"
}

def get_filechannel(channel):
    """
    Determines the appropriate filechannel for a given channel.
    
    Args:
        channel (str): Audio channel name
        
    Returns:
        str: Filechannel number (1-13) for the given channel
    """
    return CHANNEL_TO_FILECHANNEL.get(channel, "1")

def read_config_file(config_file):
    """
    Reads a configuration file and extracts metadata.
    
    Args:
        config_file (str): Path to the configuration file
        
    Returns:
        dict: Dictionary containing metadata
    """
    config = configparser.ConfigParser()
    
    try:
        # Check if the file contains a [DEFAULT] section
        with open(config_file, 'r') as f:
            content = f.read()
            
        # If the file doesn't start with a section, add [DEFAULT]
        if not content.lstrip().startswith('['):
            with open(config_file, 'r') as f:
                config_content = f.read()
                
            # Create a temporary file with the [DEFAULT] section
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp:
                temp.write('[DEFAULT]\n' + config_content)
                temp_name = temp.name
                
            # Read the temporary file
            config.read(temp_name)
            
            # Delete the temporary file
            import os
            os.unlink(temp_name)
        else:
            config.read(config_file)
            
        print(f"Reading configuration from: {config_file}", file=os.sys.stderr)
        
        # Check if the file was correctly read
        if 'DEFAULT' not in config:
            print("Warning: Configuration file format is incorrect", file=os.sys.stderr)
            return {}
            
        print("Configuration loaded successfully", file=os.sys.stderr)
        print("Raw configuration values:", file=os.sys.stderr)
        for key in config['DEFAULT']:
            print(f"  {key} = {config['DEFAULT'][key]}", file=os.sys.stderr)
        
        # Extract values and remove quotes if present
        result = {}
        for key in config['DEFAULT']:
            value = config['DEFAULT'][key]
            # Remove quotes if present
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1]
            
            # Convert configuration keys to metadata keys
            key_lower = key.lower()  # Convert key to lowercase
            if key_lower.startswith('kit_'):
                meta_key = key_lower[4:]  # Remove 'kit_'
                result[meta_key] = value
                
        # Display metadata read for debugging
        print("Metadata read from configuration:", file=os.sys.stderr)
        for key, value in result.items():
            print(f"  {key}: {value}", file=os.sys.stderr)
        
        return result
        
    except Exception as e:
        print(f"Error reading configuration file: {e}", file=os.sys.stderr)
        return {}
