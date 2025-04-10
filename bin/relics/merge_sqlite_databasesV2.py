#!/usr/bin/env python
# Made by gemini 2025-04-10

import sqlite3
import argparse
import os

def merge_databases(output_db_path, input_db_paths):
    """Merges multiple SQLite databases into a single output database,
    handling schema evolution (adding missing columns) and preventing duplicate rows
    using the 'file_name' column for initial duplicate check."""
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
                    input_column_names = list(input_columns.keys())

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
                        output_column_names = list(output_columns.keys())
                        columns_to_add = set(input_columns.keys()) - set(output_columns.keys())
                        for col_to_add in columns_to_add:
                            alter_table_sql = f"ALTER TABLE {table_name} ADD COLUMN {col_to_add} NULL;"
                            output_cursor.execute(alter_table_sql)
                            output_conn.commit()
                            print(f"Added column '{col_to_add}' to table '{table_name}' in output database.")
                            output_column_names.append(col_to_add) # Update output column names

                    # Fetch all rows from the input table
                    input_cursor.execute(f"SELECT * FROM {table_name}")
                    rows_to_insert = input_cursor.fetchall()

                    inserted_count = 0
                    for input_row in rows_to_insert:
                        input_row_dict = dict(input_row)
                        file_name_value = input_row_dict.get('file_name')

                        if file_name_value:
                            # Check if the file_name already exists in the output database
                            output_cursor.execute(f"SELECT 1 FROM {table_name} WHERE file_name = ?", (file_name_value,))
                            existing_file_name = output_cursor.fetchone()

                            if existing_file_name:
                                # file_name exists, now check the rest of the columns
                                output_cursor.execute(f"SELECT * FROM {table_name} WHERE file_name = ?", (file_name_value,))
                                matching_rows = [dict(row) for row in output_cursor.fetchall()]

                                is_duplicate = False
                                for existing_row in matching_rows:
                                    match = True
                                    for col in input_column_names:
                                        if col in existing_row and input_row_dict.get(col) != existing_row.get(col):
                                            match = False
                                            break
                                        elif col in existing_row and input_row_dict.get(col) is None and existing_row.get(col) is not None:
                                            match = False
                                            break
                                        elif col not in existing_row and input_row_dict.get(col) is not None:
                                            pass # Cannot be a duplicate based on this new column

                                    if match and all(col in existing_row or input_row_dict.get(col) is None for col in output_column_names):
                                        is_duplicate = True
                                        break

                                if not is_duplicate:
                                    values = [input_row_dict.get(col) for col in output_column_names]
                                    placeholders = ', '.join(['?'] * len(output_column_names))
                                    insert_sql = f"INSERT INTO {table_name} ({', '.join(output_column_names)}) VALUES ({placeholders})"
                                    output_cursor.execute(insert_sql, values)
                                    output_conn.commit()
                                    inserted_count += 1
                            else:
                                # file_name doesn't exist, so it's a new entry
                                values = [input_row_dict.get(col) for col in output_column_names]
                                placeholders = ', '.join(['?'] * len(output_column_names))
                                insert_sql = f"INSERT INTO {table_name} ({', '.join(output_column_names)}) VALUES ({placeholders})"
                                output_cursor.execute(insert_sql, values)
                                output_conn.commit()
                                inserted_count += 1
                        else:
                            # If 'file_name' column is missing or None, perform the full row comparison (less efficient)
                            output_cursor.execute(f"SELECT * FROM {table_name}")
                            existing_rows = [dict(row) for row in output_cursor.fetchall()]

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
                                    elif col not in existing_row and input_row_dict.get(col) is not None:
                                        pass

                                if match and all(col in existing_row or input_row_dict.get(col) is None for col in output_column_names):
                                    is_duplicate = True
                                    break

                            if not is_duplicate:
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
    parser = argparse.ArgumentParser(description="Merge multiple SQLite databases into a single database, handling schema evolution and preventing duplicates using 'file_name'.")
    parser.add_argument("--output", required=True, help="Path to the output SQLite database.")
    parser.add_argument("--inputs", nargs='+', required=True, help="List of paths to the input SQLite databases.")

    args = parser.parse_args()

    merge_databases(args.output, args.inputs)
    
    
# ah, the file_name value will be the same for each row for each output database, because each output database will be the result of processing one file. Thus is the value of the first row in the column file_name is not in the merged database, none of the value of input database is in the merged database. Thus I do not think we need to check all the rows if the first value of file_name is not in the merged database.