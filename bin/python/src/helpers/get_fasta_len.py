# %% helper
from Bio import SeqIO
def get_fasta_len(file):
    """ returns the length of an assembly in fasta format

        Dependencies:
        ------------
        import os
        from Bio import SeqIO
    """
    contigs = list(SeqIO.parse(file, "fasta"))
    return sum(list(map(len, contigs)))