#!/usr/bin/env python
# SECTION : Imports
import argparse
import datetime
import sys
import sqlite3
import pandas as pd
import logging
#!SECTION

# SECTION : Functions definitions
def create_table(df : pd.DataFrame, table_name, identifier, file_name, db_conn):
    """
    Creates or appends data to a SQLite table, using 'identifier' as the primary key,
    adding missing columns if necessary, and checking for existing data before inserting.

    Args:
        df (pd.DataFrame): DataFrame to insert.
        table_name (str): Name of the table. When argument is passed, must be between "" and not ''
        identifier (str): The identifier (pair or sample_id).
        file_name (str): The name of the processed file.
        db_conn (sqlite3.Connection): The database connection.
    """    
    cursor = db_conn.cursor()

    # Insert identifier with a different name
    df.insert(0, "nf_val_identifier", identifier)

    # Create a copy of the DataFrame *without* 'file_name' for checking duplicates and insertion
    df_to_insert = df.copy().drop(columns=["file_name"], errors="ignore")

    # Check if table exists
    cursor.execute(
        f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
    )
    table_exists = cursor.fetchone()

    if not table_exists:
        # Create table
        columns = ", ".join(f"{col} TEXT" for col in df_to_insert.columns)
        columns_with_filename = f"file_name TEXT, {columns}"
        cursor.execute(f"CREATE TABLE {table_name} ({columns_with_filename})")
        print(f"Table '{table_name}' created.")
    else:
        # Check and add missing columns
        cursor.execute(f"PRAGMA table_info({table_name})")
        existing_cols = [row[1] for row in cursor.fetchall()]
        missing_cols = [col for col in df_to_insert.columns if col not in existing_cols]

        for col in missing_cols:
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {col} TEXT")
            cursor.execute(f"UPDATE {table_name} SET {col} = NULL")
        print(f"Table '{table_name}' already exists, columns added if needed.")

    # FIXME : if to heavy to check database : implement option to skip check duplicates
    # and do a deduplication after on the whole database - this might be faster
    # or optimize in another way

    # Insert data, checking for duplicates across all data columns
    placeholders = ", ".join("?" for _ in df_to_insert.columns)
    # FIXME : continue here !!! see error message
    for row in df_to_insert.itertuples(index=False):
        row_values = list(row)
        where_clause = " AND ".join(f"{col} = ?" for col in df_to_insert.columns)
        select_query = f"SELECT 1 FROM {table_name} WHERE {where_clause}"

        try:
            cursor.execute(select_query, tuple(row_values))
            exists = cursor.fetchone()
        except sqlite3.Error as e:
            exists = None  # Handle the error and continue

        if not exists:
            insert_query = f"INSERT INTO {table_name} VALUES (?, {placeholders})"

            cursor.execute(
                insert_query,
                (file_name, *row_values),
            )
            print(f"Data inserted into '{table_name}'.")
        else:
            print(f"Skipping duplicate row in file {file_name}")

    # log function
    print(f"create_or_append_table function has run for {identifier} and filename {file_name}.")

    cursor.close()
#!SECTION

# SECTION MAIN
if __name__ == "__main__":
    # SECTION : Argument parsing
    parser = argparse.ArgumentParser(description="Create a table in a sqlite database and add results from a Pandas dataframe.",)
    parser.add_argument("--table_name", required=True, help="Name of the table to be created. Depends on data type.",)
    parser.add_argument("--identifier", required=True, help="Identifier for the data",)
    parser.add_argument("--file_name", required=True, help="Path of the result file from which results will be appened to the dataframe",)
    parser.add_argument("--db_conn", required=True, help="A sqlite connection",)

    args = parser.parse_args()
    # !SECTION
    
    # SECTION : Check if required arguments are provided
    if not all([args.table_name, args.identifier, args.file_name, args.db_conn]):
        parser.error(
            "The following arguments are required: --table_name, --identifier, --file_name, --db_conn"
        )
        sys.exit(1)      
    # !SECTION
    
    # SECTION : Handling of example
    if args.example:
        logging.info("Example usage:")
        logging.info("python create_table.py --table_name <table_name> --identifier <identifier> --file_name <file_name> --db_conn <db_conn>")
    # !SECTION
    

    # SECTION : Login info output
    log_file_name = f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_create_table.log"

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file_name, mode="w"),
            logging.StreamHandler(sys.stdout),
        ],
        )
    # !SECTION
    
    # SECTION : SCRIPT : Merge the result files
    try:
        logging.info(f"Added table for {args.table_name} and identifier {args.identifier}")
        create_table(args.table_name, args.identifier, args.file_name, args.db_conn)
    except Exception as e:
        logging.error(f"An error occurred during the creation of the table for {args.table_name} and identifier {args.identifier}: {e}")
        logging.error(f"Check {log_file_name} for more details")
    # !SECTION
# !SECTION