#!/usr/bin/env python
# rewritten by gemini 2025-07-10

# SECTION : Imports
import sys
import os
import logging
import sqlite3
import argparse
# import datetime

# --- Add script's directory to sys.path ---
# To be able to import local modules
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)
# --- End sys.path modification ---

from funktions.process_result_file import process_result_file  # noqa: E402

from funktions.error_template import (  # noqa: E402
    setup_logger,
    log_message,
    processing_error_message,
    processing_result_message,
)


# !SECTION


# SECTION: MAIN
if __name__ == "__main__":
    script_name = os.path.basename(__file__)
    logger_instance, log_file_name_used = setup_logger(script_name)

    # SECTION: Argument parsing
    parser = argparse.ArgumentParser(
        prog="results_to_db.py",
        usage="%(prog)s [options]",
        description="Wrangle results and insert into SQLite database.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        add_help=True,
    )

    # Version and example arguments (optional)
    parser.add_argument(
        "--example",
        action="store_true",
        help="Show an example of usage and exit.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.0.2",
        help="Print the script version and exit.",
    )
    # Required arguments
    parser.add_argument(
        "--database",
        action="store",
        default="output.sqlite",
        required=False,
        help="Path to a SQLite database file where results will be stored.\n"
        "If the path does not exist, it will be created.\n"
        "If not provided, the database will default to: DPI.sqlite",
    )
    parser.add_argument(
        "--comment",
        action="store",
        default="",
        required=False,
        help="Comment for the database entries.\n"
        "Long comments that include spaces must be surounded by '' ",
    )
    # NOTE: The identifier is required for the process_result_file function but the requirement is
    # hanlded afterwards. To allow control of input. Then it is not required in the parser.
    parser.add_argument(
        "--identifier",
        required=False,
        help="Either the sample_identifier or the pair identifier.\n"
        "   - sample_identifier: the sample identifier (for results of type json).\n"
        "   - The pair identifier for any other result type.",
    )
    parser.add_argument(
        "--result_file",
        required=False,
        help="result file path.",
    )

    args = parser.parse_args()
    # !SECTION

    # SECTION : Check if required arguments are provided
    if not all(
        [
            args.identifier,
            args.result_file,
        ]
    ):
        error_message = "Error: Missing required arguments. Use --help for details."
        log_message(error_message, logging.ERROR)
        parser.exit(
            1,
            error_message,
        )

    # !SECTION

    # SECTION : Handling of examples
    if args.example:
        info_message = "Example usage:"
        info_message += f"\t\t python {script_name} --database my_database.sqlite --comment 'Analysis on 2023-10-01' --identifier sample123 --result_file file.json"
        log_message(info_message, logging.INFO, exit_code=0)

    # !SECTION

    # Processing info:
    info_message = processing_result_message(
        script_name, args.result_file, args.identifier
    )
    log_message(info_message, logging.INFO)

    # !SECTION

    # SECTION : Process result files
    try:
        db_conn = sqlite3.connect(args.database)
        process_result_file(args.result_file, args.identifier, db_conn, args.comment)
        db_conn.close()

        log_message(
            f"Successfully processed file: {args.result_file} for identifier: {args.identifier}",
            logging.INFO,
        )

    except FileNotFoundError:
        error_message = f"Input file not found: {args.file_result_file}"
        log_message(error_message, logging.ERROR, exit_code=1)

    except Exception as e:
        # Need to handle the exception and rollback the transaction
        if db_conn:
            db_conn.rollback()

        error_message = processing_error_message(
            script_name, args.result_file, identifier=args.identifier, e=e
        )
        log_message(error_message, logging.ERROR, exit_code=1)
    # !SECTION
