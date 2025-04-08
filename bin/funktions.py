#!/usr/bin/env python

import pandas as pd
import numpy as np
import json
import os
import sqlite3
import re
import gffpandas.gffpandas as gffpd

# SECTION : Wrapper : processing results files
# NOTE : working
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
    print(f"Processing file: {file_name} for {identifier}")

    try:
        if result_type == "json":
            with open(file_path, "r") as f:
                data = json.load(f)

            # 3 types of data to extract for the json fil
            try:
                # Process info data
                info_df = prep_info_df(data, identifier)
                create_or_append_table(info_df, "info", identifier, file_name, db_conn)
            except Exception as e:
                print(f"Error processing info_df for {identifier}: {e}")

            try:
                # Process features data
                features_df = prep_features_df(data, identifier)
                create_or_append_table(
                    features_df, "features", identifier, file_name, db_conn
                )
            except Exception as e:
                print(f"Error processing features_df for {identifier}: {e}")
                
            try:
                # Process sequences data
                sequences_df = prep_sequences_df(data, identifier)
                create_or_append_table(
                    sequences_df, "sequences", identifier, file_name, db_conn
                )
            except Exception as e:
                print(f"Error processing sequences_df for {identifier}: {e}")

        elif result_type == "gff":           
            # processing each subtype of gff file 
            df = gff_to_df(file_path)
            
            if "_query_blocks" in file_name: 
                create_or_append_table(df, 'query_blocks', identifier, file_path, db_conn)
            elif "_query_snps" in file_name:
                create_or_append_table(df, 'query_snps', identifier, file_path, db_conn)
            elif "_query_struct" in file_name:
                create_or_append_table(df, 'query_struct', identifier, file_path, db_conn)
            elif "_query_additional" in file_name:
                create_or_append_table(df, 'query_additional', identifier, file_path, db_conn)
            elif "_query_snps_annotated" in file_name:
                create_or_append_table(df, 'query_snps_annotated', identifier, file_path, db_conn)
            elif "_ref_blocks" in file_name:
                create_or_append_table(df, 'ref_blocks', identifier, file_path, db_conn)
            elif "_ref_snps" in file_name:
                create_or_append_table(df, 'ref_snps', identifier, file_path, db_conn)
            elif "_ref_struct" in file_name:
                create_or_append_table(df, 'ref_struct', identifier, file_path, db_conn)
            elif "ref_additional" in file_name:
                create_or_append_table(df, 'ref_additional', identifier, file_path, db_conn)
            else:
                print(f"Warning: Unknown GFF subtype for {result_type} for {identifier}. Skipping {file_path}.")
                return 
            
        elif result_type == "vcf":
            # processing each subtype of vcf file
            if "_ref_snps_annotated" in file_name:
                pass
            elif "_query_snps_annotated" in file_name:
                pass
            else:
                print(f"Warning: Unknown VCF subtype for {result_type} for {identifier}. Skipping {file_path}.")
                return
            
        elif result_type == "stat":
            if "_stat.out in file_name:
                pass
            else: 
                print(f"Warning: Unknown stat subtype for for {result_type} for {identifier}. Skipping {file_path}.")
                pass 
                
        # TODO add a comment table for each indentifier / processing 
                

        db_conn.commit()
        print(f"Processed and inserted: {file_path} for identifier {identifier}")

    except Exception as e:
        print(f"Error processing {file_path} for identifier {identifier}: {e}")
        db_conn.rollback()

    print(f"the function process_result_file has run for identifier {identifier}.")

# !SECTION 




# NOTE : working
# SECTION : General function for creating table and append to sqlite database
def create_or_append_table(df, table_name, identifier, file_name, db_conn):
    """
    Creates or appends data to a SQLite table, using 'identifier' as the primary key,
    adding missing columns if necessary, and checking for existing data before inserting.

    Args:
        df (pd.DataFrame): DataFrame to insert.
        table_name (str): Name of the table.
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
    print(f"create_or_append_table function has run for {identifier}.")

    cursor.close()

# !SECTION




# SECTION : processing json data - 3 different tables
# NOTE : working
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
    
    # NOTE : Replacing dots/- is important for SQLite compatibility for insertion into sqlite db
    info.columns = [col.replace(".", "_").replace("-", "_") for col in info.columns]
    
    info.insert(0, "identifier", identifier)

    return info

# NOTE : working
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
    
    # NOTE : Replacing dots/- is important for SQLite compatibility for insertion into sqlite db
    features.columns = [col.replace(".", "_").replace("-", "_") for col in features.columns]

    return features

# NOTE : Working
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
        
    # NOTE : do not need to replace dots/- in sequences table - added for eventual compatibility
    sequences.columns = [col.replace(".", "_").replace("-", "_") for col in sequences.columns]

    return sequences

# !SECTION

# SECTION : processing gff data 
# NOTE : working
def gff_to_df(file_path):
    """
    Reads a GFF file and converts it into a pandas DataFrame.
    Appends query and ref names
    :param gff_file nucdiff result gff_file
    :return df if gff_file length >1 otherwise returns None

    Args:
        file_path (str): Path to the GFF file.

    Returns:
        pd.DataFrame: DataFrame containing the GFF data, or None if the file is not found or empty.
    """
    # Check if the file exists - report error if not
    if not os.path.exists(file_path):
        print(f"Error: GFF file not found: {file_path}")
        return None
        
        
    # Extract the ref and query ids from the file name
    file_name = os.path.basename(file_path)
    parts = file_name.split("_")
    ref, query = parts[0], parts[1]
    
    try:
        gff_df = gffpd.read_gff3(file_path)
    except Exception as e:
        print(f"Error reading GFF file {file_path}: {e}")
        return None
        
    # Dealing with empty gff (eg. query_additional): only one line
    with open(file_path, "r") as f:
        file_len = len(f.readlines())
        
    if file_len <= 1:
        print(f"Warning: Empty GFF file: {file_path}. Skipping.")
        return None
        
    try:
        gff_df = gff_df.attributes_to_columns().assign(_REF=ref, _QUERY=query, _RES_FILE=file_name)
        # NOTE : in case: Replacing dots/- is important for SQLite compatibility for insertion into sqlite db
        gff_df.columns = [col.replace(".", "_").replace("-", "_") for col in gff_df.columns]
        return gff_df
        
    except Exception as e:
        print(f"Error processing GFF data for {file_path}: {e}")
        return None




# processing each subtype of gff file


# SECTION : processing  query_blocks_files
# !SECTION 

# SECTION : processing  query_snps_gff_filess
# !SECTION 

# SECTION : processing  query_struct_files
# !SECTION 

# SECTION : processing  query_additional_files
# !SECTION 

# SECTION : processing  query_snps_annotated_files
# !SECTION 





# !SECTION

# ANCHOR : Functions to process
# ANCHOR : Functions to process
# ANCHOR : Functions to process
# ANCHOR : Functions to process
# ANCHOR : Functions to process
