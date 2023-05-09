import os
import pandas as pd
def reformat_vcf(file, outdir, skip_rows = 2):
    """ reformat the vcf from nucdiff so it can be used in downstream analyses. Adds the "INFO column that was missing."
    :param file: vcf file from nucdiff
    :param skip_rows: default 2 (normal formatting from nucdiff vcf file)
    :param outdir: where the reformated vcf will be deposited
    :return paths of reformated files
    """
    # get the header
    with open(file) as input:
        vcf_head = [next(input) for _ in range(skip_rows)]
    input.close()

    vcf_head = "".join(i for i in vcf_head)

    # get the body
    df = pd.read_table(file, sep="\t", skiprows= skip_rows, skip_blank_lines=True, index_col=None)
    df = df.assign(INFO = ".")

    # write new vcf file
    new_file = file.replace(".vcf", "_reformated.vcf")

    ## path output
    new_file = outdir + "/" + os.path.basename(new_file)

    with open(new_file, 'w') as new:
        new.write(vcf_head)
    new.close()
    df.to_csv(new_file, sep="\t", mode="a", index=False)
    # passing path of string for vcf annotator command
    return new_file