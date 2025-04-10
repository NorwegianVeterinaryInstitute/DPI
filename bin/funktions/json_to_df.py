#!/usr/bin/env python
# SECTION : Imports
import argparse
import datetime
import sys
import logging
import os

import pandas as pd # type: ignore
import numpy as np # type: ignore

# for main
import json
#!SECTION

# SECTION : Functions definitions 
# processing json data - 3 different tables
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
        pandas.DataFrame: Prepared sequences DataFrame.
    """
    sequences = pd.json_normalize(json_object["sequences"])
    sequences.insert(0, "identifier", identifier)

    # Cleaning the sequences table
    ## NOTE : split orig_description field
    ## orig_description is not always complete
    split_columns = ["len", "cov", "corr", "origname", "sw", "date"]
    new_columns = sequences["orig_description"].str.split(" ", expand=True)

    # Initialize the new columns with NaN
    for col in split_columns:
        sequences[col] = np.nan

    # Iterate through the split columns and assign values where available
    try:
        for i, col in enumerate(split_columns):
            if i < new_columns.shape[1]:  # Ensure the split produced enough columns
                sequences[col] = new_columns[i]
            else:
                print(f"Warning: 'orig_description' split did not produce enough values for column '{col}'.")
    except Exception as e:
        print(f"Error during individual 'orig_description' column assignment: {e}")

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
#!SECTION

# SECTION MAIN
if __name__ == "__main__":
    # SECTION : Argument parsing
    parser = argparse.ArgumentParser(description="Create a 3 tables to wrangle json results from annotations with Bakta and export as csv files.",)
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
    parser.add_argument("--input_json", required=True, help="Path of the dataframe that from which results will be appened to the database\n"
                                                            "Note that the function uses a pandas dataframe object, which must have been created\n"
                                                            "beforehand and passed to the function")
    parser.add_argument("--identifier", required=True, help="Identifier for the data")
    
    args = parser.parse_args()
    # !SECTION
    
    # SECTION : Check if required arguments are provided
    if not all([args.input_json, args.identifier,]):
        parser.error(
            "The following arguments are required: --input_json, --identifier, "
        )
        sys.exit(1)      
    # !SECTION
    
    # SECTION : Handling of example
    if args.example:
        logging.info("Example usage:")
        logging.info("python json_to_df.py --input_json <path_to_file> --identifier <identifier>")
    # !SECTION
    

    # SECTION : Login info output
    log_file_name = f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_json_to_df.log"

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
        logging.info(f"Processing json file {args.input_json} for identifier '{args.identifier}'.")
        
        try:
            with open(args.input_json, "r") as f:
                data = json.load(f)
                # NOTE: 3 types of data to extract for the json file
                info_df = prep_info_df(data, args.identifier)
                features_df = prep_features_df(data, args.identifier)
                sequences_df = prep_sequences_df(data, args.identifier)
                
                current_working_directory = os.getcwd()  

                info_df.to_csv(
                    os.path.join(current_working_directory, f"{args.identifier}_info.csv"),
                    index=False,
                    header=True
                    )
                features_df.to_csv(
                    os.path.join(current_working_directory, f"{args.identifier}_features.csv"),
                    index=False,
                    header=True
                    )
                sequences_df.to_csv(    
                    os.path.join(current_working_directory, f"{args.identifier}_sequences.csv"),
                    index=False,
                    header=True
                    )
                logging.info(f"Successfully processed {args.input_json} for identifier '{args.identifier}'.")
                logging.info(f"DataFrames saved as CSV files in {current_working_directory}.")
                    
        except FileNotFoundError:
            logging.error(f"Input file not found: {args.input_json}")
            sys.exit(1)
        
        except Exception as e:
            logging.error(f"Error processing tables for {args.identifier} from {args.input_json}: {e}")

        logging.info("json_to_df.py script completed successfully.")
    except Exception as e:
        logging.error(f"An error occurred during the script execution: {e}")
        logging.error(f"Check {log_file_name} for more details.")
    # !SECTION
# !SECTION