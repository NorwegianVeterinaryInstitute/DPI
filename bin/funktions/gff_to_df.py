import os
import gffpandas.gffpandas as gffpd
import pandas as pd
import numpy as np
import re

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
        gff_df = gff_df.attributes_to_columns().assign(_REF=ref, _QUERY=query)
        # NOTE : in case: Replacing dots/- is important for SQLite compatibility for insertion into sqlite db
        gff_df.columns = [col.replace(".", "_").replace("-", "_") for col in gff_df.columns]
        return gff_df
        
    except Exception as e:
        print(f"Error processing GFF data for {file_path}: {e}")
        return None
