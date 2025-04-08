import os 
import pandas as pd

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
    