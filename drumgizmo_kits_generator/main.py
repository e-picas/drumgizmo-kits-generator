#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SPDX-License-Identifier: MIT
SPDX-PackageName: DrumGizmo kits generator
SPDX-PackageHomePage: https://github.com/e-picas/drumgizmo-kits-generator
SPDX-FileCopyrightText: 2025 Pierre Cassat (Picas)

DrumGizmo Kit Generator - Main module
"""

import os
import sys
import time

from drumgizmo_kits_generator import cli, config, constants, kit_generator, logger, utils
from drumgizmo_kits_generator.exceptions import DrumGizmoError
from drumgizmo_kits_generator.state import RunData


def main() -> None:
    """Main entry point for the DrumGizmo Kit Generator."""
    try:
        logger.log(
            "INFO",
            f"### Starting run {os.getpid()} of DrumGizmo Kit Generator with CLI params: {sys.argv} ###",
        )
        start_time = time.perf_counter()
        args = cli.parse_arguments()

        # Prepare RunData instance (explicit state management)
        run_data = RunData(source_dir=args.source, target_dir=args.target)

        # Initialize logger with verbosity level and raw output
        logger.set_verbose(args.verbose)
        logger.set_raw_output(args.raw_output)

        # Display application information in verbose mode
        if not logger.is_raw_output():
            logger.debug(f"{constants.APP_NAME} v{constants.APP_VERSION} - {constants.APP_LINK}")

        # Validate directories
        kit_generator.validate_directories(run_data)

        # Display processing directories
        logger.section("Process Main Directories")
        logger.info(f"Source directory: {run_data.source_dir}")
        logger.info(f"Target directory: {run_data.target_dir}")

        # Load configuration
        logger.log("INFO", "Loading configuration...")
        run_data.config = config.load_configuration(args)

        # Print metadata
        kit_generator.print_metadata(run_data)

        # Scan samples & print information
        logger.log("INFO", "Scanning sources directory...")
        kit_generator.scan_source_files(run_data)

        # Evaluate MIDI mapping
        logger.log("INFO", "Evaluating MIDI mapping...")
        kit_generator.evaluate_midi_mapping(run_data)

        # Preview MIDI mapping in dry run mode
        if args.dry_run:
            kit_generator.print_midi_mapping(run_data)
            logger.message("\nDry run mode enabled, stopping here")
            return

        # Check SoX dependency before proceeding
        utils.check_dependency(
            "sox",
            "The required 'SoX' software has not been found in the system, can not generate kit!",
        )

        # !! - GENERATION PROCESS START - !!
        # Nothing should be actually done in the system before this point
        logger.log("INFO", "Generating kit...")

        # Prepare target directory
        kit_generator.prepare_target_directory(run_data)

        # Process audio files
        kit_generator.process_audio_files(run_data)

        # Generate XML files
        kit_generator.generate_xml_files(run_data)

        # Copy additional files
        kit_generator.copy_additional_files(run_data)

        end_time = time.perf_counter()
        run_data.generation_time = end_time - start_time
        # GENERATION PROCESS END

        # Print summary
        kit_generator.print_summary(run_data)

        logger.message("\nKit generation completed successfully!")
        logger.log(
            "INFO", f"### Ending run {os.getpid()} in {run_data.generation_time:.2f} seconds ###"
        )
    except DrumGizmoError as e:
        logger.error(f"{e}", e)
    # pylint: disable=broad-exception-caught
    except Exception as e:
        logger.error(f"Unexpected error: {e}", e)


if __name__ == "__main__":
    main()
