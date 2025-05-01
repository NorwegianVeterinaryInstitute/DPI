#!/usr/bin/env python
# SECTION : Imports
# written by gemini - 2025-05-01
import sqlite3
import sys
import os
import pandas as pd
# !SECTION


def export_sqlite_table_to_csv_pandas(db_path, table_name, csv_path):
    """
    Connects to an SQLite database, reads a specified table into a pandas DataFrame,
    and writes the DataFrame to a CSV file.

    Args:
        db_path (str): The path to the SQLite database file.
        table_name (str): The name of the table to export.
        csv_path (str): The path to the output CSV file.
    """
    # Check if the database file exists
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at '{db_path}'")
        sys.exit(1)

    conn = None  # Initialize connection variable
    try:
        # Connect to the SQLite database
        # The connection context manager handles closing automatically
        with sqlite3.connect(db_path) as conn:
            # --- Check if table exists ---
            # Use pandas to check, though a direct cursor check is also fine
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (table_name,))
            if cursor.fetchone() is None:
                print(f"Error: Table '{table_name}' not found in the database '{db_path}'.")
                # Optionally, list available tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                if tables:
                    print("\nAvailable tables:")
                    for table in tables:
                        print(f"- {table[0]}")
                sys.exit(1)

            # --- Read the entire table into a pandas DataFrame ---
            print(f"Reading table '{table_name}' into DataFrame...")
            # Construct the SQL query string safely
            query = f"SELECT * FROM {table_name}" # Basic query, assumes table name is safe
            df = pd.read_sql_query(query, conn)

            # --- Write DataFrame to CSV file ---
            print(f"Writing DataFrame to '{csv_path}'...")
            # Use index=False to avoid writing the DataFrame index as a column
            df.to_csv(csv_path, index=False, encoding='utf-8')

            if df.empty:
                 print(f"Warning: Table '{table_name}' was empty. CSV file only contains headers.")

            print(f"Successfully exported table '{table_name}' to '{csv_path}'.")

    # Catch pandas-specific errors if necessary, though general exceptions might cover them
    except sqlite3.Error as e:
        print(f"SQLite error occurred: {e}")
        sys.exit(1)
    except IOError as e:
        print(f"File I/O error occurred writing to '{csv_path}': {e}")
        sys.exit(1)
    except Exception as e:
        # Catch potential errors during pd.read_sql_query or df.to_csv
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)
    # No finally block needed for connection closing when using 'with' statement

if __name__ == "__main__":
    # Check for correct number of command-line arguments
    if len(sys.argv) != 4: # Still expecting 3 arguments
        print("Usage: python export_table_to_csv_pandas.py <database_file.sqlite> <table_name> <output_file.csv>")
        sys.exit(1)

    database_file = sys.argv[1]
    table_to_export = sys.argv[2]
    output_csv_file = sys.argv[3]

    # Call the updated function
    export_sqlite_table_to_csv_pandas(database_file, table_to_export, output_csv_file)
