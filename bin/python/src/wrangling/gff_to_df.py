# gff files to dataframe module
import sys
import os
import gffpandas.gffpandas as gffpd
from helpers.get_ids import get_ids
def gff_to_df(gff_file, id_dict, gff_pattern, comment = None):
    """
    transforms gff file to pandas df. Appends query and ref names, result file name, and comment field (used for info about analysis)
    :param gff_file nucdiff result gff_file
    :param id_dict dictionary containing ref, query ids (from detect_result_files)
    :param gff_pattern the pattern that is to remove from basename to obtain ref_query
    :param comment a string describing additional data to add to the table (or None)
    :return df if gff_file length >1 otherwise returns None
    """

    df = gffpd.read_gff3(gff_file)
    ref_gff, query_gff = get_ids(gff_file, gff_pattern)
    file_name = os.path.basename(gff_file)

    # Sanity - control detected ids are matching
    try:
        ref_gff == id_dict["ref"] and query_gff == id_dict["query"]
    except NameError:
        sys.exit("the detected reference and query id do not match. Review your command or debug")
    else:
        # dealing with empty gff (eg. query_additional): only one line
        with open(gff_file, "r") as f:
            file_len = len(f.readlines())
            f.close()
        if file_len <= 1:
            return None
        else:
            return df.attributes_to_columns().assign(_REF=id_dict["ref"],
                                                     _QUERY=id_dict["query"],
                                                     _RES_FILE=file_name,
                                                     _COMMENT=comment)


# if __name__ == "__main__":
#     import sys
#     import os
#     import gffpandas.gffpandas as gffpd
#     from diff.get_ids import get_ids
#     gff_to_df(sys.argv[1], sys.argv[2], sys.argv[3])


# # test
# #testgff1="/home/vi2067/Documents/onedrive_sync/NEW_WORK/2_Projects/2023/1_2023_Lm_ost_er_ikke_ost/ost_er_ikke_ost/code/python/inout/results/SRR11262033_SRR11262179_query_blocks.gff"
# my_id_dict = {'ref': 'SRR11262033', 'query': 'SRR11262179'}
# #test1_df = gff_to_df(testgff1, my_id_dict, "_query_blocks.gff")
# pd.set_option('display.max_columns', None)
# #test1_df.head()
#
# testgff2="/home/vi2067/Documents/onedrive_sync/NEW_WORK/2_Projects/2023/1_2023_Lm_ost_er_ikke_ost/ost_er_ikke_ost/code/python/inout/results/SRR11262033_SRR11262179_query_additional.gff"
# test2_df = gff_to_df(testgff2, my_id_dict, "_query_additional.gff")
# test2_df.head()
# if (test2_df is None):
#     print("None")
# else:
#     test2_df.head()


# testgff3="/home/vi2067/Documents/onedrive_sync/NEW_WORK/2_Projects/2023/1_2023_Lm_ost_er_ikke_ost/ost_er_ikke_ost/code/python/inout/results/SRR11262033_SRR11262179_query_snps.gff"
# test3_df = gff_to_df(testgff3, my_id_dict, "_query_snps.gff")


# testgff4="/home/vi2067/Documents/onedrive_sync/NEW_WORK/2_Projects/2023/1_2023_Lm_ost_er_ikke_ost/ost_er_ikke_ost/code/python/inout/results/SRR11262033_SRR11262179_ref_additional.gff"
# test4_df = gff_to_df(testgff4, my_id_dict, "_ref_additional.gff")
# test4_df.head()

# testgff4="/home/vi2067/Documents/onedrive_sync/NEW_WORK/2_Projects/2023/1_2023_Lm_ost_er_ikke_ost/ost_er_ikke_ost/code/python/inout/results/SRR11262033_SRR11262179_ref_additional.gff"
# test4_df = gff_to_df(testgff4, my_id_dict, "_ref_additional.gff", "comment")
# test4_df.head()
#
