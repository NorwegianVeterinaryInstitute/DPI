def clean_multifasta(file, symbol="=", replacement=""):
    """
    Replace unwanted symbols in fasta files, return fasta
    Could be transformed for any text actually
    :param file:
    :param symbol:
    :param replacement:
    :return: fasta with symbols replaced

    Dependencies:
    ------------


    """
    fasta_lines = []
    with open(file) as input:
        for line in input:
            # replacement symbols
            if symbol in line:
                line = re.sub(symbol, replacement, line)
            fasta_lines.append(line)

    fasta_lines = "".join(i for i in fasta_lines)
    new_file = file.replace(".fasta", "_noeq.fasta")
    with open(new_file, 'w') as new:
        new.write(fasta_lines)
