# %% Helper
import os
def get_ids(file, pattern, sep="_"):
    """ Getting ids from files path from basename eg. to add columns before adding to database
        by default ref_query
    :param file: path of file to get
    :param pattern pattern to remove (that is not ID1_ID2)
    :param sep separator used
    """
    file_basename = os.path.basename(file)
    return file_basename.replace(pattern, "").split(sep)

# test
# testgff1="/home/vi2067/Documents/onedrive_sync/NEW_WORK/2_Projects/2023/1_2023_Lm_ost_er_ikke_ost/ost_er_ikke_ost/code/python/inout/results/SRR11262033_SRR11262179_query_blocks.gff"
# test_ref, test_query = get_ids(testgff1, "_query_blocks.gff")
# print (f"ref: {test_ref}, query: {test_query}")
