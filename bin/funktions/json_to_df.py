#!/usr/bin/env python
# SECTION : Imports
import argparse
import os
import sys

import pandas as pd # type: ignore
import numpy as np # type: ignore
from error_template import log_message
from error_template import processing_error_message
from error_template import processing_result_message
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
    # script name
    script_name = os.path.basename(__file__)
    info_message = processing_result_message(script_name, "f{prep_info.__name__}", identifier)
    log_message(info_message, script_name)
    
    
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
    
    if info.empty:
        warning_message = "Warning: the table 'info' is empty"
        warning_message += f"Check the JSON file for identifier: {identifier}.\n"  
        print(warning_message)
        log_message(warning_message, script_name, exit_code=1)
    
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
    # script name
    script_name = os.path.basename(__file__)
    info_message = processing_result_message(script_name, "f{prep_features_df.__name__}", identifier)
    log_message(info_message, script_name)
    
    features = pd.json_normalize(json_object["features"])
    features.insert(0, "identifier", identifier)
    # need to change list types to string
    # we do not want to split those for now
    features = features.map(str)
    
    # NOTE : Replacing dots/- is important for SQLite compatibility for insertion into sqlite db
    features.columns = [col.replace(".", "_").replace("-", "_") for col in features.columns]
    
    if features.empty:
        warning_message = "Warning: the table 'features' is empty."
        warning_message += f"Check the JSON file for identifier: {identifier}.\n"  
        print(warning_message)
        log_message(warning_message, script_name, exit_code=1)
        
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
    # script name
    script_name = os.path.basename(__file__)
    info_message = processing_result_message(script_name, "f{prep_sequences.__name__}", identifier)
    log_message(info_message, script_name)
    
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
                info_message = f"Warning: 'orig_description' split did not produce enough values for column '{col}'."
                print(info_message)
                log_message(info_message, script_name)
                
    except Exception as e:
        warning_message = f"Error during individual 'orig_description' column assignment: {e}"
        print(warning_message)
        log_message(warning_message, script_name)

    ## NOTE : split description field
    try:
        sequences[["genus", "species", "gcode", "topology"]] = sequences[
            "description"
        ].str.split(" ", expand=True)
    except Exception as e:
        warning_message = f"Error during description split: {e}\n"
        warning_message += "Descriptions are not always complete, this might be the reason and not an error.\n"
        print(warning_message)
        log_message(warning_message, script_name)

    ## NOTE : Drop orig_description and description columns. 
    try:
        sequences.drop(labels=["orig_description", "description"], axis=1, inplace=True)
    except Exception as e:
        warning_message = f"Error dropping columns: {e}"
        print(warning_message)
        log_message(warning_message, script_name)

    # Replace unwanted patterns
    try:
        sequences.replace(["^.*=", "]", "NaN"], "", inplace=True, regex=True)
    except Exception as e:
        warning_message = f"Error during replace operation: {e}"
        print(warning_message)
        log_message(warning_message, script_name)
        
    # NOTE : do not need to replace dots/- in sequences table - added for eventual compatibility
    sequences.columns = [col.replace(".", "_").replace("-", "_") for col in sequences.columns]

    if sequences.empty:
        warning_message = "Warning: the table 'sequences' is empty."
        warning_message += f"Check the JSON file for identifier: {identifier}.\n"
        print(warning_message)
        log_message(warning_message, script_name, exit_code=1) 
        
    return sequences
#!SECTION

# SECTION MAIN
if __name__ == "__main__":
    script_name = os.path.basename(__file__)
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
        info_message = "Example usage:"
        info_message += "\npython json_to_df.py --input_json <path_to_file> --identifier <identifier>"
        log_message(info_message, script_name)
    # !SECTION
    
    # NOTE:  Login info output - handled by log_error
    
    # SECTION : SCRIPT : Load data and insert into the database
    info_message = processing_result_message(
        script_name, 
        args.input_json,
        args.identifier
        )
    log_message(info_message, script_name)
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
            
            info_message = f"\t\t{script_name} completed successfully.\n\n"
            info_message += f"DataFrames saved as CSV files in {current_working_directory}.\n"
            log_message(info_message, script_name)
                
    except FileNotFoundError:
        error_message = f"Input file not found: {args.input_json}"
        log_message(error_message, script_name, exit_code=1)

    except Exception as e:
        error_message = processing_error_message(
            script_name, 
            args.input_json, 
            identifier = args.identifier, 
            e = e)
        log_message(error_message, script_name, exit_code=1)
    # !SECTION
# !SECTION