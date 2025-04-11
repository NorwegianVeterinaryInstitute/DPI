#!/usr/bin/env python
# SECTION : Imports
import argparse
import os
import sys

import pandas as pd # type: ignore
from error_template import log_message
from error_template import processing_error_message
from error_template import processing_result_message
# !SECTION

# SECTION : Functions definitions
def stats_to_df(file_path):
    """
    transforms stat file to pandas df. Appends query and ref names
    :param file_path nucdiff result ref_query_stats.out 
    :return df (long format)
    """
     # script name
    script_name = os.path.basename(__file__)
    
    # Check if the file exists - report error if not
    if not os.path.exists(file_path):
        error_message = f"Error: GFF file not found: {file_path}"
        print(error_message)
        log_message(error_message, script_name, exit_code=1) # log and exit
    
    # script     
    df = pd.read_table(file_path, sep="\t", header=None, names=["param", "value"], skip_blank_lines=True, index_col=None)
    
    # Extract the ref and query ids from the file name
    file_name = os.path.basename(file_path)
    parts = file_name.split("_")
    ref, query = parts[0], parts[1]
    
    # lines with empty info
    df = df[df.value.notnull()].assign(_REF=ref,_QUERY=query)
    
    # eg. prevents read/write errors
    if df.empty:
        warning_message = "Warning: the table 'stats' is empty"
        warning_message += "Check the stats_out file.\n"  
        print(warning_message)
        log_message(warning_message, script_name, exit_code=1)
    
    return df
#!SECTION   
    
    
# SECTION MAIN
if __name__ == "__main__":
    script_name = os.path.basename(__file__)
    # SECTION : Argument parsing
    parser = argparse.ArgumentParser(description="Process stat_file created by nucdiff and export as csv files.",)
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
    
    # required arguments (only for main)
    parser.add_argument("--file_path", required=True, help="Path of the file that will be transformed into a pandas dataframe\n")
    parser.add_argument("--identifier", required=True, help="Identifier for the data. Only required for script, to allow throwing erros")
    
    args = parser.parse_args()
    # !SECTION
    
    # SECTION : Check if required arguments are provided
    if not all([args.file_path, args.identifier,]):
        parser.error(
            "The following arguments are required: --file_path, --identifier"
        )
        sys.exit(1)      
    # !SECTION
    
    # SECTION : Handling of example
    if args.example:
        info_message = "Example usage:"
        info_message += f"python {script_name} --file_path <path_to_file> --identifier <identifier>"
        log_message(info_message, script_name)

    # !SECTION
    
    # NOTE:  Login info output - handled by log_error    
    
    # SECTION : SCRIPT : Load data and insert into the database
    info_message = processing_result_message(
            script_name,
            args.file_path
            )
    log_message(info_message, script_name)
    
    try:
        df = stats_to_df(args.file_path)
        current_working_directory = os.getcwd()  
        df.to_csv(
            os.path.join(current_working_directory, f"{args.identifier}_stats.csv"),
            index=False,
            header=True
            )

        info_message = f"\t\t{script_name} completed successfully.\n\n"
        info_message += f"DataFrame saved as CSV files in {current_working_directory}."
        log_message(info_message, script_name)
        
        
                
    except FileNotFoundError:
        error_message = f"Input file not found: {args.file_path}"
        log_message(error_message, script_name, exit_code=1)

    except Exception as e:
        error_message = processing_error_message(
            script_name, 
            args.file_path, 
            args.identifier, 
            e = e)
        log_message(error_message, script_name, exit_code=1)
        
    # !SECTION
# !SECTION