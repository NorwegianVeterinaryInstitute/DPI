## %% database interaction
### Still report error when must create path otherwise working
import os
import sqlalchemy

def df_to_database(df, db_file, table_name, if_exists='replace'):
    """ appends data to at SQLite table in a database.
        If the table does not exist: creates the table
        :param df  a pandas pdf
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
        df.to_sql(table_name, con=db, if_exists=if_exists, index=False)
        db.dispose()


# TEST
#df_to_database(test4_df, "test.sqlite",  "test_table", "append")
#df_to_database(test4_df, "/home/vi2067/Documents/test/test/test.sqlite",  "test_table", "append")



