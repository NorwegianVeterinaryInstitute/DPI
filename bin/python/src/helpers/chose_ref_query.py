## %% choosing the longest assembly (fasta file) as ref
from helpers.get_fasta_len import get_fasta_len
import os
def chose_ref_query(file1, file2, suffix) :
    """ returns the name of the assembly file that has the
        longest length and therefore should be used
        as reference
    """
    if get_fasta_len(file1) >= get_fasta_len(file1):
        pattern = f"{os.path.basename(file1).replace(suffix, '')}_{os.path.basename(file2).replace(suffix, '')}"
        return file1, file2, pattern

    pattern = f"{os.path.basename(file2).replace(suffix, '')}_{os.path.basename(file1).replace(suffix, '')}"
    return file2, file1, pattern


