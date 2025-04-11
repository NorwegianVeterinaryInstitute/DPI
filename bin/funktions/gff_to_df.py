#!/usr/bin/env python
# SECTION : Imports
import argparse
import os
import sys


import gffpandas.gffpandas as gffpd # type: ignore
from error_template import log_message
from error_template import processing_error_message
from error_template import processing_result_message
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
    # script name and info
    script_name = os.path.basename(__file__)
    
    info_message = processing_result_message(script_name, file_path)
    print(info_message)
    log_message(info_message, script_name)

    try:
        gff_df = gffpd.read_gff3(file_path)
        
        # Extract the ref and query ids from the file name
        file_name = os.path.basename(file_path)
        parts = file_name.split("_")
        ref, query = parts[0], parts[1]
        
    except Exception as e:
        error_message = f"Error reading GFF file {file_path}: {e}"
        print(error_message)
        log_message(error_message, script_name, exit_code=1) 
        
    # Dealing with empty gff (eg. query_additional): only one line
    with open(file_path, "r") as f:
        file_len = len(f.readlines())
        
    if file_len <= 1:
        warning_message = f"Warning: Empty GFF file: {file_path}. Skipping."
        print(warning_message)
        log_message(warning_message, script_name, exit_code=1)
        
        
    try:
        gff_df = gff_df.attributes_to_columns().assign(_REF=ref, _QUERY=query)
        # NOTE : in case: Replacing dots/- is important for SQLite compatibility for insertion into sqlite db
        gff_df.columns = [col.replace(".", "_").replace("-", "_") for col in gff_df.columns]
        
        if gff_df.empty:
            warning_message = "Warning: the table gff_df is empty."
            warning_message += f"Check the GFF file: {file_path}.\n"       
            print(warning_message)
            log_message(warning_message, script_name, exit_code=1)
            
        return gff_df
        
    except Exception as e:
        error_message = processing_error_message(
            script_name, 
            file_path,
            identifier= None,
            e = e
            )
        log_message(error_message, script_name, exit_code=1)
    

# SECTION : MAIN
if __name__ == "__main__":
    script_name = os.path.basename(__file__)
    # SECTION : Argument parsing
    parser = argparse.ArgumentParser(
        prog=script_name,
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
        info_message = "Example usage:"
        info_message += "python {script_name} --file_path <path_to_file>"
        log_message(info_message, script_name, exit_code=0)
    # !SECTION
    
    # NOTE:  Login info output - handled by log_error
    
    # SECTION : SCRIPT : create the data frame and export as csv files
    info_message = processing_result_message(
            script_name,
            args.file_path
            )
    log_message(info_message, script_name)
        
    try:
        current_working_directory = os.getcwd()
        df = gff_to_df(args.file_path)
        base_name, extension = os.path.splitext(os.path.basename(args.file_path))        

        df.to_csv(
            os.path.join(current_working_directory, f"{base_name}.csv"),
            index=False,
            header=True
            )
        info_message = f"\t\t{script_name} completed successfully.\n\n"
        log_message(info_message, script_name)
        
    except FileNotFoundError:
        error_message = f"Input file not found: {args.file_path}"
        log_message(error_message, script_name, exit_code=1)
        
    except Exception as e:
        error_message = processing_error_message(
            script_name, 
            args.file_path, 
            identifier = None, 
            e = e)
        log_message(error_message, script_name, exit_code=1)
    # !SECTION
# !SECTION