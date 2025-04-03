#!/usr/bin/env python

import pandas as pd
import numpy as np
import json
import os
import sqlite3


# ANCHOR : Wrapper : processing results files
def process_result_file(file_path, result_type, identifier, db_conn, comment):
    """
    Processes a single result file, transforms it into a table\n
    If created, a new column will be created and appended to the database\n
    NaN will be used to fill the column for previous records.\n
    Then the result table will be inserted it into the database.

    Args:
        file_path (str): Path to the result file.
        result_type (str): The type of result (e.g., "json").
        identifier (str): The identifier (pair or sample_id).
        db_conn (sqlite3.Connection): The database connection.
        comment (str): Comment for the database entries. Please set to NULL if not used.
    """
    file_name = os.path.basename(file_path)

    try:
        if result_type == "json":
            with open(file_path, "r") as f:
                data = json.load(f)

            # 3 types of data to extract for the json fil
            # Process info data
            info_df = prep_info_df(data, identifier)
            create_or_append_table(info_df, "info", identifier, file_name, db_conn)

            # Process features data
            features_df = prep_features_df(data, identifier)
            create_or_append_table(
                features_df, "features", identifier, file_name, db_conn
            )
            # Process sequences data
            sequences_df = prep_sequences_df(data, identifier)
            create_or_append_table(
                sequences_df, "sequences", identifier, file_name, db_conn
            )

        elif result_type == "gff":
            # Add logic for GFF parsing and table creation
            # Example:
            # df = parse_gff(file_path)
            # create_or_append_table(df, result_type, identifier, file_name, cursor)
            pass  # Add gff parsing here
        else:
            print(f"Warning: Unknown result type: {result_type}. Skipping {file_path}.")
            return

        db_conn.commit()
        print(f"Processed and inserted: {file_path}")

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        db_conn.rollback()

    print("the function process_result_file has run.")


# ANCHOR : Functions for json data processing
def create_or_append_table(df, table_name, identifier, file_name, db_conn):
    """
    Creates or appends data to a SQLite table, using 'identifier' as the primary key,
    adding missing columns if necessary, and checking for existing data before inserting.

    Args:
        df (pd.DataFrame): DataFrame to insert.
        table_name (str): Name of the table.
        identifier (str): The identifier (primary key).
        file_name (str): The name of the processed file.
        db_conn (sqlite3.Connection): The database connection.
    """
    cursor = db_conn.cursor()
    df.insert(0, "identifier", identifier)
    df.insert(1, "file_name", file_name)

    # Check if table exists
    cursor.execute(
        f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'"
    )
    table_exists = cursor.fetchone()

    if not table_exists:
        # Create table with 'identifier' as primary key
        columns = ", ".join(f"{col} TEXT" for col in df.columns)
        cursor.execute(
            f"CREATE TABLE {table_name} (identifier TEXT PRIMARY KEY, {columns[13:]})"
        )  # remove identifier column from columns string and add primary key
        # TODO why columns[13:]?
    else:
        # Check and add missing columns
        cursor.execute(f"PRAGMA table_info({table_name})")
        existing_cols = [row[1] for row in cursor.fetchall()]
        missing_cols = [col for col in df.columns if col not in existing_cols]

        for col in missing_cols:
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {col} TEXT")
            cursor.execute(f"UPDATE {table_name} SET {col} = NULL")

        print(f"Table '{table_name}' already exists, columns added if needed.")

    # Insert data, checking for duplicates based on 'identifier'
    placeholders = ", ".join("?" for _ in df.columns)
    try:
        cursor.execute(
            f"INSERT INTO {table_name} VALUES ({placeholders})", tuple(df.iloc[0])
        )  # insert only one row at the time, because the identifier is a primary key.
        print(f"Data inserted into '{table_name}'.")  # Add print statement
    except sqlite3.IntegrityError:
        print(f"Skipping duplicate identifier: {identifier} in file {file_name}")

    cursor.close()


# json data will go into 3 different tables (for archive)
def prep_info_df(json_object, identifier):
    """
    Prepares the info DataFrame from the JSON annotation.

    Args:
        json_object (dict): Annotation JSON from Bakta.
        identifier (str): Sample ID to add to the table.
    Returns:
        pd.DataFrame: Prepared info DataFrame.
    """
    # create df for each separate key
    genome = pd.json_normalize(json_object["genome"])
    stats = pd.json_normalize(json_object["stats"])
    run = pd.json_normalize(json_object["run"])
    version = pd.json_normalize(json_object["version"])

    # joining df for simple info - can go into own table
    info = pd.concat([genome, stats, run, version], axis=1)
    info.insert(0, "identifier", identifier)

    # function log:
    print(f"info table created for {identifier}")

    # NOTE test if the info table is populated
    info.to_csv("info.csv", index=False)

    return info


def prep_features_df(json_object, identifier):
    """
    Prepares the features DataFrame from the JSON annotation.

    Args:
        json_object (dict): Annotation JSON from Bakta.
        identifier (str): Sample ID to add to the table.
    Returns:
        pd.DataFrame: Prepared features DataFrame.
    """
    features = pd.json_normalize(json_object["features"])
    features.insert(0, "identifier", identifier)
    # need to change list types to string
    # we do not want to split those for now
    features = features.map(str)

    # function log:
    print(f"features table created for {identifier}")

    # NOTE test if the features table is populated
    features.to_csv("features.csv", index=False)

    return features


def prep_sequences_df(json_object, identifier):
    """
    Prepares the sequences DataFrame from the JSON annotation.

    Args:
        json_object (dict): Annotation JSON from Bakta.
        identifier (str): Sample ID to add to the table.
    Returns:
        pd.DataFrame: Prepared sequences DataFrame.
    """
    sequences = pd.json_normalize(json_object["sequences"])
    sequences.insert(0, "identifier", identifier)

    # Cleaning the sequences table
    ## NOTE : split orig_description field
    ## orig_description is not always complete
    try:
        sequences[["len", "cov", "corr", "origname", "sw", "date"]] = sequences[
            "orig_description"
        ].str.split(" ", expand=True)
    except Exception as e:
        print(f"Error during orig_description split: {e}")
        # if it does not work we only report as empty - neabs the description is not complete
        sequences[["len", "cov", "corr", "origname", "sw", "date"]] = pd.DataFrame(
            np.nan,
            columns=["len", "cov", "corr", "origname", "sw", "date"],
            index=np.arange(len(sequences["orig_description"])),
        )

    ## NOTE : split description field
    try:
        sequences[["genus", "species", "gcode", "topology"]] = sequences[
            "description"
        ].str.split(" ", expand=True)
    except Exception as e:
        print(f"Error during description split: {e}")

    ## NOTE : Drop orig_description and description columns
    try:
        sequences.drop(labels=["orig_description", "description"], axis=1, inplace=True)
    except Exception as e:
        print(f"Error dropping columns: {e}")

    # Replace unwanted patterns
    try:
        sequences.replace(["^.*=", "]", "NaN"], "", inplace=True, regex=True)
    except Exception as e:
        print(f"Error during replace operation: {e}")
    # function log:
    print(f"sequences table created for {identifier}")

    # NOTE test if the sequences_df is empty
    sequences.to_csv("sequences.csv", index=False)

    return sequences


# ANCHOR : Functions to process
# ANCHOR : Functions to process
# ANCHOR : Functions to process
# ANCHOR : Functions to process
# ANCHOR : Functions to process
