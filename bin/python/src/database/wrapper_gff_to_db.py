# gives the df to append to sqlite databse
from wrangling.gff_to_df import gff_to_df
from database.df_to_database import df_to_database


def wrapper_gff_to_db(gff_file, id_dict, gff_pattern, comment, db_file, table_name, if_exists = 'append'):
    """
    transforms gff file to pandas df then appends to sqlite
    :param gff_file nucdiff result gff_file
    :param id_dict dictionary containing ref, query ids (from detect_result_files)
    :param gff_pattern the pattern that is to remove from basename to obtain ref_query
    :param comment a string describing additional data to add to the table (or None)
    :param db_file sqlite database file
    :param if_exists pandas df.to_sql: if_exists 'replace','append','fail'
    """

    df = gff_to_df(gff_file = gff_file, id_dict = id_dict, gff_pattern = gff_pattern, comment = comment)

    if not df is None:
        df_to_database(df = df, db_file = db_file, table_name = table_name, if_exists = if_exists)
    else:
        print(f"No data to add for {gff_file}")

