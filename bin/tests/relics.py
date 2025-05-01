import sqlite3
import os
os.listdir()


# Listing tables
conn = sqlite3.connect('2025_DPI_test.sqlite')
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

for table in tables:
    print(table[0])

conn.close()
    
# Getting Table Schema:
import sqlite3

    conn = sqlite3.connect('2025_DPI_test.sqlite')
    cursor = conn.cursor()

    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='my_table'")
    schema = cursor.fetchone()

    if schema:
        print(schema[0])

    conn.close()
    
    
# clear console 
os.system('clear')
# os.system('cls')

# For vcf files
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