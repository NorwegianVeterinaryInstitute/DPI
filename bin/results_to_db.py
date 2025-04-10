#!/usr/bin/env python
# rewritten by gemini 2025-07-10

# SECTION : Imports
import sys
import logging
import sqlite3
import argparse
import funktions.process_result_file as process_result_file
import datetime
# !SECTION


# SECTION: MAIN 
if __name__ == "__main__":
    # SECTION: Argument parsing
    parser = argparse.ArgumentParser(
        prog="results_to_db.py", usage="%(prog)s [options]", 
        description="Wrangle results and insert into SQLite database.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        add_help=True,)

    # Version and example arguments (optional)
    parser.add_argument(
        "--example",
        action="store_true",
        help="Show an example of usage and exit.",
        )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.0.2",
        help="Print the script version and exit.",
        )
# Required arguments
    parser.add_argument(
        "--database",
        action="store",
        default="output.sqlite",
        required=False,
        help="Path to a SQLite database file where results will be stored.\n"
        "If the path does not exist, it will be created.\n"
        "If not provided, the database will default to: DPI.sqlite",
        )
    parser.add_argument(
        "--comment",
        action="store",
        default="",
        required=False,
        help="Comment for the database entries.\n"
        "Long comments that include spaces must be surounded by '' ",
        )
    # NOTE: The identifier is required for the process_result_file function but the requirement is 
    # hanlded afterwards. To allow control of input. Then it is not required in the parser.
    parser.add_argument(
        "--identifier", 
        required=False,
        help="Either the sample_identifier or the pair identifier.\n"
        "   - sample_identifier: the sample identifier (for results of type json).\n"
        "   - The pair identifier for any other result type.",
        )
    parser.add_argument(
        "--result_file",
        required=False,
        help="result file path.",
    )

    args = parser.parse_args()
    # !SECTION
    
    # SECTION : Check if required arguments are provided
    if not all([args.identifier, args.result_file,]):
        parser.error(
        "The following arguments are required: --comment, --identifier, --result_file"
        )
        sys.exit(1)
    # !SECTION
    
    # SECTION : Handling of examples
    if args.example:
        logging.info("Example usage:")
        logging.info("python results_to_db.py --database my_database.sqlite \\")
        logging.info(" --comment 'Analysis on 2023-10-01' \\")
        logging.info(" --identifier sample123 \\")
        logging.info(" --result_file file.json")
        sys.exit(0)
    # !SECTION
    

    # SECTION : Logging info output
    log_file_name = f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_results_to_db.log"
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file_name, mode="w"),
            logging.StreamHandler(sys.stdout),
        ],
    )
    # !SECTION
    
    # SECTION : Process result files
    try:
        logging.info(f"Processing {args.identifier} in {args.result_file}")
        db_conn = sqlite3.connect(args.database)
        process_result_file(args.result_file, args.identifier, db_conn, args.comment)
        db_conn.close()
    except Exception as e:
        logging.error(f"An error occurred during processing of {args.identifier}: {e}")
        logging.error(f"Check {log_file_name} for more details")
    # !SECTION


