def rename_contigs(file):
    """ renaming contigs in fasta file to make it complient
        with bakta annotation format

         Dependencies
        ------------
        from Bio import SeqIO
    """
    contigs = list(SeqIO.parse(file, "fasta"))
    for i, record in enumerate(contigs):
        record.id = "contig_" + str(i + 1)
        record.name = record.id[:]
        record.description = record.id[:]
    new_name = file.replace(".fasta", "_baktacontig.fasta")
    SeqIO.write(contigs, new_name, "fasta")