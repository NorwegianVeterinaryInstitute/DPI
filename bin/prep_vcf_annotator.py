import argparse
import sys
import os
import pandas as pd

def parse_args(args):

    parser = argparse.ArgumentParser(
        prog="prep_vcf_annotator.py",
        description='Prepare annotation with vcf annotator: correct format vcf from nucdiff output. Prepares script launch command for vcf annotator',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("--vcf",
                        action="store",
                        required=True,
                        help="vcf file from nucdiff")
    parser.add_argument("--outdir",
                        action="store",
                        default=".",
                        help="oudir for reformated file")
    args = vars(parser.parse_args())
    return args

# %% functions
def reformat_vcf(file, outdir = ".", skip_rows = 2):
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
    if (outdir == "."):
        new_file = os.path.basename(new_file)
    else:
        new_file = outdir + "/" + os.path.basename(new_file)

    with open(new_file, 'w') as new:
        new.write(vcf_head)
    new.close()
    df.to_csv(new_file, sep="\t", mode="a", index=False)

# %% SCRIPT
if __name__ == '__main__':
    args = parse_args(sys.argv[1:])

    #%% Output version file - per default
    with open('prep_vcf_annotator.version', 'w', newline='') as file:
        file.write("prep_vcf_annotator.py version 0.1")
    file.close()

    #%% Action
    reformat_vcf(args["vcf"], args["outdir"])

