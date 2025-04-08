import pandas as pd
import numpy as np
    
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
        pd.DataFrame: Prepared sequences DataFrame.
    """
    sequences = pd.json_normalize(json_object["sequences"])
    sequences.insert(0, "identifier", identifier)

    # Cleaning the sequences table
    ## NOTE : split orig_description field
    ## orig_description is not always complete
    try:
        sequences[["len", "cov", "corr", "origname", "sw", "date"]] = sequences[
            "orig_description"
        ].str.split(" ", expand=True)
    except Exception as e:
        print(f"Error during orig_description split: {e}")
        # if it does not work we only report as empty - neabs the description is not complete
        sequences[["len", "cov", "corr", "origname", "sw", "date"]] = pd.DataFrame(
            np.nan,
            columns=["len", "cov", "corr", "origname", "sw", "date"],
            index=np.arange(len(sequences["orig_description"])),
        )

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
