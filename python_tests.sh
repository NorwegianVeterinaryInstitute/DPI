# !/usr/bin/env bash


# SECTION: 1. Testing creation of tables 

# ANCHOR : GFF tables 
cd /cluster/projects/nn9305k/active/evezeyl/projects/OEIO/2025_TEST_DPI/results/04_NUCDIFF/SRR11262179_SRR11262033
IMG="/cluster/work/users/evezeyl/images/evezeyl-py_test-latest.img"
apptainer shell $IMG

SCRIPT="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI_dev/DPI/bin/funktions/gff_to_df.py"
cat SRR11262179_SRR11262033_query_blocks.gff

$SCRIPT --file_path SRR11262179_SRR11262033_query_blocks.gff

rm *{.csv,.log}

# !SECTION


# SECTION 