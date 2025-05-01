#!/usr/bin/env python
# Made by gemini 2025-04-10
import sqlite3
import argparse
import os

def merge_databases(output_db_path, input_db_paths):
    """Merges multiple SQLite databases into a single output database,
    handling schema evolution (adding missing columns) and preventing duplicate rows.
    
    """
    output_conn = None
    try:
        # Connect to the output database (creates if it doesn't exist)
        output_conn = sqlite3.connect(output_db_path)
        output_conn.row_factory = sqlite3.Row  # Access columns by name
        output_cursor = output_conn.cursor()

        for i, input_db_path in enumerate(input_db_paths):
            if not os.path.exists(input_db_path):
                print(f"Warning: Input database not found: {input_db_path}")
                continue

            input_conn = None
            try:
                input_conn = sqlite3.connect(input_db_path)
                input_conn.row_factory = sqlite3.Row
                input_cursor = input_conn.cursor()

                # Get all table names from the input database
                input_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                input_tables = [row['name'] for row in input_cursor.fetchall()]

                for table_name in input_tables:
                    # Get column information from the input table
                    input_cursor.execute(f"PRAGMA table_info({table_name})")
                    input_columns = {row['name']: row['type'] for row in input_cursor.fetchall()}

                    # Check if the table exists in the output database
                    output_cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")
                    output_table_exists = output_cursor.fetchone()

                    if not output_table_exists:
                        # Create the table in the output database with columns from the input
                        create_table_sql = f"CREATE TABLE {table_name} ({', '.join([f'{col} {dtype}' for col, dtype in input_columns.items()])});"
                        output_cursor.execute(create_table_sql)
                        output_conn.commit()
                        print(f"Created table '{table_name}' in output database.")
                    else:
                        # Add missing columns to the output table
                        output_cursor.execute(f"PRAGMA table_info({table_name})")
                        output_columns = {row['name']: row['type'] for row in output_cursor.fetchall()}
                        columns_to_add = set(input_columns.keys()) - set(output_columns.keys())
                        for col_to_add in columns_to_add:
                            alter_table_sql = f"ALTER TABLE {table_name} ADD COLUMN {col_to_add} NULL;"
                            output_cursor.execute(alter_table_sql)
                            output_conn.commit()
                            print(f"Added column '{col_to_add}' to table '{table_name}' in output database.")

                    # Fetch all rows from the input table
                    input_cursor.execute(f"SELECT * FROM {table_name}")
                    rows_to_insert = input_cursor.fetchall()
                    input_column_names = list(input_columns.keys())

                    # Fetch existing rows from the output table to check for duplicates
                    output_cursor.execute(f"SELECT * FROM {table_name}")
                    existing_rows = [dict(row) for row in output_cursor.fetchall()] # Convert to dictionaries for easier comparison
                    output_column_names = [description[0] for description in output_cursor.description]

                    inserted_count = 0
                    for input_row in rows_to_insert:
                        input_row_dict = dict(input_row)

                        # Check for duplicates (simple comparison of all available columns)
                        is_duplicate = False
                        for existing_row in existing_rows:
                            match = True
                            for col in input_column_names:
                                if col in existing_row and input_row_dict.get(col) != existing_row.get(col):
                                    match = False
                                    break
                                elif col in existing_row and input_row_dict.get(col) is None and existing_row.get(col) is not None:
                                    match = False
                                    break
                                elif col not in existing_row and input_row_dict.get(col) is not None: # New column in input, None in existing
                                    pass # Cannot be a duplicate based on this new column

                            if match and all(col in existing_row or input_row_dict.get(col) is None for col in output_column_names):
                                is_duplicate = True
                                break

                        if not is_duplicate:
                            # Prepare values for insertion, handling missing columns in the input row
                            values = [input_row_dict.get(col) for col in output_column_names]
                            placeholders = ', '.join(['?'] * len(output_column_names))
                            insert_sql = f"INSERT INTO {table_name} ({', '.join(output_column_names)}) VALUES ({placeholders})"
                            output_cursor.execute(insert_sql, values)
                            output_conn.commit()
                            inserted_count += 1

                    print(f"Merged {inserted_count} new rows into table '{table_name}' from: {input_db_path}")

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
    parser = argparse.ArgumentParser(description="Merge multiple SQLite databases into a single database, handling schema evolution and preventing duplicates.")
    parser.add_argument("--output", required=True, help="Path to the output SQLite database.")
    parser.add_argument("--inputs", nargs='+', required=True, help="List of paths to the input SQLite databases.")

    args = parser.parse_args()

    merge_databases(args.output, args.inputs)