import os
import re
def create_run_vcf_annotator(vcf_ref, vcf_query, gbff1, gbff2, outdir, outdir_script):
    """
    creates a bash script with the command to run vcf annotator
    :param vcf_ref: the reformatted vcf according to reference coordinate system from nucdiff
    :param vcf_query: the reformatted vcf according to query coordinate system from nucdiff
    :param outdir: the output directory of vcf annotator
    :param outdir_script: the path where the script to run vcf annotator will be written
    """

    # detect suffix
    prefix = re.sub("_ref_snps_reformated.vcf", '', os.path.basename(vcf_ref))
    # str ids
    ref_id, query_id = re.split('_', prefix)
    # which gff2 is ref and query
    if ref_id in gbff1:
        ref_gbff = gbff1
        query_gbff = gbff2
    else:
        ref_gbff = gbff2
        query_gbff = gbff1

    # create references commands to run vcf_annotator
    command_ref = f"vcf-annotator {vcf_ref} {ref_gbff} --output {outdir + '/' + prefix + '_ref_snps_annotated.vcf'}"
    command_query = f"vcf-annotator {vcf_query} {query_gbff} --output {outdir + '/' + prefix + '_query_snps_annotated.vcf'}"

    if outdir_script == ".":
        script = "run_vcf_annotator.sh"
    else:
        script = outdir_script + "/" + "run_vcf_annotator.sh"
        #if outdir does not exist create
        os.makedirs(os.path.dirname(script), exist_ok=True)

    # write script
    with open(script, 'w') as f:
        f.write("#!/bin/bash\n")
        f.write(command_ref + "\n")
        f.write(command_query)
    f.close()

