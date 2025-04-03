#!/usr/bin/env python

import pandas as pd
import numpy as np


# ANCHOR : Wrapper : processing results files
def process_result_file(result_file, result_type, id, db_conn):
    """
    Processes a result files of a specific type,
    transforms them into a table, and inserts the results to the database.

    Args:
        result_file paths of the result file.
        result_type (str): The type of result (e.g., "json", "snp_annotations").
        id (str): The sample_id or pair identifier.
        db_conn (sqlite3.Connection): The database connection.
    """
    print("process_result_file function is not implemented yet.")


# ANCHOR : Functions for json data processing
# json data will go into 3 different tables (for archive)
def prep_info_df(json_object, sample_id):
    """_summary_
    prepare the info dataframe from the json annotation

    Args:
        json_object (_dict_): _annotation json from bakta_
        sample_id (_str_): _sample id to add to the table_
    """
    # create df for each separate key
    genome = pd.json_normalize(json_object["genome"])
    stats = pd.json_normalize(json_object["stats"])
    run = pd.json_normalize(json_object["run"])
    version = pd.json_normalize(json_object["version"])
    ## joining df for simple info - can go into own table
    info = pd.concat([genome, stats, run, version], axis=1)
    info.insert(0, "sample_id", sample_id)
    return info


def prep_features_df(json_object, sample_id):
    """_summary_
    prepare the features dataframe from the json annotation

    Args:
        json_object (_dict_): _annotation json from bakta_
        sample_id (_str_): _sample id to add to the table_
    """
    features = pd.json_normalize(json_object["features"])
    features.insert(0, "sample_id", sample_id)
    # need to change list types to string
    # we do not want to split those for now
    features = features.map(str)
    return features


def prep_sequences_df(json_object, sample_id):
    """_summary_
    prepare the sequences dataframe from the json annotation

    Args:
        json_object (_dict_): _annotation json from bakta_
        sample_id (_str_): _sample id to add to the table_
    """
    sequences = pd.json_normalize(json_object["sequences"])
    sequences.insert(0, "sample_id", sample_id)

    # cleaning the sequences table
    ## orig_description is not always complete - we cant fix in those cases
    try:
        sequences[["len", "cov", "corr", "origname", "sw", "date"]] = sequences[
            "orig_description"
        ].str.split(" ", expand=True)
    except:
        # if it does not work we only report as empty - neabs the description is not complete
        sequences[["len", "cov", "corr", "origname", "sw", "date"]] = pd.DataFrame(
            np.nan,
            columns=["len", "cov", "corr", "origname", "sw", "date"],
            index=np.arange(len(sequences["orig_description"])),
        )
    ## The rest should be ok
    sequences[["genus", "species", "gcode", "topology"]] = sequences[
        "description"
    ].str.split(" ", expand=True)
    sequences.drop(labels=["orig_description", "description"], axis=1)
    sequences.replace(["^.*=", "]", "NaN"], "", inplace=True, regex=True)
    return sequences


def prep_sequences_df(json_object, sample_id):
    """_summary_
    prepare the sequences dataframe from the json annotation

    Args:
        json_object (_dict_): _annotation json from bakta_
        sample_id (_str_): _sample id to add to the table_
    """
    sequences = pd.json_normalize(json_object["sequences"])
    sequences.insert(0, "sample_id", sample_id)

    # cleaning the sequences table
    ## orig_description is not always complete - we cant fix in those cases
    try:
        sequences[["len", "cov", "corr", "origname", "sw", "date"]] = sequences[
            "orig_description"
        ].str.split(" ", expand=True)
    except:
        # if it does not work we only report as empty - neabs the description is not complete
        sequences[["len", "cov", "corr", "origname", "sw", "date"]] = pd.DataFrame(
            np.nan,
            columns=["len", "cov", "corr", "origname", "sw", "date"],
            index=np.arange(len(sequences["orig_description"])),
        )
    ## The rest should be ok
    sequences[["genus", "species", "gcode", "topology"]] = sequences[
        "description"
    ].str.split(" ", expand=True)
    sequences.drop(labels=["orig_description", "description"], axis=1)
    sequences.replace(["^.*=", "]", "NaN"], "", inplace=True, regex=True)
    return sequences


# ANCHOR : Functions to process
# ANCHOR : Functions to process
# ANCHOR : Functions to process
# ANCHOR : Functions to process
# ANCHOR : Functions to process
