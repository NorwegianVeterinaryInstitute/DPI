# %% helper
# replaces two set of characters in files (for small reformatting)
def replace_2char(infile, outfile, replace_from1, replace_from2, replace_to1, replace_to2):
    """
    Replace to set of text in files, eg. for ref, query naming (
     Here used to change contigs names in maf file prior to indexing
     Ex regular expressions: https://www3.ntu.edu.sg/home/ehchua/programming/howto/Regexe.html
    :param infile: infile
    :param outfile: outfile
    :param replace_from1: regex pattern to replace from ie ID1_[0-9]*
    :param replace_from2: regex pattern to replace from ie ID1_[0-9]*
    :param replace_to1: replacement string ie ID1
    :param replace_to2: replacement string ie ID2
    :return: file with string replaced

    Dependencies:
    ------------
    import re
    """

    with open(infile, 'r') as file:
        filetext = file.read()

    filetext = re.sub(replace_from1, replace_to1, filetext)
    filetext = re.sub(replace_from2, replace_to2, filetext)

    with open(outfile, 'w') as file:
        file.write(filetext)
