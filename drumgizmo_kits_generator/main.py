#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SPDX-License-Identifier: MIT
SPDX-PackageName: DrumGizmo kits generator
SPDX-PackageHomePage: https://github.com/e-picas/drumgizmo-kits-generator
SPDX-FileCopyrightText: 2025 Pierre Cassat (Picas)

DrumGizmo Kit Generator - Main module
"""

import time
import traceback

from drumgizmo_kits_generator import cli, config, constants, kit_generator, logger, utils
from drumgizmo_kits_generator.exceptions import DrumGizmoError


def main() -> None:
    """Main entry point for the DrumGizmo Kit Generator."""
    try:
        start_time = time.perf_counter()
        args = cli.parse_arguments()

        # Initialize logger with verbosity level and raw output
        logger.set_verbose(args.verbose)
        logger.set_raw_output(args.raw_output)

        # Display application information in verbose mode
        logger.debug(f"{constants.APP_NAME} v{constants.APP_VERSION} - {constants.APP_LINK}")

        # Validate directories
        kit_generator.validate_directories(args.source, args.target)

        # Display processing directories
        logger.section("Process Main Directories")
        logger.info(f"Source directory: {args.source}")
        logger.info(f"Target directory: {args.target}")

        # Load configuration (already transformed and validated)
        metadata = config.load_configuration(args)

        # Print metadata
        kit_generator.print_metadata(metadata)

        # Scan source files
        extensions = metadata["extensions"]
        audio_files = kit_generator.scan_source_files(args.source, extensions)

        # Scan samples & rint information
        kit_generator.print_samples_info(audio_files, metadata)

        # Preview MIDI mapping in dry run mode
        if args.dry_run:
            kit_generator.print_midi_mapping(audio_files, metadata)
            logger.message("\nDry run mode enabled, stopping here")
            return

        # Check SoX dependency before proceeding
        utils.check_dependency(
            "sox",
            "The required 'SoX' software has not been found in the system, can not generate kit!",
        )

        # !! - GENERATION PROCESS START - !!
        # Nothing should be actually done in the system before this point

        # Prepare target directory
        kit_generator.prepare_target_directory(args.target)

        # Process audio files
        processed_audio_files = kit_generator.process_audio_files(
            audio_files, args.target, metadata
        )

        # Generate XML files
        kit_generator.generate_xml_files(audio_files, args.target, metadata)

        # Copy additional files
        kit_generator.copy_additional_files(args.source, args.target, metadata)

        end_time = time.perf_counter()
        generation_process_duration = end_time - start_time
        # GENERATION PROCESS END

        # Print summary
        kit_generator.print_summary(
            args.target, metadata, processed_audio_files, audio_files, generation_process_duration
        )

        logger.message("\nKit generation completed successfully!")
    except DrumGizmoError as e:
        logger.error(f"Error: {e}")
    # pylint: disable=broad-exception-caught
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        if logger.is_verbose():
            logger.error(traceback.format_exc())


if __name__ == "__main__":
    main()
