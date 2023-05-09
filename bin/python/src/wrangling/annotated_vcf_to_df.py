## %% annotated vcf to panda dataframe
import pandas as pd
import re
def annotated_vcf_to_df(file):
    """
    Read the annotated vcf and returns a pandas dataframe
    :param file: annotated vcf
    :return: pandas dataframe
    """
    # Helpers
    def row_to_dic_helper(row):
        """
        Returns a dictionary
        splitting columns at ; and =
        :param row: row
        :return: dictionary
        """
        list_row = re.split(';|=', row)
        # keys : values
        return dict(zip(list_row[::2], list_row[1::2]))

    # get position start table
    start_row = 0
    with open(file) as input:
        for line in input:
            if "#CHROM" in line:
                 break

            start_row += 1
    input.close()
    # get the body
    df = pd.read_table(file, sep="\t", skiprows= start_row, skip_blank_lines=True, index_col=None)
    # each row to dict
    df["INFO"] = df["INFO"].apply(lambda row: row_to_dic_helper(row))
    # normalize INFO
    df2 = pd.json_normalize(df['INFO'])
    # concatenate df
    return pd.concat([df.drop("INFO", axis=1).reset_index(drop=True), df2.reset_index(drop=True)], axis=1)

# Test
# tvcf = "/home/vi2067/Documents/onedrive_sync/NEW_WORK/2_Projects/2023/1_2023_Lm_ost_er_ikke_ost/ost_er_ikke_ost/code/python/inout/SRR11262033_SRR11262179_ref_snps_annotated.vcf"
# test_df = annotated_vcf_to_df(tvcf)
# test_df.head()