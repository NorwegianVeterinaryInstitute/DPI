#!/usr/bin/env python

# SECTION : Imports
import argparse
import os
import gffpandas.gffpandas as gffpd
#import pandas as pd
#import numpy as np
#import re
import datetime
import sys
import logging

# !SECTION

# SECTION : Functions definitions
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

# SECTION MAIN
if __name__ == "__main__":
    # SECTION : Argument parsing
    parser = argparse.ArgumentParser(
        prog="gff_to_df.py",
        description="Creates a table csv file from a gff file.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        add_help=True,)
    
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
    # Required arguments
    parser.add_argument("--file_path", required=True, help="Path to the result file",)
    
    args = parser.parse_args()
    # !SECTION
    
    # SECTION : Check if required arguments are provided
    if not all([args.file_path]):
        parser.error(
            "The following arguments are required: --file_path"
        )
        sys.exit(1)      
    # !SECTION
    
    # SECTION : Handling of example
    if args.example:
        logging.info("Example usage:")
        logging.info("python gff_to_df.py --file_path <path_to_file>")
    # !SECTION
    

    # SECTION : Login info output
    log_file_name = f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_gff_to_df.log"

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file_name, mode="w"),
            logging.StreamHandler(sys.stdout),
        ],
        )
    # !SECTION
    
    # SECTION : SCRIPT : create the data frame and export as csv files
    try:
        logging.info(f"processing result file ${args.file_path}")
        current_working_directory = os.getcwd()
        df = gff_to_df(args.file_path)
        base_name, extension = os.path.splitext(os.path.basename(args.file_path))        

        df.to_csv(
            os.path.join(current_working_directory, f"{base_name}.csv"),
            index=False,
            header=True
            )
    except Exception as e:
        logging.error(f"An error occurred during the processing of result files: {e}")
        logging.error(f"Check {log_file_name} for more details")
    # !SECTION
# !SECTION