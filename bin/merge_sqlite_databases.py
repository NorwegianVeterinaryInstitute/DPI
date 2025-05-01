#!/usr/bin/env python
# Made by gemini 2025-04-10
# Improved by Eve Fiskebeck 

# SECTION : IMPORTS
import argparse
import os
import sys
import sqlite3

# --- Add script's directory to sys.path ---
# To be able to import local modules
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)
# --- End sys.path modification ---

from funktions.error_template import log_message,processing_error_message,processing_result_message
# !SECTION 

# SECTION : FUNCTION Merging datase 
def merge_databases(output_db_path, input_db_paths):
    """Merges multiple SQLite databases into a single output database,
    handling schema evolution and preventing duplicate rows by checking the
    'file_name' of the first row of each input database's tables.
    """
    
    # script name and info
    script_name = os.path.basename(__file__)
    
    info_message = processing_result_message(script_name, "input_dbs")
    print(info_message)
    log_message(info_message, script_name)
    
    output_conn = None
    try:
        # Connect to the output database (creates if it doesn't exist)
        output_conn = sqlite3.connect(output_db_path)
        output_conn.row_factory = sqlite3.Row  # Access columns by name
        output_cursor = output_conn.cursor()
    
        for i, input_db_path in enumerate(input_db_paths):
            if not os.path.exists(input_db_path):
                warning_message = f"Warning: Input database {input_db_path} not found"
                print(warning_message)
                log_message(warning_message, script_name, exit_code=0)
                # NOTE : here I want to continue but through a warning. Data will be missing
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
                        output_column_names = list(input_columns.keys())
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

                    # Fetch the first row from the input table to get the 'file_name'
                    input_cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
                    first_input_row = input_cursor.fetchone()

                    if first_input_row and 'file_name' in first_input_row.keys() and first_input_row['file_name'] is not None:
                        file_name_value = first_input_row['file_name']

                        # Check if this 'file_name' already exists in the output database table
                        output_cursor.execute(f"SELECT 1 FROM {table_name} WHERE file_name = ?", (file_name_value,))
                        existing_file_name = output_cursor.fetchone()

                        if not existing_file_name:
                            # 'file_name' not found, so no duplicates from this input database table
                            input_cursor.execute(f"SELECT * FROM {table_name}")
                            rows_to_insert = input_cursor.fetchall()
                            inserted_count = 0
                            for input_row in rows_to_insert:
                                input_row_dict = dict(input_row)
                                values = [input_row_dict.get(col) for col in output_column_names]
                                placeholders = ', '.join(['?'] * len(output_column_names))
                                insert_sql = f"INSERT INTO {table_name} ({', '.join(output_column_names)}) VALUES ({placeholders})"
                                output_cursor.execute(insert_sql, values)
                                output_conn.commit()
                                inserted_count += 1
                            print(f"Inserted {inserted_count} rows into table '{table_name}' from: {input_db_path} (based on unique file_name).")
                        else:
                            # 'file_name' found, need to check for individual row duplicates
                            input_cursor.execute(f"SELECT * FROM {table_name}")
                            rows_to_insert = input_cursor.fetchall()
                            existing_rows_with_filename = [dict(row) for row in output_cursor.execute(f"SELECT * FROM {table_name} WHERE file_name = ?", (file_name_value,)).fetchall()]
                            inserted_count = 0
                            for input_row in rows_to_insert:
                                input_row_dict = dict(input_row)
                                is_duplicate = False
                                for existing_row in existing_rows_with_filename:
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
                            print(f"Inserted {inserted_count} new rows into table '{table_name}' from: {input_db_path} (after individual duplicate check).")

                    else:
                        # If 'file_name' is missing or None in the first row, fall back to full comparison
                        print(f"Warning: 'file_name' missing in the first row of table '{table_name}' in {input_db_path}. Performing full row comparison.")
                        output_cursor.execute(f"SELECT * FROM {table_name}")
                        existing_rows = [dict(row) for row in output_cursor.fetchall()]
                        inserted_count = 0
                        input_cursor.execute(f"SELECT * FROM {table_name}")
                        rows_to_insert = input_cursor.fetchall()
                        for input_row in rows_to_insert:
                            input_row_dict = dict(input_row)
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
                        # print(f"Inserted {inserted_count} new rows into table '{table_name}' from: {input_db_path} (full row comparison).")

            except sqlite3.Error as e:
                error_message = f"SQLite error while processing {input_db_path}: {e}"
                print(error_message)
                log_message(error_message, script_name)
                if input_conn:
                    input_conn.rollback()
            finally:
                if input_conn:
                    input_conn.close()
        
        info_message = f"Successfully merged all databases into: {output_db_path}"
        print(info_message)
        log_message(info_message, script_name)
        
    except sqlite3.Error as e:
        error_message = f"SQLite error while creating/merging into {output_db_path}: {e}"
        print(error_message)
        log_message(error_message, script_name)
        if output_conn:
            output_conn.rollback()
    finally:
        if output_conn:
            output_conn.close()
# !SECTION 

# SECTION MAIN
if __name__ == "__main__":
    script_name = os.path.basename(__file__)    
    # SECTION : Argument parsing
    parser = argparse.ArgumentParser(
        description="Merge multiple SQLite databases, optimizing duplicate check using the first 'file_name' value.",
        )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to the output SQLite database.",
        )
    parser.add_argument(
        "--input",
        nargs='+',
        required=True,
        help="List of paths to the input SQLite databases.",
        )
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
    
    args = parser.parse_args()
    # !SECTION
    
    # SECTION : Check if required arguments are provided
    if not all([args.output, args.input,]):
        parser.error(
            "The following arguments are required: --output <output_db_path>, --input <input_db_paths>.\n"
        )
        sys.exit(1)      
    # !SECTION
    
    # SECTION : Handling of example
    if args.example:
        info_message = "Example usage:"
        info_message += "python {script_name} --output <output_db_path> --input <input_db_paths>"
        log_message(info_message, script_name, exit_code=0)
    # !SECTION
    
    # NOTE:  Login info output - handled by log_error
         
    # SECTION : SCRIPT : Merge the result files
    info_message = processing_result_message(
            script_name,
            "input_dbs",
            )
    log_message(info_message, script_name)
    try:
        merge_databases(args.output, args.input)
    except FileNotFoundError:
        error_message = f"Input file not found: {args.file_path}"
        log_message(error_message, script_name, exit_code=1)
    except Exception as e:
        error_message = processing_error_message(
            script_name, 
            "inputs_db",
            identifier = None, 
            e = e)
        log_message(error_message, script_name, exit_code=1)
    # !SECTION

# !SECTION