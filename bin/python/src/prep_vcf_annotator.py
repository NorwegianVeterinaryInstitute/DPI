import argparse
import os
import sys

parser = argparse.ArgumentParser(
    prog="prep_vcf_annotator.py",
    description='Prepare annotation with vcf annotator: correct format vcf from nucdiff output. Prepares script launch command for vcf annotator',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument("--vcf1",
                    action="store",
                    required=True,
                    help="vcf file output 1 from nucdiff")
parser.add_argument("--vcf2",
                    action="store",
                    required=True,
                    help="vcf file output 2 from nucdiff")
parser.add_argument("--gbff1",
                    action="store",
                    required=True,
                    help="gbff file output 1 from bakta annotation")
parser.add_argument("--gbff2",
                    action="store",
                    required=True,
                    help="gbff file output 2 from bakta annotation")
parser.add_argument("--outdir",
                    action="store",
                    default=".",
                    help="path of output directory for vcf annotator")
parser.add_argument("--outdir_script",
                    action="store",
                    default=".",
                    help="path where the script to run vcf annotator will be deposited")
parser.add_argument("--test",
                    action="store",
                    default=False,
                    help="Source paths for testing. Paths defined in test_paths.py")


args = vars(parser.parse_args())

# sourcing functions dir
sys.path.append(os.path.dirname(__file__) + "/" + "diff")

# default test directories here
if args["test"]:
    sys.path.append(os.path.dirname(__file__) + "/" + "test")
    import test_paths
    pc_out = os.getenv("OUTPUTDIR")
    #print("pc_out: " + pc_out)
    args["outdir"] = pc_out
    args["outdir_script"] = pc_out

# get the paths if ".":
## cannot work for test
if not args["test"] and args["outdir"] == ".":
    args["outdir"] = os.getcwd()

if not args["test"] and args["outdir_script"] == ".":
    args["outdir_script"] = os.getcwd()

# script
# we have two vcf files to prepare (ref and query referential
from reformat_vcf import reformat_vcf
reformated_vcf1 = reformat_vcf(args["vcf1"], args["outdir"])
reformated_vcf2 = reformat_vcf(args["vcf2"], args["outdir"])

# detecting which is according to coordinate ref or query
if "_ref_snps.vcf" in args["vcf1"]:
    ref_vcf = reformated_vcf1
    query_vcf = reformated_vcf2
else:
    ref_vcf = reformated_vcf2
    query_vcf = reformated_vcf1

# detection of which one should be used as ref or query as coordinate system for annotation is in function
from create_run_vcf_annotator import create_run_vcf_annotator
create_run_vcf_annotator(ref_vcf, query_vcf, args["gbff1"] , args["gbff2"], args["outdir"], args["outdir_script"])

