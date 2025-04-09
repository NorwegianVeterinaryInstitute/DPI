# Creates a comment dataframe
import pandas as pd


def create_comment_df (identifier, comment): 
    """Creates a database so that comments are registred for the analyses beeing run. Each time a file is appened to sqlite database
    Args:
        identifier (_type_): value identifier, sample or ref_query
        comment (_type_): comment for sqlite database, provided by nf script

    Returns:
        DataFrame: simple pandas dataframe
    """
    
    # identifier can be ref or ref_query 
    
    try: 
        parts = identifier.split("_")
        ref, query = parts[0], parts[1]
    # if there is query is empty or does not exist
    except IndexError:
        ref = identifier
        query = None
    # Create a DataFrame with the comment
    data = {
        "ref": [ref],
        "query": [query],
        "comment": [comment]
    }
    df = pd.DataFrame(data)
    return df
    