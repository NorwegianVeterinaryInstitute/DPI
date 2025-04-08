import sys
import os
import gffpandas.gffpandas as gffpd

# list files in current directory
os.listdir(os.getcwd())
file_path = os.path.join("./SRR11262179_SRR11262033_query_blocks.gff")
file_name = os.path.basename(file_path)
"_query_blocks" in file_name

# extract ref query names 
parts = file_name.split("_")
ref, query = parts[0], parts[1]

# getting table 
gff_df = gffpd.read_gff3(file_path)
print(gff_df.header)
print(gff_df.df)
    