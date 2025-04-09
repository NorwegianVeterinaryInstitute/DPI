import re 
import pandas as pd
    
def vcf_to_df(file_path):
    """
    Read the (annotated) vcf and returns a pandas dataframe
    :param file_path: annotated vcf
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
        import re
        import pandas as pd
        
        list_row = re.split(';|=', row)
        # Ensure even number of elements to form key-value pairs
        if len(list_row) % 2 != 0:
            # Handle cases with trailing semicolons or incomplete key-value pairs
            list_row.append('')  # Add an empty string as a value for the last key
        # keys : values
        dic_cols = dict(zip(list_row[::2], list_row[1::2]))
        return dic_cols

    # get position start table
    start_row = 0
    with open(file_path) as input_file:
        for line in input_file:
            if "#CHROM" in line:
                 break
            start_row += 1

    # get the body
    df = pd.read_table(file_path, sep="\t", skiprows=start_row, skip_blank_lines=True, index_col=None)
    # each row to dict
    df["INFO"] = df["INFO"].apply(lambda row: row_to_dic_helper(row))
    # normalize INFO
    df2 = pd.json_normalize(df['INFO'])
    # concatenate df
    snp_df = pd.concat([df.drop("INFO", axis=1).reset_index(drop=True), df2.reset_index(drop=True)], axis=1)
    # #CHROM is not valid in sqlite 
    snp_df.columns = [col.replace("#", "") for col in snp_df.columns]
    # Cleaning the formating of data originating from INFO : 
    for col in snp_df.select_dtypes(include='object').columns:
        snp_df[col] = snp_df[col].str.replace('[space]', ' ')
    
    print(f"vcf_to_df as run for {file_path}")
    return snp_df

if __name__ == '__main__':
    # Create a dummy VCF file for testing
    vcf_content = """##fileformat=VCFv4.2
##INFO=<ID=AC,Number=A,Type=Integer,Description="Allele count in genotypes, for each ALT allele, in the same order as listed">
##INFO=<ID=AF,Number=A,Type=Float,Description="Allele Frequency">
##INFO=<ID=AN,Number=1,Type=Integer,Description="Total number of alleles in called genotypes">
##INFO=<ID=DP,Number=1,Type=Integer,Description="Approximate read depth; some reads may have been filtered">
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO
chr1	100	rs123	A	G	100	PASS	AC=1;AF=0.5;AN=2;DP=10
chr1	101	rs456	C	T,A	150	PASS	AC=2,1;AF=0.667,0.333;AN=3;DP=15;MQ=30
chr2	200	.	G	C	90	FILTER	DP=5;MQ=40;SVTYPE=DEL
chr3	300	rs789	T	A	120	PASS	AC=1;DP=20;AF=0.25;
"""
    with open("test.vcf", "w") as f:
        f.write(vcf_content)

    # Example usage:
    file_path = "test.vcf"
    df_result = vcf_to_df(file_path)
    print(df_result)