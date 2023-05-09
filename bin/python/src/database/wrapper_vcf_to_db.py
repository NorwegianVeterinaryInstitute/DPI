# gives the vcf to append to sqlite database
import sys
import os
from helpers.get_ids import get_ids
from wrangling.annotated_vcf_to_df import annotated_vcf_to_df
from database.df_to_database import df_to_database
import pandas as pd

def wrapper_vcf_to_db(vcf_file, id_dict, vcf_pattern, comment, db_file, table_name, if_exists = 'append'):
    """
    transforms annotated vcf file to pandas df, appends required columns then appends to sqlite databae
    :param vcf_file annotated result from vcf-annotator
    :param id_dict dictionary containing ref, query ids (from detect_result_files)
    :param vcf_pattern the pattern that is to remove from basename to obtain ref_query
    :param comment a string describing additional data to add to the table (or None)
    :param db_file sqlite database file
    :param if_exists pandas df.to_sql: if_exists 'replace','append','fail'
    """

    ref_vcf, query_vcf = get_ids(vcf_file, vcf_pattern)

    # Sanity check
    try:
        ref_vcf == id_dict["ref"] and query_vcf == id_dict["query"]
    except NameError:
        sys.exit("the detected reference and query id do not match. Review your command or debug")
    else:
        df = annotated_vcf_to_df(vcf_file)
        file_name = os.path.basename(vcf_file)
        df = df.assign(_REF=id_dict["ref"], _QUERY=id_dict["query"], _RES_FILE=file_name, _COMMENT=comment)

        if not df is None:
            df_to_database(df = df, db_file = db_file, table_name = table_name, if_exists = if_exists)
        else:
            print(f"No data to add for {vcf_file}")

# TEST
# tvcf = "/home/vi2067/Documents/onedrive_sync/NEW_WORK/2_Projects/2023/1_2023_Lm_ost_er_ikke_ost/ost_er_ikke_ost/code/python/inout/SRR11262033_SRR11262179_ref_snps_annotated.vcf"
# myid_dict = {'ref': 'SRR11262033', 'query': 'SRR11262179'}
# wrapper_vcf_to_db(tvcf, myid_dict, "_ref_snps_annotated.vcf",
#                   "test", "/home/vi2067/Documents/2/tt.sqlite",
#                   "_ref_snps_annotated", if_exists = 'append')
