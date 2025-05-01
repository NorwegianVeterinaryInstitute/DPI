#!/usr/bin/env python

import sqlite3
import argparse
import os

def merge_databases(output_db_path, input_db_paths):
    """Merges multiple SQLite databases into a single output database."""
    output_conn = None
    try:
        output_conn = sqlite3.connect(output_db_path)
        output_cursor = output_conn.cursor()

        for i, input_db_path in enumerate(input_db_paths):
            if not os.path.exists(input_db_path):
                print(f"Warning: Input database not found: {input_db_path}")
                continue

            input_conn = None
            try:
                input_conn = sqlite3.connect(input_db_path)
                input_cursor = input_conn.cursor()

                # Get all table names from the input database
                input_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = [row[0] for row in input_cursor.fetchall()]

                for table_name in tables:
                    # Check if the table exists in the output database
                    output_cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")
                    output_table_exists = output_cursor.fetchone()

                    # Fetch all rows from the input table
                    input_cursor.execute(f"SELECT * FROM {table_name}")
                    rows = input_cursor.fetchall()
                    column_names = [description[0] for description in input_cursor.description]
                    placeholders = ', '.join(['?'] * len(column_names))
                    insert_sql = f"INSERT INTO {table_name} ({', '.join(column_names)}) VALUES ({placeholders})"

                    if not output_table_exists:
                        # Create the table in the output database if it doesn't exist
                        create_table_sql = f"CREATE TABLE {table_name} ({', '.join(column_names)});" # Simple version - you might need to adjust data types
                        output_cursor.execute(create_table_sql)

                    # Insert rows into the output table
                    output_cursor.executemany(insert_sql, rows)
                    output_conn.commit()

                print(f"Successfully merged data from: {input_db_path}")

            except sqlite3.Error as e:
                print(f"SQLite error while processing {input_db_path}: {e}")
                if input_conn:
                    input_conn.rollback()
            finally:
                if input_conn:
                    input_conn.close()

        print(f"Successfully merged all databases into: {output_db_path}")

    except sqlite3.Error as e:
        print(f"SQLite error while creating/merging into {output_db_path}: {e}")
        if output_conn:
            output_conn.rollback()
    finally:
        if output_conn:
            output_conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge multiple SQLite databases into a single database.")
    parser.add_argument("--output", required=True, help="Path to the output SQLite database.")
    parser.add_argument("--inputs", nargs='+', required=True, help="List of paths to the input SQLite databases.")

    args = parser.parse_args()

    merge_databases(args.output, args.inputs)