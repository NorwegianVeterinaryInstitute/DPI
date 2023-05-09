#import os
#import gffpandas.gffpandas as gffpd
import pandas as pd
#import sqlite3
#import re
#from Bio import SeqIO
#pip list # Biopython 1.81


# %% Sourcing functions
## %% database interaction
#from .df_to_database import df_to_database
#from .chose_ref import chose_ref
# from rename_contigs import rename_contigs
# from .reformat_vcf import reformat_vcf
from reformat.reformat_maf import reformat_maf
# from .df_to_database import df_to_database
# from .get_ids import get_ids

# from .replace_2char import replace_2char
from helpers.clean_multifasta import clean_multifasta

# %% for testing


# %% RUN
## %% Getting data to database
### %% Ex1. Query blocks to columns to database
# query_blocks = gffpd.read_gff3(gff_infile)
# ids=get_ids(gff_infile, "_query_blocks.gff")
# query_blocks_attr_to_columns = query_blocks.attributes_to_columns().assign(ID1=ids[0], ID2=ids[1])
# query_blocks_attr_to_columns.head(n=30)
#
# df_to_database(query_blocks_attr_to_columns, "nucdiff_res.db",  "query_blocks", "replace")

### %% Ex2. stat file
### Extract ids from filename
#stat_file_basename = os.path.basename(stat_file)
#type(stat_file_basename)
#ids = stat_file_basename.replace(stat_file_pattern, "").split("_")
#print(ids[0] + " " + ids[1])

# stats = pd.read_table(stat_file, sep="\t", header=None, names=["param", "value"], skip_blank_lines=True, index_col=None)
# ids = get_ids(stat_file, "_stat.out")
# stats = stats[stats.value.notnull()].assign(ID1=ids[0], ID2=ids[1])
# stats.head(n=30)
# df_to_database(stats, "nucdiff_res.db",  "stats", "replace")

### %% Ex3. Choice reference query
# print(get_fasta_len(fasta1))
# print(get_fasta_len(fasta2))
# return file path to use as reference
# we might want rewrite after ie for tagging
# def chose_ref(file1, file2):
#     if get_fasta_len(file1) >= get_fasta_len(file1):
#         return file1
#     return file2

#sanity_ref_bakta_file ="/mnt/2T/Insync/ONEDRIVE/NEW_WORK/2_Projects/2023/1_2023_Lm_ost_er_ikke_ost/ost_er_ikke_ost/analysis/testdiff/highlysimilar/bakta_reannotate/bakta_annot/SRR11262033.fna"
#sanity_ref_original="/mnt/2T/Insync/ONEDRIVE/NEW_WORK/2_Projects/2023/1_2023_Lm_ost_er_ikke_ost/ost_er_ikke_ost/analysis/testdiff/highlysimilar/bakta_reannotate/SRR11262033_pilon_spades.fasta"
#print(get_fasta_len(sanity_ref_bakta_file))
#print(get_fasta_len(sanity_ref_original))
# OK is the same
# chose_ref(fasta1, fasta2)

# renaming contigs in fasta file
# -[ ] should add that it output file correspondance old to new names

### %% Ex4. Renaming contigs - discarded for now
#rename_contigs(fasta1)
#rename_contigs(fasta2)

### %% Ex5. Reformating the vcf file
# https://gist.github.com/dceoy/99d976a2c01e7f0ba1c813778f9db744

# We could add the option to add a new header if needed (but for now ok)
# temp_head, temp = reformat_vcf(vcf_ref)
# reformat_vcf(vcf_ref)

## %% Ex6.  conversion of mummer pairwise alignment so that can be used in standard programs
# then need to look at maf format or fasta alignment to reconstruct / visualise
# https://biopython.org/wiki/Multiple_Alignment_Format
# Conversion with delta2maf sofware externally
ref_maf_file = "ref.maf"

## we might need to replace contigs namings
#test = "blb_1 0 1 10 "
#re.sub("blb_[0-9]*", "blb", test)
#re.sub("blb_[0-9]*", "blb", test2)
#test2 = "blb_11 0 1 10"
ref_maf_file_corr = "/mnt/2T/Insync/ONEDRIVE/NEW_WORK/2_Projects/2023/1_2023_Lm_ost_er_ikke_ost/ost_er_ikke_ost/analysis/testdiff/highlysimilar/bakta_reannotate/bakta_annot/nucdiff/ref_corr.maf"
replace_2char(ref_maf_file, ref_maf_file_corr, "SRR11262033_[0-9]*" , "SRR11262179_[0-9]*", "SRR11262033" , "SRR11262179")
# ok this works but I am not so sure anymore its the right thing to do ...

## %% Ex7 reformatting maf file to see if then can be opened by other software
reformat_maf("ref.maf", "SRR11262033")

## %% Ex8. wranglign block sequences - temporary let go
from Bio import AlignIO
from Bio.AlignIO import MafIO
#ref SRR11262033 query SRR11262179

for blocks in AlignIO.parse("ref_reformated.maf", "maf"):
    for block in blocks:
        print(f' starts: {block.annotations["start"]} on the {block.annotations["strand"]} strand of a sequence '
              f'{block.annotations["srcSize"]} in length, and runs for {block.annotations["size"]} bp')

## creating the index for the reference
# nope this still does not work no matter what !!
# can it be because it waits for a . for the chromosome and not a _ ?
# replace_char_infile("ref_reformated.maf", "ref_reformated_corr.maf", "SRR11262033_" , "SRR11262179_", "SRR11262033." , "SRR11262179.")
# https://github.com/biopython/biopython/blob/master/Bio/AlignIO/MafIO.py
ref_idx = MafIO.MafIndex("SRR11262033_16.mafindex", "ref_reformated.maf", "SRR11262033")

# !!! still does not work
# seems also not score as number so ....
# https://github.com/pbenner/tfbayes/blob/master/tfbayes/alignio/MafIO.py
# there is a bug somewhere so go with fasta

cliff = "/mnt/2T/Insync/ONEDRIVE/NEW_WORK/"
multi_fasta_file = cliff + "2_Projects/2023/1_2023_Lm_ost_er_ikke_ost/ost_er_ikke_ost/code/python/nucdiff_res/ref_reformated.fasta"

# maybe do a copy before but ok for testing

from Bio import SeqIO
from Bio.SeqFeature import SeqFeature, SimpleLocation

# clean = in the multifasta file
clean_multifasta("ref_reformated.fasta")

def read_multi_fasta(file):
    # getting all the records
    records=[]
    with open(file) as handle:
        for record in SeqIO.parse(handle, "fasta"):
            records.append(record)
    return records


test = read_multi_fasta("ref_reformated_noeq.fasta")
for i, record in enumerate(test):
    print(i, record.id)
# ok so we can extract blocks now pair, impair ... and the rest add features and see how to reproduce alignments then

# so in description is the start and stop
records[0].id
records[0].description
records[0].seq
records[0].seq.start
record[0].features
len(records[0].seq)
contig, start, size, strand, srcSize = records[0].description.split(" ")
seq1=records[0]
# ref is the reference used
# counting is python stile starts at 0 so stops
# https://www.biostars.org/p/57549/
blocknr=1
seq1.features = SeqFeature(SimpleLocation(int(start), int(start) + int(size) -1, strand = 1, ref = "SRR11262033"), type=f"block_{blocknr}", id = contig)

seq1.start = start
print(seq1.features)

temp.head(n = 30)
type(start)

## %% Ex.9 Snp file correction , then see if can get annotations in database
# reformat_vcf(vcf_ref)
# reformat_vcf(vcf_query)

# then annotation  - then need to get annotations to database
# https://github.com/dridk/PyVCF3
#
#
# test = annotated_vcf_to_df(annotated_vcf_ref)
# test.to_csv("test_df_annotated.csv")


#print(test[:1])

## Ex10. syntheny
