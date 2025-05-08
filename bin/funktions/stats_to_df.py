#!/usr/bin/env python
# SECTION : Imports
import argparse
import logging
import os
# import sys

import pandas as pd  # type: ignore

from .error_template import (
    setup_logger,
    log_message,
    processing_error_message,
    processing_result_message,
)

# !SECTION


# SECTION : Functions definitions
def stats_to_df(file_path):
    """
    transforms stat file to pandas df. Appends query and ref names
    :param file_path nucdiff result ref_query_stats.out
    :return df (long format)
    """
    # script name
    script_name = os.path.basename(__file__)

    info_message = processing_result_message(script_name, file_path)
    log_message(info_message, logging.INFO)

    # script
    try:
        df = pd.read_table(
            file_path,
            sep="\t",
            header=None,
            names=["param", "value"],
            skip_blank_lines=True,
            index_col=None,
        )

    except Exception as e:
        error_message = f"Error reading stats_out file {file_path}: {e}"
        log_message(error_message, logging.ERROR, exit_code=1)

    try:
        # Extract the ref and query ids from the file name
        file_name = os.path.basename(file_path)
        parts = file_name.split("_")
        ref, query = parts[0], parts[1]

        # lines with empty info
        df = df[df.value.notnull()].assign(_REF=ref, _QUERY=query)

        # eg. prevents read/write errors
        if df.empty:
            warning_message = "Warning: the table 'stats' is empty"
            warning_message += "Check the stats_out file.\n"
            log_message(warning_message, logging.WARNING, exit_code=1)

        return df

    except Exception as e:
        error_message = processing_error_message(
            script_name, file_path, identifier=None, e=e
        )
        log_message(error_message, logging.ERROR, exit_code=1)


#!SECTION


# SECTION MAIN
if __name__ == "__main__":
    script_name = os.path.basename(__file__)
    logger_instance, log_file_name_used = setup_logger(script_name)

    # SECTION : Argument parsing
    parser = argparse.ArgumentParser(
        description="Process stat_file created by nucdiff and export as csv files.",
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

    # required arguments (only for main)
    parser.add_argument(
        "--file_path",
        required=True,
        help="Path of the file that will be transformed into a pandas dataframe\n",
    )
    parser.add_argument(
        "--identifier",
        required=True,
        help="Identifier for the data. Only required for script, to allow throwing erros",
    )

    args = parser.parse_args()
    # !SECTION

    # SECTION : Check if required arguments are provided
    if not all(
        [
            args.file_path,
            args.identifier,
        ]
    ):
        error_message = "Error: Missing required arguments. Use --help for details."
        log_message(error_message, logging.ERROR)
        parser.exit(
            1,
            error_message,
        )

    # !SECTION

    # SECTION : Handling of example
    if args.example:
        info_message = "Example usage:"
        info_message += f"\t\t python {script_name} --file_path <path_to_file> --identifier <identifier>"
        log_message(info_message, logging.INFO, exit_code=0)

    # !SECTION

    # NOTE:  Login info output - handled by log_error

    # SECTION : SCRIPT : Load data and insert into the database
    # Processing info:
    info_message = processing_result_message(script_name, args.file_path)
    log_message(info_message, logging.INFO)

    try:
        df = stats_to_df(args.file_path)
        current_working_directory = os.getcwd()
        df.to_csv(
            os.path.join(current_working_directory, f"{args.identifier}_stats.csv"),
            index=False,
            header=True,
        )

        info_message = f"\t\t{script_name} completed successfully.\n\n"
        info_message += f"DataFrame saved as CSV files in {current_working_directory}."
        log_message(
            f"Successfully processed file: {args.file_path} for identifier: {args.identifier}",
            logging.INFO,
        )

    except FileNotFoundError:
        error_message = f"Input file not found: {args.file_path}"
        log_message(error_message, logging.ERROR, exit_code=1)

    except Exception as e:
        error_message = processing_error_message(
            script_name, args.file_path, args.identifier, e=e
        )
        log_message(error_message, logging.ERROR, exit_code=1)
    # !SECTION
# !SECTION
