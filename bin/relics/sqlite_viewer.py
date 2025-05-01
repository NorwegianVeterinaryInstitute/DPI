#!/usr/bin/env python
# SECTION : Imports
# written by gemini - 2025-05-01
import sqlite3
import sys
import os

# !SECTION

def view_sqlite_table(db_path, table_name):
    """
    Connects to an SQLite database, fetches all rows from a specified table,
    and prints the header and rows in a tab-delimited format.

    Args:
        db_path (str): The path to the SQLite database file.
        table_name (str): The name of the table to view.
    """
    # Check if the database file exists
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at '{db_path}'")
        sys.exit(1)

    conn = None  # Initialize connection variable
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # --- Check if table exists ---
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

        # --- Fetch column names ---
        cursor.execute(f"PRAGMA table_info({table_name});")
        # The column name is the second element (index 1) in the result tuples
        column_names = [info[1] for info in cursor.fetchall()]

        # --- Fetch all rows from the table ---
        cursor.execute(f"SELECT * FROM {table_name};")
        rows = cursor.fetchall()

        # --- Print header ---
        print("\t".join(column_names))
        print("-" * (sum(len(name) for name in column_names) + len(column_names) * 4)) # Separator line

        # --- Print rows ---
        if not rows:
            print(f"Table '{table_name}' is empty.")
        else:
            for row in rows:
                # Convert each element in the row to string for joining
                # Handle None values gracefully
                print("\t".join(str(item) if item is not None else 'NULL' for item in row))

    except sqlite3.Error as e:
        print(f"SQLite error occurred: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)
    finally:
        # Ensure the connection is closed even if errors occur
        if conn:
            conn.close()

if __name__ == "__main__":
    script_name = os.path.basename(__file__)    
    # Check for correct number of command-line arguments
    if len(sys.argv) != 3:
        print(f"Usage: python {script_name} <database_file.sqlite> <table_name>")
        sys.exit(1)

    database_file = sys.argv[1]
    table_to_view = sys.argv[2]
    

    view_sqlite_table(database_file, table_to_view)
    
