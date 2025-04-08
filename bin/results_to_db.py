#!/usr/bin/env python

import argparse
import sys
import logging
import sqlite3


# sys.path.append(os.getcwd())
import funktions as fk


# ANCHOR : Login info output
log_file_name = "results_to_db.log"
# FIXME : Change the log file name to include the when it runs the other functions
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file_name, mode="w"),
        logging.StreamHandler(sys.stdout),
    ],
    )


# ANCHOR : Main Parsing arguments and running
def main():
    parser = argparse.ArgumentParser(
        prog="results_to_db.py",
        usage="%(prog)s [options]",
        description="Wrangle results and insert into SQLite database.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        add_help=True,

    )
    # Version and example arguments (optional)
    parser.add_argument(
        "--example", action="store_true", help="Show an example of usage and exit."
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
        default="DPI.sqlite",
        required=False,
        help="Path to the SQLite database file.\n"
        "If the path does not exist, it will be created.\n"
        "If not provided, the database will default to: DPI.sqlite",
    )
    parser.add_argument(
        "--comment",
        required=False,
        help="Comment for the database entries.\n"
        "Long comments that include spaces must be surounded by '' ",
    )
    parser.add_argument(
        "--identifier",
        required=False,
        help="Either the sample_identifier or the pair identifier.\n"
        "   - sample_identifier: the sample identifier (for results of type json).\n"
        "   - The pair identifier for any other result type.",
    )
    parser.add_argument(
        "--result_type",
        action="store",
        required=False,
        help="The type of result being processed.\n"
        "   - json: JSON annotation file from Bakta\n"
        "   - gff: GFF file",
    )
    parser.add_argument(
        "--result_file",
        required=False,
        help="result file path.",
    )

    args = parser.parse_args()

    # Handling of examples
    if args.example:
        logging.info("Example usage:")
        logging.info(" python results_to_db.py --database my_database.sqlite \\")
        logging.info("  --comment 'Analysis on 2023-10-01' \\")
        logging.info("  --identifier sample123 \\")
        logging.info("  --result_type json \\")
        logging.info("  --result_file file.json")
        return

    # Check if required arguments are provided when not version or example
    if (
        not args.comment
        or not args.identifier
        or not args.result_type
        or not args.result_file
    ):
        parser.error(
            "The following arguments are required: --comment, --identifier, --result_type, --result_file"
        )
        return

    # Arguments usage definition
    db_path = args.database
    comment = args.comment
    identifier = args.identifier
    result_type = args.result_type
    result_file = args.result_file

    # Connect to the database
    db_conn = sqlite3.connect(db_path)

    # Process the result files
    try:
        if result_type == "json":
            logging.info(f"main: >Processing {result_type} for {identifier} in {result_file}")
            fk.process_result_file(result_file, result_type, identifier, db_conn, comment=None)
        else:
            logging.info(f"main: >Processing {result_type} for {identifier} in {result_file}")
            fk.process_result_file(result_file, result_type, identifier, db_conn, comment)
    except Exception as e:
        logging.error(f"main: >An error occurred during processin of {result_type} for {identifier}: {e}")
        logging.error(f"main: >Check {log_file_name} for more details")


    logging.info(f"{result_type} result processed for identifier: {identifier}")
    
    # Close the database connection
    db_conn.close()


if __name__ == "__main__":
    main()
