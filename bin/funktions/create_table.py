#!/usr/bin/env python
# SECTION : Imports
import argparse
import datetime
import sys
import logging

import sqlite3
import pandas # type: ignore
#!SECTION

# SECTION : Functions definitions
def create_table(df : pandas.DataFrame, table_name, identifier, file_name, db_file):
    """
    Creates or appends data to a SQLite table, using 'identifier' as the primary key,
    adding missing columns if necessary, and checking for existing data before inserting.

    Args:
        df (pd.DataFrame): DataFrame to insert.
        table_name (str): Name of the table. When argument is passed, must be between "" and not ''
        identifier (str): The identifier (pair or sample_id) - solely used for error messages.
        file_name (str): The name of the processed file.
        db_file (str): Path to the SQLite database file.
    """
    try:
        # NOTE: creates the db it if does not exists
        db_conn = sqlite3.connect(db_file)
        cursor = db_conn.cursor()
                
        # Create a copy of the DataFrame *without* 'file_name' for insertion
        df_to_insert = df.copy().drop(columns=["file_name"], errors="ignore")

        # NOTE : the table does not exist yet (empty connection) - it must be created
        cursor.execute(
            f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
        )
        columns = ", ".join(f"{col} TEXT" for col in df_to_insert.columns)
        columns_with_filename = f"file_name TEXT, {columns}"
        
        cursor.execute(f"CREATE TABLE {table_name} ({columns_with_filename})")
        print(f"Table '{table_name}' created.")

        # NOTE : there is no need to check for duplicates. All data is new
        # Insert data, checking for duplicates across all data columns
        placeholders = ", ".join("?" for _ in df_to_insert.columns)
        
        for row in df_to_insert.itertuples(index=False):
            row_values = list(row)
            insert_query = f"INSERT INTO {table_name} VALUES (?, {placeholders})"
            cursor.execute(insert_query,(file_name, *row_values),)
            
        cursor.close()
        
    except Exception as e:
        print(f"Error processing {file_name} for identifier {identifier}: {e}")
        if 'db_conn' in locals():
            db_conn.rollback()
    finally:
        if 'db_conn' in locals():
            db_conn.commit()
            db_conn.close()
            
    print(f"create_or_append_table function has run for {identifier} and filename {file_name}.")
#!SECTION

# SECTION MAIN
if __name__ == "__main__":
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
    parser.add_argument("--file_name", required=False, default="dummy", help="Name of the processed file which lead to the table (only for documentation purposes in main).")
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
        logging.info("Example usage:")
        logging.info("python create_table.py --input_csv <path_to_file> --db_file <db_file> --table_name <table_name> --identifier <identifier>")
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
    
# SECTION : SCRIPT : Load data and insert into the database
    try:
        logging.info(f"Processing table '{args.table_name}' for identifier '{args.identifier}' from file '{args.input_csv}' into database '{args.db_file}'.")
        
        # # NOTE need to create the pandas dataframe from the file and the database connection
        # Load the Pandas DataFrame (replace with your actual data loading method)
        try:
            df = pandas.read_csv(args.input_csv)
        except FileNotFoundError:
            logging.error(f"Input CSV file not found: {args.input_csv}")
            sys.exit(1)

        create_table(df, args.table_name, args.identifier, args.file_name,args.db_file)
        logging.info("create_table.py script completed successfully.")
    except Exception as e:
        logging.error(f"An error occurred during the script execution: {e}")
        logging.error(f"Check {log_file_name} for more details.")
    # !SECTION
# !SECTION