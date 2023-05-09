def create_run_nucdiff(ref, query, outdir, prefix, outdir_script):
    """
    creates a bash script with the command to run nucdiff
    :param ref: the bakta fna that will be used as reference for nucdiff
    :param query: the bakta fna that will be used as query for nucdiff
    :param outdir: the output directory of nucdiff
    :param prefix: the prefix used in nucdiff
    :param outdir_script: the path where the script to run nucdiff will be written

    Dependencies:
    ------------

    """

    # thought first to run it from python but
    command = f"nucdiff  --vcf yes {ref} {query} {outdir} {prefix}"

    if outdir_script == ".":
        script = "run_nucdiff.sh"
    else:
        script = outdir_script + "/" + "run_nucdiff.sh"

    with open(script, 'w') as f:
        f.write("#!/bin/bash\n")
        f.write(command)
    f.close()

# create_run_nucdiff("ref.fasta", "query.fasta", ".", "ref_query", ".")
