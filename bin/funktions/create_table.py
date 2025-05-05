#!/usr/bin/env python
# SECTION : Imports
import argparse
import os
import re
import sys

import sqlite3
import pandas  # type: ignore
from .error_template import (
    log_message,
    processing_error_message,
    processing_result_message,
)
#!SECTION


# SECTION : Functions definitions
def create_table(
    df: pandas.DataFrame, table_name, identifier, file_path, db_conn: sqlite3.Connection
):
    """
    Creates or appends data to a SQLite table using an existing connection.
    Checks if table exists, creates if not. Adds missing columns if necessary.
    Inserts data from the DataFrame, adding a 'file_path' column.

    Args:
        df (pandas.DataFrame): DataFrame to insert.
        table_name (str): Name of the table. When argument is passed, must be between "" and not ''
        identifier (str): The identifier (pair or sample_id) - solely used for error messages.
        file_path (str): Path of the source file (added as a column).
        db_conn (sqlite3.Connection): An active SQLite database connection object.
    """
    # script name and info
    script_name = os.path.basename(__file__)

    info_message = processing_result_message(script_name, file_path)
    print(info_message)
    log_message(info_message, script_name)

    # Case empty or None
    try:
        df_to_insert = df.copy().drop(columns=["file_path"], errors="ignore")

        # Use the passed connection object directly
        # --- Debugging Start (Optional: Remove after fixing) ---
        print(f"DEBUG create_table: Received db_conn type: {type(db_conn)}")
        print(f"DEBUG create_table: Received db_conn value: {repr(db_conn)}")
        # --- Debugging End ---

        # connect to the database
        cursor = db_conn.cursor()

        # Create a copy of the DataFrame *without* 'file_path' for insertion
        cursor.execute(
            f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
        )
        table_exists = cursor.fetchone()

        df_columns = ["file_path"] + list(df_to_insert.columns)  # Include file_path

        # HERE INSERT
        if not table_exists:
            columns_sql = ", ".join(
                f'"{col}" TEXT' for col in df_columns
            )  # Quote column names
            create_sql = f'CREATE TABLE IF NOT EXISTS "{table_name}" ({columns_sql})'  # Use IF NOT EXISTS
            cursor.execute(create_sql)
            print(f"Table '{table_name}' ensured/created in database.")
            log_message(
                f"Table '{table_name}' ensured/created in database.", script_name
            )
        else:
            # Table exists, check for missing columns
            cursor.execute(f'PRAGMA table_info("{table_name}")')
            existing_columns = [row[1] for row in cursor.fetchall()]
            missing_columns = set(df_columns) - set(existing_columns)

            for col in missing_columns:
                try:
                    alter_sql = f'ALTER TABLE "{table_name}" ADD COLUMN "{col}" TEXT'
                    cursor.execute(alter_sql)
                    print(f"Added missing column '{col}' to table '{table_name}'.")
                    log_message(
                        f"Added missing column '{col}' to table '{table_name}'.",
                        script_name,
                    )
                except sqlite3.OperationalError as alter_e:
                    error_message = f"Failed to add column '{col}' to table '{table_name}': {alter_e}"
                    print(error_message)
                    log_message(
                        error_message, script_name, exit_code=1
                    )  # Exit if schema update fails

        # NOTE : there is no need to check for duplicates. All data is new
        # Insert data
        # Prepare insert statement with placeholders for all expected columns
        placeholders = ", ".join("?" for _ in df_columns)

        # Construct the column names string separately to avoid f-string quote issues
        quoted_columns_str = ", ".join(f'"{col}"' for col in df_columns)
        insert_sql = (
            f'INSERT INTO "{table_name}" ({quoted_columns_str}) VALUES ({placeholders})'
        )

        # Prepare data rows including the file_path
        rows_to_insert = []
        for row in df_to_insert.itertuples(index=False):
            rows_to_insert.append((file_path,) + tuple(row))  # Prepend file_path

        cursor.executemany(insert_sql, rows_to_insert)
        db_conn.commit()  # Commit the changes using the passed connection

        message_info = f"Successfully inserted {len(rows_to_insert)} rows into table '{table_name}' for identifier '{identifier}' from file '{file_path}'."
        log_message(message_info, script_name)

        # Close the cursor, but NOT the connection
        cursor.close()

    # Close the cursor, but NOT the connection
    except (sqlite3.Error, Exception) as e:  # Catch SQLite and other errors
        # allow some df/gff to be empty
        if (df is None or df.empty) and ("query_additional" in file_path):
            warning_message = f"Warning: Input DataFrame is empty for {identifier} and file {file_path}. No table will be created."
            log_message(warning_message, script_name, exit_code=0)
            return None

        else:
            error_message = processing_error_message(
                script_name, file_path, identifier, e
            )
            log_message(warning_message, script_name, exit_code=1)

    finally:
        message_info = f"create_or_append_table function has run for {identifier} and filename {file_path}."
        log_message(message_info, script_name)


#!SECTION

# SECTION MAIN
if __name__ == "__main__":
    script_name = os.path.basename(__file__)
    # SECTION : Argument parsing
    parser = argparse.ArgumentParser(
        description="Create a table in a sqlite database and add results from a Pandas dataframe.",
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
        "--input_csv",
        required=True,
        help="Path of the dataframe that from which results will be appened to the database\n"
        "Note that the function uses a pandas dataframe object, which must have been created\n"
        "beforehand and passed to the function",
    )
    parser.add_argument(
        "--file_path",
        required=False,
        default="dummy",
        help="Name of the processed file which lead to the table (only for documentation purposes in main).",
    )
    parser.add_argument(
        "--db_file",
        required=True,
        help="Path to a sqlite dabase. If database does not exists it will be created",
    )
    parser.add_argument(
        "--table_name",
        required=True,
        help="Name of the table to be created. Depends on data type.",
    )
    parser.add_argument("--identifier", required=True, help="Identifier for the data")

    args = parser.parse_args()
    # !SECTION

    # SECTION : Check if required arguments are provided
    if not all(
        [
            args.input_csv,
            args.db_file,
            args.table_name,
            args.identifier,
        ]
    ):
        parser.error(
            "The following arguments are required: --input_csv --db_cfile, --table_name, --identifier, "
        )
        sys.exit(1)
    # !SECTION

    # SECTION : Handling of example
    if args.example:
        info_message = "Example usage:"
        info_message += f"python {script_name} --input_csv <path_to_file> --db_file <db_file> --table_name <table_name> --identifier <identifier>"
        log_message(info_message, script_name, exit_code=0)
    # !SECTION
    # NOTE:  Login info output - handled by log_error

    # SECTION : SCRIPT : Load data and insert into the database
    info_message = processing_result_message(script_name, args.file_path)
    log_message(info_message, script_name)

    # # NOTE need to create the pandas dataframe from the file and the database connection
    # Load the Pandas DataFrame (replace with your actual data loading method)
    try:
        df = pandas.read_csv(args.input_csv)

        standalone_conn = sqlite3.connect(args.db_file)
        # Pass the connection object to the function
        create_table(
            df,
            args.table_name,
            args.identifier,
            args.file_path,
            standalone_conn,
        )

        if standalone_conn:
            standalone_conn.close()  # Ensure connection is closed

    except FileNotFoundError:
        error_message = f"Input file not found: {args.file_path}"
        log_message(error_message, script_name, exit_code=1)

    except Exception as e:
        error_message = processing_error_message(
            script_name, args.file_path, identifier=None, e=e
        )
        log_message(error_message, script_name, exit_code=0)

    # Other errors will be taken into account by the function
    # !SECTION
# !SECTION
