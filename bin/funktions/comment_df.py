# Creates a comment dataframe
# NOTE : I do not think I make this one a script - as wont be used outside of the pipeline
import os

import pandas as pd
from error_template import log_message
from error_template import processing_error_message
from error_template import processing_result_message


def create_comment_df (identifier, comment): 
    """Creates a database so that comments are registred for the analyses beeing run. Each time a file is appened to sqlite database
    Args:
        identifier (_type_): value identifier, sample or ref_query
        comment (_type_): comment for sqlite database, provided by nf script

    Returns:
        DataFrame: simple pandas dataframe
    """
    script_name = os.path.basename(__file__)
    info_message = processing_result_message(script_name, "NA - comment table creation")
    print(info_message)
    log_message(info_message, script_name)

    # identifier can be ref or ref_query 
    try: 
        parts = identifier.split("_")
        ref, query = parts[0], parts[1]
        
    # if there is query is empty or does not exist
    except IndexError:
        ref = identifier
        query = None
        
        
    # Create a DataFrame with the comment
    try: 
        data = {
            "ref": [ref],
            "query": [query],
            "comment": [comment]
        }
        df = pd.DataFrame(data)
        
        if df.empty:
            warning_message = "Warning: the table 'stats' is empty"
            warning_message += "Check the stats_out file.\n"  
            print(warning_message)
            log_message(warning_message, script_name, exit_code=1)
        
        return df
    
    except Exception as e:
        error_message = f"Error creating comment table: {e}"
        print(error_message)
        log_message(error_message, script_name, exit_code=1) 