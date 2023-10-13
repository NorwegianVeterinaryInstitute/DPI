import argparse
import sys
import os
import pandas as pd
import json
import sqlalchemy 

# https://realpython.com/command-line-interfaces-python-argparse/ is good start
def parse_args(args):

    parser = argparse.ArgumentParser(
        prog="json_annot_import.py",
        usage=None, 
        description='Import the total annotation json file from bakta and transform it to a panda df.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        add_help=True
        )

    parser.add_argument("--json",
                        action="store",
                        required=True,
                        help="json annotation file from bakta")
    parser.add_argument("--database",
                        action="store",
                        default="nucdiff.sqlite",
                        required=False,
                        help="path/name of the database. If it does not exists, it will be created, otherwise results are append")
    parser.add_argument("--sample_id",
                        action="store",
                        default=".",
                        help="sample_id that will be used")
    parser.add_argument("--version",
                        action="version",
                        version = "%(prog)s 0.0.1",
                        help="print the version of the script")
    
    args = vars(parser.parse_args())
    return args


# %% functions
def df_to_database(df, db_file, table_name, if_exists='append'):
    """ appends data to at SQLite table in a database.
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
        
        # check if column exists 
        # https://stackoverflow.com/questions/58153158/to-sql-add-column-if-not-exists-sqlalchemy-mysql
        target_cols = pd.read_sql_query(f"select * from {table_name} limit 1;", db).columns.tolist()
        df_cols = df.columns.tolist()
        missing_columns = set(df_cols) - set(target_cols) 
        
        if missing_columns != set():
            # This is not elegent solution but did not manage to add directly column via sqlalchemy
            temp_df = pd.read_sql_query(f"SELECT * FROM {table_name};", db)
            
            for missing_col in list(missing_columns):
                temp_df.insert(len(temp_df.columns), missing_col, "NaN")
                
            # add updated database
            temp_df.to_sql(table_name, db, if_exists="replace", index=False)
            del(temp_df)
        
        
        # add latest data - at the end
        df.to_sql(table_name, db, if_exists=if_exists, index=False)
        
        # ensure that db stop (not sure necessary here)    
        db.dispose()


# json data will go into 3 different tables (for archive)
def prep_info_df(json_object, sample_id):
    """_summary_
    prepare the info dataframe from the json annotation

    Args:
        json_object (_dict_): _annotation json from bakta_
        sample_id (_str_): _sample id to add to the table_
    """
    # create df for each separate key
    genome = pd.json_normalize(json_object['genome'])
    stats= pd.json_normalize(json_object['stats'])
    run = pd.json_normalize(json_object['run'])
    version = pd.json_normalize(json_object['version'])
    ## joining df for simple info - can go into own table
    info = pd.concat([genome, stats, run, version], axis = 1)
    info.insert(0, "sample_id", sample_id)
    return info



def prep_features_df(json_object, sample_id):
    """_summary_
    prepare the features dataframe from the json annotation

    Args:
        json_object (_dict_): _annotation json from bakta_
        sample_id (_str_): _sample id to add to the table_
    """
    features = pd.json_normalize(data['features'])
    features.insert(0, "sample_id", sample_id)
    # need to change list types to string
    # we do not want to split those for now
    features = features.map(str)
    return features


def prep_sequences_df(json_object, sample_id):
    """_summary_
    prepare the sequences dataframe from the json annotation

    Args:
        json_object (_dict_): _annotation json from bakta_
        sample_id (_str_): _sample id to add to the table_
    """
    sequences = pd.json_normalize(data['sequences'])
    sequences.insert(0, "sample_id", sample_id)
    
    # cleaning the sequences table
    sequences[["len", "cov", "corr", "origname", "sw", "date"]] = sequences["orig_description"].str.split(" ", expand=True)
    sequences[["genus", "species", "gcode", "topology"]] = sequences["description"].str.split(" ", expand=True)
    sequences.drop(labels= ["orig_description", "description"], axis = 1)
    sequences.replace(["^.*=","]"], "", inplace = True, regex = True)
    return sequences


# %% SCRIPT
if __name__ == '__main__':
    args = parse_args(sys.argv[1:])
    
    #%% Action
    f = open(args["json"])
    data = json.load(f)
    f.close()

    info = prep_info_df(data, args["sample_id"])
    df_to_database(info,args["database"], "annotation_info",if_exists='append')
    
    features= prep_features_df(data, args["sample_id"])
    df_to_database(features,args["database"], "annotation_features",if_exists='append')
    
    sequences=prep_sequences_df(data, args["sample_id"])
    df_to_database(sequences,args["database"], "annotation_sequences",if_exists='append')
