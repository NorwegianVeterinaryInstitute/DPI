import argparse
import os
import sys

parser = argparse.ArgumentParser(
    prog="prep_nucdiff.py",
    description="Step1. Prepare run nucdiff. Find longest assembly in the pair, output nucdiff run script",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument("--fasta1",
                    action="store",
                    required=True,
                    help="Fasta file for isolate 1 (fna) produced by Bakta during annotation process")
parser.add_argument("--fasta2",
                    action="store",
                    required=True,
                    help="Fasta file for isolate 2 (fna) produced by Bakta during annotation process")
parser.add_argument("--suffix",
                    action="store",
                    default=".fna",
                    help="Suffix of fasta1 and fasta2 files")
parser.add_argument("--outdir",
                    action="store",
                    default=".",
                    help="path of output directory for nucdiff")
parser.add_argument("--outdir_script",
                    action="store",
                    default=".",
                    help="path where the script to run nucdiff will be deposited")
parser.add_argument("--test",
                    action="store",
                    default=False,
                    help="Source paths for testing. Paths defined in test_paths.py")

args = vars(parser.parse_args())

# sourcing functions dir
sys.path.append(os.path.dirname(__file__) + "/" + "diff")

# script
if args["test"]:
    sys.path.append(os.path.dirname(__file__) + "/" + "test")
    import test_paths
    #print("INPUTDIR" + os.getenv('INPUTDIR'))
    work_dir = os.getenv('INPUTDIR')
    pc_out = os.getenv("OUTPUTDIR")
    args["fasta1"] = work_dir + args["fasta1"]
    args["fasta2"] = work_dir + args["fasta2"]
    args["outdir"] = pc_out
    args["outdir_script"] = pc_out

# get the paths if ".":
## should not work for test
if not args["test"] and args["outdir"] == ".":
    args["outdir"] = os.getcwd()
if not args["test"] and args["outdir_script"] == ".":
    args["outdir_script"] = os.getcwd()

# so if test can set $INPUTDIR/fasta1
from chose_ref_query import chose_ref_query
ref_file, query_file, nucdiff_pattern = chose_ref_query(args["fasta1"], args["fasta2"], args["suffix"])

# Create the nucdiff run command
from create_run_nucdiff import create_run_nucdiff
create_run_nucdiff(ref_file, query_file, args["outdir"], nucdiff_pattern, args["outdir_script"])

# Test commands
# python prep_nucdiff.py --fasta1 SRR11262033.fna --fasta2 SRR11262179.fna --test True
# python src/prep_nucdiff.py --fasta1 ${INPUT}/SRR11262033.fna --fasta2 ${INPUT}/SRR11262179.fna --outdir .
