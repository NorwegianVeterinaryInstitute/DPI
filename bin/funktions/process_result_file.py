#!/usr/bin/env python
# Wrapper : processing each type of results files. A single file at the time
# Improved with geminis help (2025-04-10)

# SECTION : Imports
import argparse
import logging
import os
import sqlite3

# import sys
import json


from .error_template import (
    setup_logger,
    log_message,
    processing_error_message,
    processing_result_message,
)

from .json_to_df import prep_info_df, prep_features_df, prep_sequences_df
from .gff_to_df import gff_to_df
from .vcf_to_df import vcf_to_df
from .stats_to_df import stats_to_df
from .comment_df import create_comment_df
from .create_table import create_table

# !SECTION


# SECTION : Functions definitions
# NOTE helper
def determine_result_type(file_name):
    """
    Helper: Determines the type of result for correct processing
    Returns the result type

    Args:
        file_name (str): basename of the result file.
    """

    if file_name.endswith(".json"):
        return "json"
    elif file_name.endswith(".gff"):
        return "gff"
    elif file_name.endswith(".vcf"):
        return "vcf"
    elif file_name.endswith("_stat.out"):
        return "stats"
    else:
        return None


def process_result_file(file_path, identifier, db_file, comment):
    """
    Processes a single result file, transforms it into a table
    and inserts it into the specified SQLite database.

    Args:
        file_path (str): Path to the result file.
        identifier (str): The identifier (pair or sample_id).
        db_file (str): Path to the SQLite database file.
        comment (str): Comment for the database entries.
    """
    # script name and info
    script_name = os.path.basename(__file__)

    info_message = processing_result_message(script_name, file_path, identifier)
    log_message(info_message, logging.INFO)

    # script
    # NOTE: defensive programming implemented with each function to create the df ... each level
    try:
        file_name = os.path.basename(file_path)
        result_type = determine_result_type(file_name)

        if result_type == "json":
            with open(file_path, "r") as f:
                data = json.load(f)

            # NOTE: 3 types of data to extract for the json file

            info_df = prep_info_df(data, identifier)
            create_table(info_df, "info", identifier, file_name, db_file)

            features_df = prep_features_df(data, identifier)
            create_table(features_df, "features", identifier, file_name, db_file)

            sequences_df = prep_sequences_df(data, identifier)
            create_table(sequences_df, "sequences", identifier, file_name, db_file)

        # NOTE : processing different types of gff files
        elif result_type == "gff":
            try:
                df = gff_to_df(file_path)  # The potential error point

                if "_query_blocks" in file_name:
                    create_table(df, "query_blocks", identifier, file_name, db_file)
                elif "_query_snps" in file_name:
                    create_table(df, "query_snps", identifier, file_name, db_file)
                elif "_query_struct" in file_name:
                    create_table(df, "query_struct", identifier, file_name, db_file)
                elif "_query_additional" in file_name:
                    create_table(df, "query_additional", identifier, file_name, db_file)
                elif "_query_snps_annotated" in file_name:
                    create_table(
                        df, "query_snps_annotated", identifier, file_name, db_file
                    )
                elif "_ref_blocks" in file_name:
                    create_table(df, "ref_blocks", identifier, file_name, db_file)
                elif "_ref_snps" in file_name:
                    create_table(df, "ref_snps", identifier, file_name, db_file)
                elif "_ref_struct" in file_name:
                    create_table(df, "ref_struct", identifier, file_name, db_file)
                elif "ref_additional" in file_name:
                    create_table(df, "ref_additional", identifier, file_name, db_file)
                else:
                    error_message = f"Warning: Unknown GFF subtype for {result_type} for {identifier}. Filepath {file_path}. Skipping {file_path}."
                    log_message(error_message, logging.WARNING, exit_code=1)
            except TypeError as te:  # Catch the specific error
                error_message = (
                    f"FATAL DEBUG: Caught TypeError when calling gff_to_df in : {te}."
                )
                error_message += f"script executing: {script_name}"
                # do not need to exit here, will be exited by gff_to_df if necesary
                log_message(error_message, logging.ERROR, exit_code=0)

        # NOTE: processing different types of vcf files
        elif result_type == "vcf":
            df = vcf_to_df(file_path)

            if "_ref_snps_annotated" in file_name:
                create_table(df, "ref_snps_annotated", identifier, file_name, db_file)
            elif "_query_snps_annotated" in file_name:
                create_table(df, "query_snps_annotated", identifier, file_name, db_file)
            else:
                error_message = f"Warning: Unknown VCF subtype for {result_type} for {identifier}. Skipping {file_name}."
                log_message(error_message, logging.ERROR, exit_code=1)

        elif result_type == "stats":
            df = stats_to_df(file_path)
            if "_stat.out" in file_name:
                create_table(df, "stat_file", identifier, file_name, db_file)
            else:
                error_message = f"Warning: Unknown stats subtype for {result_type} for {identifier}. Skipping {file_path}."
                log_message(error_message, logging.ERROR, exit_code=1)

        # NOTE : adding comment table for each type of file processed in the database
        comment_df = create_comment_df(identifier, comment)
        create_table(comment_df, "comments", identifier, file_name, db_file)

    except Exception as e:
        error_message = processing_error_message(
            script_name, file_path, identifier=None, e=e
        )
        log_message(error_message, logging.ERROR, exit_code=1)


# !SECTION

# SECTION MAIN
if __name__ == "__main__":
    script_name = os.path.basename(__file__)
    logger_instance, log_file_name_used = setup_logger(script_name)

    # SECTION : Argument parsing
    parser = argparse.ArgumentParser(
        description="Process a result file and add it to an SQLite database.",
    )
    parser.add_argument(
        "--file_path",
        required=True,
        help="Path to the result file",
    )
    parser.add_argument(
        "--identifier",
        required=True,
        help="Identifier for the data",
    )
    parser.add_argument(
        "--db_file",
        required=True,
        help="Path to the SQLite database file",
    )
    parser.add_argument(
        "--comment",
        default="",
        required=False,
        help="Optional comment for the database entry",
    )

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

    args = parser.parse_args()
    # !SECTION

    # SECTION : Check if required arguments are provided
    if not all([args.file_path, args.identifier, args.db_file]):
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

        info_message += f"\t\t python {script_name} --file_path <path_to_file> --identifier <identifier> --db_file <db_file>"
        log_message(info_message, logging.INFO, exit_code=0)

    # Processing info:
    info_message = processing_result_message(
        script_name, args.file_path, args.identifier
    )
    log_message(info_message, logging.INFO)

    # Python environment info
    # python_env_info = f"""
    # --- Python Environment ---
    # sys.executable: {sys.executable}
    # sys.path: {sys.path}
    # PYTHONPATH env var: {os.environ.get("PYTHONPATH", "Not Set")}
    # ---
    # """

    # log_message(python_env_info, logging.DEBUG)

    # !SECTION

    # SECTION : SCRIPT : Merge the result files

    try:
        db_conn = sqlite3.connect(args.db_file)
        process_result_file(args.file_path, args.identifier, db_conn, args.comment)
        db_conn.close()

        log_message(
            f"Successfully processed file: {args.file_path} for identifier: {args.identifier}",
            logging.INFO,
        )
    except FileNotFoundError:
        error_message = f"Input file not found: {args.file_path}"
        log_message(error_message, logging.ERROR, exit_code=1)

    except Exception as e:
        error_message = processing_error_message(
            script_name, args.file_path, identifier=None, e=e
        )
        log_message(error_message, logging.ERROR, exit_code=1)
    # !SECTION
# !SECTION

# NOTE: might still be a bit overkill with all error messages
# reduced somewhat but there are still some redundancies in error messages
