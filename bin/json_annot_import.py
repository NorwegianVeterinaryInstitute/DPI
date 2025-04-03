#!/usr/bin/env python

import argparse
import sys
import os
import pandas as pd
import json
import sqlalchemy
import numpy as np


# %% functions
def df_to_database(df, db_file, table_name, if_exists="replace"):
    """appends data to at SQLite table in a database.
    If the table does not exist: creates the table
    NEED TO APPEND IF DATA EXIST - CHECK AND ONLY UPDATE IF NOT
    :param df a pandas pdf
    :param db_file sqlite database file
    :param table_name sqlite table
    :param if_exists pandas df.to_sql: if_exists 'replace','append','fail'
    """
    db_abspath = os.path.abspath(db_file)
    try:
        # test if file exist
        open(db_abspath)
    except OSError:
        print("The database do not exist. Creating the database")
        # abspath for windows compatibilty
        os.makedirs(os.path.dirname(db_abspath), exist_ok=True)
    finally:
        db = sqlalchemy.create_engine(f"sqlite:////{db_abspath}")

        # if the table does not exist or exist and no more columns - we put data directly
        try:
            df.to_sql(table_name, db, if_exists=if_exists, index=False)
        # else: check if all columns exist in table
        # https://stackoverflow.com/questions/58153158/to-sql-add-column-if-not-exists-sqlalchemy-mysql
        except:
            target_cols = pd.read_sql_query(
                f"select * from {table_name} limit 1;", db
            ).columns.tolist()
            df_cols = df.columns.tolist()
            missing_columns = set(df_cols) - set(target_cols)

            if missing_columns != set():
                # This is not elegent solution but did not manage to add directly column via sqlalchemy
                temp_df = pd.read_sql_query(f"SELECT * FROM {table_name};", db)

                for missing_col in list(missing_columns):
                    temp_df.insert(len(temp_df.columns), missing_col, "NaN")

                # add updated database
                temp_df.to_sql(table_name, db, if_exists="replace", index=False)
                del temp_df

            # add latest data - at the end
            df.to_sql(table_name, db, if_exists=if_exists, index=False)

        finally:
            # ensure that db stop (not sure necessary here)
            db.dispose()


# %% SCRIPT
if __name__ == "__main__":
    args = parse_args(sys.argv[1:])

    # %% Action
    f = open(args["json"])
    data = json.load(f)
    f.close()

    info = prep_info_df(data, args["sample_id"])
    df_to_database(info, args["database"], "annotation_info", if_exists="append")

    features = prep_features_df(data, args["sample_id"])
    df_to_database(
        features, args["database"], "annotation_features", if_exists="append"
    )

    sequences = prep_sequences_df(data, args["sample_id"])
    df_to_database(
        sequences, args["database"], "annotation_sequences", if_exists="append"
    )
