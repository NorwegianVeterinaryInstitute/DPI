#!/usr/bin/env python
# Wrapper : processing each type of results files. A single file at the time
# Improved with geminis help (2025-04-10)

# SECTION : Imports
import argparse
import os
import json
import datetime

from funktions.json_to_df import prep_info_df
from funktions.json_to_df import prep_features_df
from funktions.json_to_df import prep_sequences_df
from funktions.gff_to_df import gff_to_df
from funktions.vcf_to_df import vcf_to_df
from funktions.stats_to_df import stats_to_df
from funktions.comment_df import create_comment_df
from funktions.create_table import create_table
# !SECTION

# SECTION : Functions definitions
# NOTE helper
def determine_result_type(file_name):
    """
    Helper: Determines the type of result for correct processing
    Returns the result type

    Args:
        file_name (str): basename of the result file.
    """

    if file_name.endswith(".json"):
        return "json"
    elif file_name.endswith(".gff"):
        return "gff"
    elif file_name.endswith(".vcf"):
        return "vcf"
    elif file_name.endswith("_stat.out"):
        return "stats"
    else:
        return None


def process_result_file(file_path, identifier,db_file, comment):
    """
    Processes a single result file, transforms it into a table
    and inserts it into the specified SQLite database.

    Args:
        file_path (str): Path to the result file.
        identifier (str): The identifier (pair or sample_id).
        db_file (str): Path to the SQLite database file.
        comment (str): Comment for the database entries.
    """
    file_name = os.path.basename(file_path)
    print(f"Processing file: {file_name} for {identifier}")

    result_type = determine_result_type(file_name)
    
    try:
        # NOTE: creates the db it if does not exists
        db_conn = sqlite3.connect(db_file)
        cursor = db_conn.cursor()
        
        
        if result_type == "json":
            with open(file_path, "r") as f:
                data = json.load(f)

            # NOTE: 3 types of data to extract for the json file
            try:
                info_df = prep_info_df(data, identifier)
                create_table(info_df, "info", identifier, file_name, db_file)
            except Exception as e:
                print(f"Error processing info_df for {identifier} filename {file_name}: {e}")

            try:
                features_df = prep_features_df(data, identifier)
                create_table(features_df, "features", identifier, file_name, db_file)
            except Exception as e:
                print(f"Error processing features_df for {identifier} filename {file_name}: {e}")

            try:
                sequences_df = prep_sequences_df(data, identifier)
                create_table(sequences_df, "sequences", identifier, file_name, db_file)
            except Exception as e:
                print(f"Error processing sequences_df for {identifier} filename {file_name}: {e}")

        # NOTE : processing different types of gff files
        elif result_type == "gff":
            df = gff_to_df(file_path)

            if "_query_blocks" in file_name:
                create_table(df, "query_blocks", identifier, file_name, db_file)
            elif "_query_snps" in file_name:
                create_table(df, "query_snps", identifier, file_name, db_file)
            elif "_query_struct" in file_name:
                create_table(df, "query_struct", identifier, file_name, db_file)
            elif "_query_additional" in file_name:
                create_table(df, "query_additional", identifier, file_name, db_file)
            elif "_query_snps_annotated" in file_name:
                create_table(df, "query_snps_annotated", identifier, file_name, db_file)
            elif "_ref_blocks" in file_name:
                create_table(df, "ref_blocks", identifier, file_name, db_file)
            elif "_ref_snps" in file_name:
                create_table(df, "ref_snps", identifier, file_name, db_file)
            elif "_ref_struct" in file_name:
                create_table(df, "ref_struct", identifier, file_name, db_file)
            elif "ref_additional" in file_name:
                create_table(df, "ref_additional", identifier, file_name, db_file)
            else:
                print(f"Warning: Unknown GFF subtype for {result_type} for {identifier}. Filepath {file_path}. Skipping {file_path}.")
                return

        # NOTE: processing different types of vcf files
        elif result_type == "vcf":
            df = vcf_to_df(file_path)

            if "_ref_snps_annotated" in file_name:
                create_table(df, "ref_snps_annotated", identifier, file_name, db_file)
            elif "_query_snps_annotated" in file_name:
                create_table(df, "query_snps_annotated", identifier, file_name, db_file)
            else:
                print(f"Warning: Unknown VCF subtype for {result_type} for {identifier}. Skipping {file_name}.")
                return

        elif result_type == "stats":
            df = stats_to_df(file_path)
            if "_stat.out" in file_name:
                create_table(df, "stat_file", identifier, file_name, db_file)
            else:
                print(f"Warning: Unknown stats subtype for {result_type} for {identifier}. Skipping {file_path}.")
                return

        # NOTE : adding comment table for each type of file processed in the database
        comment_df = create_comment_df(identifier, comment)
        create_table(comment_df, "comments", identifier, file_name, db_file)

        db_conn.commit()
        print(f"Processed and inserted: {file_name} for identifier {identifier}")

    except Exception as e:
        print(f"Error processing {file_path} for identifier {identifier}: {e}")
        if 'db_conn' in locals():
            db_conn.rollback()
    finally:
        if 'db_conn' in locals():
            db_conn.close()
# !SECTION

# SECTION MAIN
if __name__ == "__main__":
    # SECTION : Argument parsing
    parser = argparse.ArgumentParser(description="Process a result file and add it to an SQLite database.")
    parser.add_argument("--file_path", required=True, help="Path to the result file",)
    parser.add_argument("--identifier", required=True, help="Identifier for the data",)
    parser.add_argument("--db_file", required=True, help="Path to the SQLite database file",)
    parser.add_argument("--comment", default="", required=False, help="Optional comment for the database entry",)

    args = parser.parse_args()
    # !SECTION
    
    # SECTION : Check if required arguments are provided
    if not all([args.file_path, args.identifier, args.db_file]):
        parser.error(
            "The following arguments are required: --file_path, --identifier, --db_file"
        )
        sys.exit(1)      
    # !SECTION
    
    # SECTION : Handling of example
    if args.example:
        logging.info("Example usage:")
        logging.info("python process_result_file.py --file_path <path_to_file> --identifier <identifier> --db_file <db_file>")")
        return
    # !SECTION
    

    
    # SECTION : Login info output
    log_file_name = f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_process_result_file.log"

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file_name, mode="w"),
            logging.StreamHandler(sys.stdout),
        ],
        )
    # !SECTION
    
    # SECTION : SCRIPT : Merge the result files
    try:
        logging.info(f"processing result file ${args.file_path} for {args.identifier}")
        process_result_file(args.file_path, args.identifier, args.db_file, args.comment)
    except Exception as e:
        logging.error(f"An error occurred during the processing of result files: {e}")
        logging.error(f"Check {log_file_name} for more details")
    # !SECTION
# !SECTION