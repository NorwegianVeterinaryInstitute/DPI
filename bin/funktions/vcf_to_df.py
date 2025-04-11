#!/usr/bin/env python
# SECTION : Imports
import argparse
import os
import sys

import re 
import pandas as pd # type: ignore

from .error_template import log_message, processing_error_message, processing_result_message

# !SECTION

# SECTION : Functions definitions
# ANCHOR Helper function
def row_to_dic_helper(row):
    """
    Returns a dictionary
    splitting columns at ; and =
    :param row: row
    :return: dictionary
    """
    # NOTE if space is a splitting delimiter
    list_row = re.split(';|=', row)
    # Ensure even number of elements to form key-value pairs
    if len(list_row) % 2 != 0:
        # Handle cases with trailing semicolons or incomplete key-value pairs
        list_row.append('')  # Add an empty string as a value for the last key
    # keys : values
    dic_cols = dict(zip(list_row[::2], list_row[1::2]))
    return dic_cols
    
def vcf_to_df(file_path):
    """
    Read the (annotated) vcf and returns a pandas dataframe
    :param file_path: annotated vcf
    :return: pandas dataframe
    """
    # script name and info
    script_name = os.path.basename(__file__)
    
    info_message = processing_result_message(script_name, file_path)
    print(info_message)
    log_message(info_message, script_name)
    
    # script 
    try:     
        # get position start table
        start_row = 0
        with open(file_path) as input_file:
            for line in input_file:
                if "#CHROM" in line:
                    break
                start_row += 1
        print(f"starting row for reading vcf file: {start_row}")
    except Exception as e:
        error_message = f"Error reading VCF file {file_path}: {e}"
        print(error_message)
        log_message(error_message, script_name, exit_code=1) 
            
    try:
        df = pd.read_table(file_path, sep="\t", skiprows=start_row, skip_blank_lines=True, index_col=None)

        # For annotated vcf files 
        if "INFO" in df.columns:
            df["INFO"] = df["INFO"].apply(lambda row: row_to_dic_helper(row))
            # normalize INFO
            df2 = pd.json_normalize(df['INFO'])
            # concatenate df
            snp_df = pd.concat([df.drop("INFO", axis=1).reset_index(drop=True), df2.reset_index(drop=True)], axis=1)

        # NOTE: For Nucdiff vcf files do not have INFO column with ; and = as separators
        else:
            snp_df = df
        
        # NOTE #CHROM is not valid in sqlite headers
        snp_df.columns = [col.replace("#", "") for col in snp_df.columns]
        # Cleaning the formating of data originating from INFO : 
        for col in snp_df.select_dtypes(include='object').columns:
            snp_df[col] = snp_df[col].str.replace('[space]', ' ')
    
        if snp_df.empty:
            warning_message = "Warning: the table snp_df is empty."
            warning_message += f"Check the SNP file: {file_path}.\n"       
            print(warning_message)
            log_message(warning_message, script_name, exit_code=1)
                
        return snp_df
    
    except Exception as e:
        error_message = processing_error_message(
            script_name, 
            file_path,
            identifier= None,
            e = e
            )
        log_message(error_message, script_name, exit_code=1)
    
#!SECTION  

# SECTION MAIN
if __name__ == "__main__":
    script_name = os.path.basename(__file__)    
    # SECTION : Argument parsing
    parser = argparse.ArgumentParser(description="Process vcf_file created by eg. nucdiff and export as csv files.",)
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
        log_message(info_message, script_name, exit_code=0)
    # !SECTION
    
    # NOTE:  Login info output - handled by log_error
    
    # SECTION : SCRIPT : Load data and insert into the database
    info_message = processing_result_message(
            script_name,
            args.file_path
            )
    log_message(info_message, script_name)
    
    try:
        current_working_directory = os.getcwd()  
        df = vcf_to_df(args.file_path)
        df.to_csv(
            os.path.join(current_working_directory, f"{args.identifier}_vcf.csv"),
            index=False,
            header=True
            )
    
        info_message = f"\t\t{script_name} completed successfully.\n\n"
        info_message += f"DataFrame saved as CSV file in {current_working_directory}.\n"
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


