import argparse
import sys
import os
import csv
from Bio import SeqIO

def parse_args(args):

    parser = argparse.ArgumentParser(
        prog="prep_nucdiff.py",
        description="Step1. Prepare run nucdiff. Find longest assembly in the pair, write file with parameters for nf",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("--fasta1",
                        action="store",
                        required=True,
                        help="Fasta file for isolate 1 (fna) produced by Bakta during annotation process")
    parser.add_argument("--fasta2",
                        action="store",
                        required=True,
                        help="Fasta file for isolate 2 (fna) produced by Bakta during annotation process")
    parser.add_argument("--suffix",
                        action="store",
                        required=False,
                        default=".fna",
                        help="Suffix of fasta1 and fasta2 files")

    args = vars(parser.parse_args())
    return args


# %% Functions
## %% helper get length fasta file
def get_fasta_len(file):
    """ returns the length of an assembly in fasta format
    """
    contigs = list(SeqIO.parse(file, "fasta"))
    return sum(list(map(len, contigs)))

## %% choosing the longest assembly (fasta file) as ref
def chose_ref_query(file1, file2, suffix) :
    """ returns the name of the assembly file that has the
        longest length and therefore should be used
        as reference
    """
    if get_fasta_len(file1) >= get_fasta_len(file2):
        ref_file, query_file = file1, file2
    else:
        ref_file, query_file = file2, file1

    ref = os.path.basename(ref_file).replace(suffix, '')
    query = os.path.basename(query_file).replace(suffix, '')
    return f"{ref}_{query}", ref, query

# %% SCRIPT
if __name__ == '__main__':
    args = parse_args(sys.argv[1:])

    #%% Output version file - per default
    with open('prep_nucdiff.version', 'w', newline='') as file:
        f.write("pre_nucdiff.py version 0.1")
    file.close()

    #%% Script the parameters ref or query for nextflow
    with open('ref_query_params.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(list(chose_ref_query(args["fasta1"], args["fasta2"], args["suffix"])))
    file.close()

# test
# prepnucdiff="/home/vi2067/Documents/onedrive_sync/NEW_WORK/2_Projects/2023/1_2023_Lm_ost_er_ikke_ost/DPI/bin/python/src/prep_nucdiff.py"
# python $prepnucdiff --fasta1 SRR11262033.fna --fasta2 SRR11262179.fna