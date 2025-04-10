#!/usr/bin/env python
# SECTION : Imports
import argparse
import datetime
import sys
import logging
import os

import re 
import pandas as pd # type: ignore
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
    # get position start table
    start_row = 0
    with open(file_path) as input_file:
        for line in input_file:
            if "#CHROM" in line:
                 break
            start_row += 1
    print(start_row)
    
    # get the body
    df = pd.read_table(file_path, sep="\t", skiprows=start_row, skip_blank_lines=True, index_col=None)
    # each row to dict
    
    # NOTE: nucdiff vcf files do not have INFO column with ; and = as separators
    # For annotated vcf files 
    if "INFO" in df.columns:
        df["INFO"] = df["INFO"].apply(lambda row: row_to_dic_helper(row))
        # normalize INFO
        df2 = pd.json_normalize(df['INFO'])
        # concatenate df
        snp_df = pd.concat([df.drop("INFO", axis=1).reset_index(drop=True), df2.reset_index(drop=True)], axis=1)
    
    # should work for nucdiff vcf files
    else:
        snp_df = df
    
    # NOTE #CHROM is not valid in sqlite 
    snp_df.columns = [col.replace("#", "") for col in snp_df.columns]
    # Cleaning the formating of data originating from INFO : 
    for col in snp_df.select_dtypes(include='object').columns:
        snp_df[col] = snp_df[col].str.replace('[space]', ' ')
    
    print(f"vcf_to_df as run for {file_path}")
    return snp_df
#!SECTION  

# SECTION MAIN
if __name__ == "__main__":
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
        logging.info("Example usage:")
        logging.info("python vcf_to_df.py --file_path <path_to_file> --identifier <identifier>")
    # !SECTION
    

    # SECTION : Login info output
    log_file_name = f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_vcf_to_df.log"

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file_name, mode="w"),
            logging.StreamHandler(sys.stdout),
        ],
        )
    # !SECTION
    
# SECTION : SCRIPT : Load data and insert into the database
    try:
        logging.info(f"Processing vcf_file {args.file_path} for identifier '{args.identifier}'.")
        
        try:
                df = vcf_to_df(args.file_path)
                current_working_directory = os.getcwd()  
                df.to_csv(
                    os.path.join(current_working_directory, f"{args.identifier}_vcf.csv"),
                    index=False,
                    header=True
                    )

                logging.info(f"Successfully processed {args.file_path} for identifier '{args.identifier}'.")
                logging.info(f"DataFrame saved as CSV files in {current_working_directory}.")
                    
        except FileNotFoundError:
            logging.error(f"Input file not found: {args.file_path}")
            sys.exit(1)
        
        except Exception as e:
            logging.error(f"Error processing data for {args.identifier} from {args.file_path}: {e}")

        logging.info("vcf_to_df.py script completed successfully.")
    except Exception as e:
        logging.error(f"An error occurred during the script execution: {e}")
        logging.error(f"Check {log_file_name} for more details.")
    # !SECTION
# !SECTION


