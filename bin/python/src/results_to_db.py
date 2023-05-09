import argparse
import os
import sys

parser = argparse.ArgumentParser(
    prog="prep_vcf_annotator.py",
    description='Wrangling results and appending to database',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument("--resdir",
                    action="store",
                    required=True,
                    help="directory where all results to include in the database are deposited")
parser.add_argument("--database",
                    action="store",
                    default="nucdiff.sqlite",
                    required=True,
                    help="path/name of the database. If it does not exists, it will be created, otherwise results are append")
parser.add_argument("--comment",
                    action="store",
                    default=False,
                    help="Comment to add to the tables in the database (eg. date analysis, type assembly)")

parser.add_argument("--test",
                    action="store",
                    default=False,
                    help="Source paths for testing. Paths defined in test_paths.py")

args = vars(parser.parse_args())

# sourcing functions dir
sys.path.append(os.path.dirname(__file__))

# default test directories here
if args["test"]:
    #sys.path.append(os.path.dirname(__file__) + "/" + "test")
    import test_paths
    args["resdir"] = os.getenv("OUTPUTDIR")

if not args["test"] and args["resdir"] == ".":
    args["resdir"] = os.getcwd()

# %% script
from helpers.detect_result_files import detect_result_files
from database.wrapper_gff_to_db import wrapper_gff_to_db
from database.wrapper_vcf_to_db import wrapper_vcf_to_db
from database.wrapper_stat_to_db import wrapper_stat_to_db
## %% getting results files to add to database
res_files_dict = detect_result_files(args["resdir"])
id_dict = res_files_dict["id"]
# %% getting df and adding the results to database
# %% could be improved function by filetype detection ... but ok for now
## %% the query_files to db
query_files_dict = res_files_dict["query_files"]
for key in query_files_dict.keys():
   wrapper_gff_to_db(
       gff_file=query_files_dict[key][0], id_dict=id_dict, gff_pattern=query_files_dict[key][1],
       comment=args["comment"], db_file=args["database"],
       table_name=key, if_exists='append')

## %% the ref_files to db
ref_files_dict = res_files_dict["ref_files"]
for key in ref_files_dict.keys():
   wrapper_gff_to_db(
       gff_file=ref_files_dict[key][0], id_dict=id_dict, gff_pattern=ref_files_dict[key][1],
       comment=args["comment"], db_file=args["database"],
       table_name=key, if_exists='append')

## %% the stat_file to db
stat_files_dict = res_files_dict["stat_files"]

for key in stat_files_dict.keys():
    wrapper_stat_to_db(stat_file=stat_files_dict[key][0],
                       id_dict=id_dict, stat_pattern=stat_files_dict[key][1],
                       comment=args["comment"], db_file=args["database"],
                       table_name=key, if_exists='append')

## %% the annotated_vcf to db
vcf_files_dict=res_files_dict["annotated_vcf_files"]

for key in vcf_files_dict.keys():
    wrapper_vcf_to_db(vcf_file=vcf_files_dict[key][0], id_dict=id_dict, vcf_pattern=vcf_files_dict[key][1],
                      comment=args["comment"], db_file=args["database"],
                      table_name=key, if_exists='append')


# Test
# IN="/home/vi2067/Documents/onedrive_sync/NEW_WORK/2_Projects/2023/1_2023_Lm_ost_er_ikke_ost/ost_er_ikke_ost/code/python/inout"
#python src/results_to_db.py --resdir $IN --database /home/vi2067/Documents/test/script_test.sqlite --comment "test_script"

