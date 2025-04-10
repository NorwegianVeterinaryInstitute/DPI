#!/usr/bin/env python
# SECTION : Imports
import argparse
import datetime
import sys
import logging
import os

import pandas as pd # type: ignore
# !SECTION

# SECTION : Functions definitions
def stats_to_df(file_path):
    """
    transforms stat file to pandas df. Appends query and ref names
    :param file_path nucdiff result ref_query_stats.out 
    :return df (long format)
    """

    df = pd.read_table(file_path, sep="\t", header=None, names=["param", "value"], skip_blank_lines=True, index_col=None)
    
    # Extract the ref and query ids from the file name
    file_name = os.path.basename(file_path)
    parts = file_name.split("_")
    ref, query = parts[0], parts[1]
    
    # lines with empty info
    df = df[df.value.notnull()].assign(_REF=ref,_QUERY=query)
    
    return df
#!SECTION   
    
    
    # SECTION MAIN
if __name__ == "__main__":
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
        logging.info("Example usage:")
        logging.info("python stats_to_df.py --file_path <path_to_file> --identifier <identifier>")
    # !SECTION
    

    # SECTION : Login info output
    log_file_name = f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_stats_to_df.log"

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
        logging.info(f"Processing stat_file {args.file_path} for identifier '{args.identifier}'.")
        
        try:
                df = stats_to_df(args.file_path)
                current_working_directory = os.getcwd()  
                df.to_csv(
                    os.path.join(current_working_directory, f"{args.identifier}_stats.csv"),
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

        logging.info("stats_to_df.py script completed successfully.")
    except Exception as e:
        logging.error(f"An error occurred during the script execution: {e}")
        logging.error(f"Check {log_file_name} for more details.")
    # !SECTION
# !SECTION