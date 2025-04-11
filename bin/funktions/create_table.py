#!/usr/bin/env python
# SECTION : Imports
import argparse
import os
import sys

import sqlite3
import pandas # type: ignore
from .error_template import log_message, processing_error_message, processing_result_message
#!SECTION

# SECTION : Functions definitions
def create_table(df : pandas.DataFrame, table_name, identifier, file_path, db_file):
    """
    Creates or appends data to a SQLite table, using 'identifier' as the primary key,
    adding missing columns if necessary, and checking for existing data before inserting.

    Args:
        df (pd.DataFrame): DataFrame to insert.
        table_name (str): Name of the table. When argument is passed, must be between "" and not ''
        identifier (str): The identifier (pair or sample_id) - solely used for error messages.
        file_path (str): The name of the processed file.
        db_file (str): Path to the SQLite database file.
    """
    # script name and info
    script_name = os.path.basename(__file__)
    
    info_message = processing_result_message(script_name, file_path)
    print(info_message)
    log_message(info_message, script_name)
    
    db_conn = None
    
    try:
        # NOTE: creates the db it if does not exists
        db_conn = sqlite3.connect(db_file)
        cursor = db_conn.cursor()

        # Create a copy of the DataFrame *without* 'file_path' for insertion
        df_to_insert = df.copy().drop(columns=["file_path"], errors="ignore")

        if df_to_insert.empty:
                    warning_message = f"Warning: Input DataFrame is empty for {identifier} and file {file_path}. No table will be created."
                    print(warning_message)
                    sys.exit(1)


        # NOTE : the table does not exist yet (empty connection) - it must be created
        cursor.execute(
            f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
        )
        columns = ", ".join(f"{col} TEXT" for col in df_to_insert.columns)
        columns_with_filename = f"file_path TEXT, {columns}"

        cursor.execute(f"CREATE TABLE {table_name} ({columns_with_filename})")
        print(f"Table '{table_name}' created.")

        # NOTE : there is no need to check for duplicates. All data is new
        # Insert data, checking for duplicates across all data columns
        placeholders = ", ".join("?" for _ in df_to_insert.columns)

        for row in df_to_insert.itertuples(index=False):
            row_values = list(row)
            insert_query = f"INSERT INTO {table_name} VALUES (?, {placeholders})"
            cursor.execute(insert_query,(file_path, *row_values),)

        cursor.close()

    except Exception as e:
        error_message = processing_error_message(script_name, file_path, identifier, e)
        print(error_message)        
        if db_conn:
            db_conn.rollback()
        log_message(error_message, script_name, exit_code=1)
            
        
    finally:
        if db_conn:
            db_conn.commit()
            cursor = db_conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
            cursor.close()
            db_conn.close()
            
            if row_count == 0:
                error_message = f"Error: Table '{table_name}' in '{db_file}' is empty after processing '{file_path}' for '{identifier}'."
                log_message(error_message, script_name, exit_code=1)

        message_info = f"create_or_append_table function has run for {identifier} and filename {file_path}."
        log_message(message_info, script_name)
#!SECTION

# SECTION MAIN
if __name__ == "__main__":
    script_name = os.path.basename(__file__) 
    # SECTION : Argument parsing
    parser = argparse.ArgumentParser(description="Create a table in a sqlite database and add results from a Pandas dataframe.",)
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
    parser.add_argument("--input_csv", required=True, help="Path of the dataframe that from which results will be appened to the database\n"
                                                            "Note that the function uses a pandas dataframe object, which must have been created\n"
                                                            "beforehand and passed to the function")
    parser.add_argument("--file_path", required=False, default="dummy", help="Name of the processed file which lead to the table (only for documentation purposes in main).")
    parser.add_argument("--db_file", required=True, help="Path to a sqlite dabase. If database does not exists it will be created")
    parser.add_argument("--table_name", required=True, help="Name of the table to be created. Depends on data type.")
    parser.add_argument("--identifier", required=True, help="Identifier for the data")

    args = parser.parse_args()
    # !SECTION

    # SECTION : Check if required arguments are provided
    if not all([args.input_csv, args.db_file, args.table_name, args.identifier,]):
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
    info_message = processing_result_message(
            script_name,
            args.file_path
            )
    log_message(info_message, script_name)
    
    try:
        # # NOTE need to create the pandas dataframe from the file and the database connection
        # Load the Pandas DataFrame (replace with your actual data loading method)
        try:
            df = pandas.read_csv(args.input_csv)
            create_table(df, args.table_name, args.identifier, args.file_path,args.db_file)
        
        except FileNotFoundError:
            error_message = f"Input file not found: {args.file_path}"
            log_message(error_message, script_name, exit_code=1)

    except Exception as e:
        error_message = processing_error_message(
            script_name, 
            args.file_path, 
            identifier = None, 
            e = e)
        log_message(error_message, script_name, exit_code=1)
    # !SECTION
# !SECTION