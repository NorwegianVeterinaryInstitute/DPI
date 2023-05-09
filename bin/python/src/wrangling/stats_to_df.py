# stat file to df
import os
import sys
import pandas as pd
from helpers.get_ids import get_ids

def stats_to_df(stat_file, id_dict, stat_pattern, comment = None):
    """
    transforms stat file to pandas df. Appends query and ref names, result file name, and comment field (used for info about analysis)
    :param stat_file nucdiff result gff_file
    :param id_dict dictionary containing ref, query ids (from detect_result_files)
    :param stat_pattern the pattern that is to remove from basename to obtain ref_query
    :param comment a string describing additional data to add to the table (or None)
    :return df (long format)
    """

    df = pd.read_table(stat_file, sep="\t", header=None, names=["param", "value"], skip_blank_lines=True, index_col=None)
    ref_stat, query_stat = get_ids(stat_file, stat_pattern)
    file_name = os.path.basename(stat_file)

    # Sanity - control detected ids are matching
    try:
        ref_stat == id_dict["ref"] and query_stat == id_dict["query"]
    except NameError:
        sys.exit("the detected reference and query id do not match. Review your command or debug")
    else:
        # lines with empty info
        df = df[df.value.notnull()].assign(_REF=id_dict["ref"],
                                           _QUERY=id_dict["query"],
                                           _RES_FILE=file_name,
                                           _COMMENT=comment)
        return df

# test
# teststat="/home/vi2067/Documents/onedrive_sync/NEW_WORK/2_Projects/2023/1_2023_Lm_ost_er_ikke_ost/ost_er_ikke_ost/code/python/inout/results/SRR11262033_SRR11262179_stat.out"
# my_id_dict = {'ref': 'SRR11262033', 'query': 'SRR11262179'}
# test1_df = stats_to_df(stat_file= teststat,
#                        id_dict = my_id_dict,
#                        stat_pattern = "_stat.out", comment = None)
# pd.set_option('display.max_columns', None)
# test1_df









