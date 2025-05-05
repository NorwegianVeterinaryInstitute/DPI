#!/usr/bin/env python
# Made by gemini 2025-04-10
# Debugged and improved by gemini and Eve Fiskebeck 2025-05-01


# SECTION : IMPORTS
import sys
import os

# import logging
import sqlite3
import argparse
# import datetime

# --- Add script's directory to sys.path ---
# To be able to import local modules
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)
# --- End sys.path modification ---

from funktions.error_template import (
    log_message,
    processing_error_message,
    processing_result_message,
)

# !SECTION


# SECTION : FUNCTION Merging datase
def merge_databases(output_db_path, input_list_file):
    """Merges multiple SQLite databases into a single output database,
    handling schema evolution and preventing duplicate rows by checking the
    'file_name' of the first row of each input database's tables.

    Args:
        output_db_path (str): Path to the output SQLite database.
        input_list_file (str): Path to a text file containing a list of input SQLite database paths.
    """

    # script name and info
    script_name = os.path.basename(__file__)

    info_message = f"Starting merge process for output: {output_db_path}"
    log_message(info_message, script_name)

    try:
        if not input_list_file:
            warning_message = "No input text file containing the list paths of databases to process is provided."
        # Read the list of input database file paths from the input file
        try:
            with open(input_list_file, "r") as f:
                input_db_paths_list = [line.strip() for line in f if line.strip()]
            log_message(
                f"Read {len(input_db_paths_list)} database paths from {input_list_file}",
                script_name,
            )
        except FileNotFoundError:
            error_message = f"Error: Input list file not found at {input_list_file}"
            log_message(error_message, script_name, exit_code=1)

        # If found but empty
        if not input_db_paths_list:
            warning_message = (
                f"Input list file '{input_list_file}' is empty. No databases to merge."
            )
            log_message(warning_message, script_name, exit_code=1)

        info_message = f"""
        Output database: {output_db_path}")
        Processing {len(input_db_paths_list)} 
        input databases listed in {input_list_file}.
        """
        log_message(info_message, script_name)

        # Connect to the output database (creates if it doesn't exist)
        with sqlite3.connect(output_db_path) as output_conn:
            output_conn.row_factory = sqlite3.Row  # Access columns by name
            output_cursor = output_conn.cursor()

            # Keep track of tables already created in the output DB
            created_tables = set()

            for i, input_db_path in enumerate(input_db_paths_list):
                info_message = f"Processing input database {i + 1}/{len(input_db_paths_list)}: {input_db_path}"
                log_message(info_message, script_name)

                # --- Add Debug Print ---
                debug_message = f"Attempting to attach database path: '{input_db_path}'"
                log_message(debug_message, script_name)

                if not os.path.exists(input_db_path):
                    error_message = (
                        f"Warning: Input database {input_db_path} not found. Skipping."
                    )
                    log_message(error_message, script_name, exit_code=1)
                    # Important to make fail OR nextflow process will continue to run.
                    # And it wont be possible to resume.

                try:
                    # Attach the current input database
                    # Use a unique alias for each attached database
                    attach_alias = f"input_db_{i}"
                    output_cursor.execute(
                        f"ATTACH DATABASE ? AS {attach_alias};", (input_db_path,)
                    )
                    info_message = f"Attached {input_db_path} as {attach_alias}"
                    log_message(info_message, script_name)

                    # Get list of tables from the attached database
                    output_cursor.execute(
                        f"SELECT name FROM {attach_alias}.sqlite_master WHERE type='table';"
                    )
                    input_tables = [row["name"] for row in output_cursor.fetchall()]

                    for table_name in input_tables:
                        if table_name.startswith(
                            "sqlite_"
                        ):  # Skip SQLite internal tables
                            continue

                        info_message = f"  Processing table: {table_name}"
                        log_message(info_message, script_name)

                        # Get column information from the input table (via attached db)
                        output_cursor.execute(
                            f"PRAGMA {attach_alias}.table_info({table_name})"
                        )
                        input_columns = {
                            row["name"]: row["type"] for row in output_cursor.fetchall()
                        }
                        input_column_names = list(input_columns.keys())

                        # Check if the table exists in the main output database
                        output_cursor.execute(
                            "SELECT name FROM main.sqlite_master WHERE type='table' AND name=?;",
                            (table_name,),
                        )
                        output_table_exists = output_cursor.fetchone()

                        if not output_table_exists:
                            # Create the table in the output database using the structure from the input
                            # Fetch column structure from input table
                            output_cursor.execute(
                                f"SELECT * FROM {attach_alias}.{table_name} LIMIT 0"
                            )

                            col_defs = []
                            if (
                                output_cursor.description
                            ):  # Check if description is available
                                for desc in output_cursor.description:
                                    col_name = desc[0]
                                    # Basic type inference (can be improved if needed)
                                    col_type = "TEXT"  # Default to TEXT
                                    col_defs.append(f'"{col_name}" {col_type}')
                                create_table_sql = f'CREATE TABLE main."{table_name}" ({", ".join(col_defs)});'
                                output_cursor.execute(create_table_sql)
                                output_conn.commit()
                                info_message = f"  Created table '{table_name}' in output database."
                                log_message(info_message, script_name)
                                created_tables.add(table_name)
                            else:
                                # Fallback or error if description is None after SELECT LIMIT 0
                                warning_message = f"  Warning: Could not determine columns for new table '{table_name}'. Skipping creation."
                                log_message(warning_message, script_name)
                                continue  # Skip to next table

                        else:
                            # Add missing columns to the output table if needed
                            output_cursor.execute(
                                f'PRAGMA main.table_info("{table_name}")'
                            )
                            output_columns = {
                                row["name"]: row["type"]
                                for row in output_cursor.fetchall()
                            }
                            # output_column_names = list(output_columns.keys())
                            columns_to_add = set(input_columns.keys()) - set(
                                output_columns.keys()
                            )
                            for col_to_add in columns_to_add:
                                # Determine type from input if possible, default to TEXT
                                col_type = input_columns.get(col_to_add, "TEXT")
                                alter_table_sql = f'ALTER TABLE main."{table_name}" ADD COLUMN "{col_to_add}" {col_type};'
                                output_cursor.execute(alter_table_sql)
                                output_conn.commit()
                                info_message = f"  Added column '{col_to_add}' to table '{table_name}' in output database."
                                log_message(info_message, script_name)
                                # output_column_names.append(col_to_add) # Update output column names

                        # --- Get definitive output column names AFTER creation/alteration ---
                        output_cursor.execute(f'PRAGMA main.table_info("{table_name}")')
                        output_column_names = [
                            row["name"] for row in output_cursor.fetchall()
                        ]
                        if not output_column_names:
                            warning_message = f"  Warning: Could not retrieve columns for output table '{table_name}' after creation/alteration. Skipping insertion."
                            log_message(warning_message, script_name)
                            continue  # Skip insertion for this table

                        # --- Duplicate Checking Logic ---
                        # NOTE - The logic has been simplified - if not ok see commit id 144b6de9ccfcd049d8da96292f842cc200f80f06
                        # Fetch the first row from the input table to get the 'file_name' (or 'file_path')
                        # Prefer 'file_path' if it exists, otherwise 'file_name'
                        id_col_name = None
                        if "file_path" in input_column_names:
                            id_col_name = "file_path"
                        elif "file_name" in input_column_names:
                            id_col_name = "file_name"

                        file_identifier_value = None
                        if id_col_name:
                            output_cursor.execute(
                                f'SELECT "{id_col_name}" FROM {attach_alias}."{table_name}" LIMIT 1'
                            )
                            first_input_row = output_cursor.fetchone()
                            if first_input_row:
                                file_identifier_value = first_input_row[id_col_name]

                        # Check if data from this specific file identifier already exists
                        existing_data_for_file = False
                        if id_col_name and file_identifier_value is not None:
                            output_cursor.execute(
                                f'SELECT 1 FROM main."{table_name}" WHERE "{id_col_name}" = ? LIMIT 1',
                                (file_identifier_value,),
                            )
                            if output_cursor.fetchone():
                                existing_data_for_file = True
                                info_message = f"    Data for identifier '{file_identifier_value}' already exists in table '{table_name}'. Skipping insertion for this file."
                                log_message(info_message, script_name)

                        # If no data for this file exists, insert all rows
                        if not existing_data_for_file:
                            # Ensure columns match between input and output for insertion
                            common_columns = [
                                col
                                for col in input_column_names
                                if col in output_column_names
                            ]
                            common_columns_quoted = [
                                f'"{col}"' for col in common_columns
                            ]
                            common_columns_str = ", ".join(common_columns_quoted)

                            insert_sql = f'INSERT INTO main."{table_name}" ({common_columns_str}) SELECT {common_columns_str} FROM {attach_alias}."{table_name}";'
                            output_cursor.execute(insert_sql)
                            inserted_count = output_cursor.rowcount
                            output_conn.commit()
                            info_message = f"    Inserted {inserted_count} rows into table '{table_name}' from {input_db_path} (based on unique '{id_col_name}')."

                    # Detach the database
                    output_cursor.execute(f"DETACH DATABASE {attach_alias};")
                    info_message = f"Detached {attach_alias}"
                    log_message(info_message, script_name)

                except sqlite3.Error as e:
                    error_message = (
                        f"SQLite error while processing {input_db_path}: {e}"
                    )
                    log_message(error_message, script_name)
                    output_conn.rollback()  # Rollback changes made for this input DB
                except Exception as e:
                    error_message = f"Unexpected error processing {input_db_path}: {e}"
                    log_message(error_message, script_name)
                    output_conn.rollback()

        info_message = f"Successfully finished merging databases into: {output_db_path}"
        log_message(info_message, script_name)

    except FileNotFoundError:  # Catch specific error for list file
        error_message = f"Error: Input list file not found at {input_list_file}"
        log_message(error_message, script_name, exit_code=1)
    except sqlite3.Error as e:
        error_message = f"SQLite error with output database {output_db_path}: {e}"
        log_message(error_message, script_name, exit_code=1)
    except Exception as e:
        error_message = f"An unexpected error occurred: {e}"
        log_message(error_message, script_name, exit_code=1)


# !SECTION


# SECTION MAIN
if __name__ == "__main__":
    script_name = os.path.basename(__file__)
    # SECTION : Argument parsing
    parser = argparse.ArgumentParser(
        prog=script_name,
        description="Merge multiple SQLite databases, checking for duplicates based on 'file_path' or 'file_name'.",
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
        version="%(prog)s 0.0.3",  # Incremented version
        help="Print the script version and exit.",
    )
    # Required arguments
    parser.add_argument(
        "--output",
        required=True,
        help="Path to the output SQLite database.",
    )
    parser.add_argument(
        "--input",  # Changed from --input
        required=True,
        help="Path to a text file containing the list of input SQLite database files (one path per line).",
    )

    args = parser.parse_args()
    # !SECTION

    # SECTION : Check if required arguments are provided
    if not all([args.output, args.input]):  # Check args.input
        parser.error(
            "The following arguments are required: --output <output_db_path> --inputs <input_list_file>.\n"
        )
        sys.exit(1)
    # !SECTION

    # SECTION : Handling of example
    if args.example:
        info_message = "Example usage:"
        info_message += (
            f"python {script_name} --output merged.sqlite --input list_input_dbs.txt"
        )
        log_message(info_message, script_name, exit_code=0)
    # !SECTION

    # NOTE: Logging setup could be moved here from the function
    # logging.basicConfig(...)

    # SECTION : SCRIPT : Merge the result files
    # NOTE : this became somewhat uselless
    info_message = processing_result_message(script_name, f"list file : {args.input}")
    log_message(info_message, script_name)

    try:
        merge_databases(args.output, args.input)  # Pass args.input
        info_message = f"Script {script_name} ran successfully"
        # log_message(info, script_name, exit_code=1) # This was logging 'info' which is not defined, and exiting on success
        log_message(info_message, script_name)  # Log success message

    # except FileNotFoundError: # This is less likely now as we check existence inside the function
    #     error_message = f"One of the input file was not found: {args.input}"
    #     log_message(error_message, script_name, exit_code=1)
    except Exception as e:
        error_message = processing_error_message(
            script_name, f"Input list file: {args.input}", identifier=None, e=e
        )
        log_message(error_message, script_name, exit_code=1)
    # !SECTION

# !SECTION
