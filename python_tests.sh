# !/usr/bin/env bash
IMG="/cluster/work/users/evezeyl/images/evezeyl-py_test-latest.img"
apptainer shell $IMG


# SECTION: 1. Testing creation of tables 
# ANCHOR : GFF tables - ok 
cd /cluster/projects/nn9305k/active/evezeyl/projects/OEIO/2025_TEST_DPI/results/04_NUCDIFF/SRR11262179_SRR11262033
SCRIPT="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI_dev/DPI/bin/funktions/gff_to_df.py"
#cat SRR11262179_SRR11262033_query_blocks.gff
$SCRIPT --file_path SRR11262179_SRR11262033_query_blocks.gff

rm *{.csv,.log}

# ANCHOR : vcf tables 
SCRIPT="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI_dev/DPI/bin/funktions/vcf_to_df.py"

cd /cluster/projects/nn9305k/active/evezeyl/projects/OEIO/2025_TEST_DPI/results/04_NUCDIFF/SRR11262179_SRR11262033
$SCRIPT --file_path SRR11262179_SRR11262033_query_snps.vcf --identifier nucdiff_vcf #nucdiff_vcf simple - working

cd /cluster/projects/nn9305k/active/evezeyl/projects/OEIO/2025_TEST_DPI/results/06_VCF_ANNOTATOR
$SCRIPT --file_path SRR11262179_SRR11262033_ref_snps_annotated.vcf --identifier vcf_annotator_vcf

rm *{.csv,.log}


# ANCHOR : json files 
cd /cluster/projects/nn9305k/active/evezeyl/projects/OEIO/2025_TEST_DPI/results/02_ANNOTATE/SRR11262033
SCRIPT="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI_dev/DPI/bin/funktions/json_to_df.py"
cat SRR11262033.json
$SCRIPT --input_json SRR11262033.json --identifier json_test

rm *{.csv,.sqlite,.log}

# ANCHOR : stats 
cd /cluster/projects/nn9305k/active/evezeyl/projects/OEIO/2025_TEST_DPI/results/04_NUCDIFF/SRR11262179_SRR11262033
SCRIPT="/cluster/projects/nn9305k/active/evezeyl/projects/OEIO/git/DPI_dev/DPI/bin/funktions/stats_to_df.py"
$SCRIPT --file_path SRR11262179_SRR11262033_stat.out --identifier test
rm *{.csv,.sqlite,.log}
# !SECTION


# SECTION 