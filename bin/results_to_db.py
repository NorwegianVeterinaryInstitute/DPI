#!/usr/bin/env python

import argparse

# import sys
# import os
import sqlite3

# import pandas as pd
# import json
# import sqlalchemy

# import numpy as np
# sys.path.append(os.getcwd())
import funktions as fk


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
        "If not providentifiered, the database will default to: DPI.sqlite",
    )
    parser.add_argument(
        "--comment",
        required=False,
        help="Comment for the database entries.\n"
        "Long comments that include spaces must be surounded by '' ",
    )
    parser.add_argument(
        "--identifierentifier",
        required=False,
        help="Either the sample_identifier or the pair identifierentifier.\n"
        "   - sample_identifier: the sample identifierentifier (for results of type json).\n"
        "   - The pair identifierentifier for any other result type.",
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
        print("Example usage:")
        print(" python results_to_db.py --database my_database.sqlite \\")
        print("  --comment 'Analysis on 2023-10-01' \\")
        print("  --identifier sample123 \\")
        print("  --result_type json \\")
        print("  --result_file file.json")
        return

    # Check if required arguments are providentifiered when not version or example
    if (
        not args.comment
        or not args.identifierentifier
        or not args.result_type
        or not args.result_file
    ):
        parser.error(
            "The following arguments are required: --comment, --identifierentifier, --result_type, --result_file"
        )
        return

    # Arguments usage definition
    db_path = args.database
    comment = args.comment
    identifierentifier = args.identifierentifier
    result_type = args.result_type
    result_file = args.result_file

    # Connect to the database
    db_conn = sqlite3.connect(db_path)

    # Process the result files
    fk.process_result_file(result_file, result_type, identifierentifier, db_conn)

    # Close the database connection
    db_conn.close()


if __name__ == "__main__":
    main()
