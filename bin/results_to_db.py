import argparse
import sys
import os
import re
import pandas as pd
import gffpandas.gffpandas as gffpd
import sqlalchemy
import glob
import functools
import operator

def parse_args(args):
    parser = argparse.ArgumentParser(
        prog="results_to_db.py",
        description='Wrangling results and appending to database',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("--resdir",
                        default=".",
                        action="store",
                        required=False,
                        help="directory where all results to include in the database are deposited")
    parser.add_argument("--database",
                        action="store",
                        default="nucdiff.sqlite",
                        required=False,
                        help="path/name of the database. If it does not exists, it will be created, otherwise results are append")
    parser.add_argument("--comment",
                        action="store",
                        default="NA",
                        help="Comment to add to the tables in the database (eg. date analysis, type assembly)")
    args = vars(parser.parse_args())
    return args

########################################################################################################################
# %% Functions
## %% helper detect ref_query_patterns
def ref_query_patterns(dir):
    """
    detect the difference ref query patterns that will need to be added in database
    :returns list of existing ref_query
    """
    list_path = glob.glob(dir + "/*_stat.out")
    return list(map(lambda i: os.path.basename(i).replace("_stat.out", ""), list_path))

#%% helper : return all the files per pattern
def res_files_per_pattern(dir, list_patterns):
    """
    return each list element contain all the files per pattern
    """
    return list(map(lambda pattern: glob.glob(dir + "/" + pattern + "*"), list_patterns))

## %% detect all results files per pattern
def detect_result_files(res_files_list):
    """
    organize the detected result files for ONE ref_query pattern and create a dictionary so it can be wrangled correctly
    builds on res_files_per_pattern
    :res_files_list a flat list of all result files
    :returns dictionary of list file paths to analyze in different categories id(ref,query), query_files, ref_files, stat_file
    """
    # Prepare creating the dictionary with all files types
    # sorting lists so that ref_query order always identical
    # query
    query_blocks_files = sorted([s for s in res_files_list if any(xs in s for xs in ['_query_blocks.gff'])])
    query_snps_gff_files = sorted([s for s in res_files_list if any(xs in s for xs in ['_query_snps.gff'])])
    query_struct_files = sorted([s for s in res_files_list if any(xs in s for xs in ['_query_struct.gff'])])
    query_additional_files = sorted([s for s in res_files_list if any(xs in s for xs in ['_query_additional.gff'])])
    query_snps_annotated_files = sorted([s for s in res_files_list if any(xs in s for xs in ['_query_snps_annotated.vcf'])])
    # ref
    ref_blocks_files = sorted([s for s in res_files_list if any(xs in s for xs in ['_ref_blocks.gff'])])
    ref_snps_gff_files = sorted([s for s in res_files_list if any(xs in s for xs in ['_ref_snps.gff'])])
    ref_struct_files = sorted([s for s in res_files_list if any(xs in s for xs in ['_ref_struct.gff'])])
    ref_additional_files = sorted([s for s in res_files_list if any(xs in s for xs in ['_ref_additional.gff'])])
    ref_snps_annotated_files = sorted([s for s in res_files_list if any(xs in s for xs in ['_ref_snps_annotated.vcf'])])
    # stat
    stat_files_list = sorted([s for s in res_files_list if any(xs in s for xs in ['_stat.out'])])

    # creating dictionaries
    query_files = {'query_blocks': (query_blocks_files, "_query_blocks.gff"),
                   'query_snps_gff': (query_snps_gff_files, "_query_snps.gff"),
                   'query_struct': (query_struct_files, "_query_struct.gff"),
                   'query_additional': (query_additional_files, "_query_additional.gff")}

    ref_files = {'ref_blocks': (ref_blocks_files,"_ref_blocks.gff"),
                 'ref_snps_gff': (ref_snps_gff_files,"_ref_snps.gff"),
                 'ref_struct': (ref_struct_files,"_ref_struct.gff"),
                 'ref_additional': (ref_additional_files,  "_ref_additional.gff")}

    annotated_vcf_files = {"ref_snps_annotated": (ref_snps_annotated_files,  "_ref_snps_annotated.vcf"),
                          "query_snps_annotated": (query_snps_annotated_files, "_query_snps_annotated.vcf")}

    stat_files = {'stat_file': (stat_files_list, "_stat.out")}


    # get the ref and query id - ordered in the tuple
    prefixes = list(map(lambda x : re.sub("_stat.out", '', os.path.basename(x)), stat_files_list))
    ref_query_ids = list(map(lambda x: re.split('_', x), prefixes))
    ref_ids, query_ids = list(zip(*ref_query_ids ))
    id = {'ref': ref_ids, 'query': query_ids}

    # global dict
    files_dict = {'id': id,
                  'query_files': query_files,
                  'ref_files': ref_files,
                  'stat_files': stat_files,
                  "annotated_vcf_files": annotated_vcf_files}
    return files_dict

## %% table to database
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

## %% helper get ids
def get_ids(file, pattern, sep="_"):
    """ Getting ids from files path from basename eg. to add columns before adding to database
        by default ref_query
    :param file: path of file to get
    :param pattern pattern to remove (that is not ID1_ID2)
    :param sep separator used
    """
    file_basename = os.path.basename(file)
    return file_basename.replace(pattern, "").split(sep)

## %% gff
def gff_to_df(gff_file, id_dict, gff_pattern, comment = None):
    """
    transforms gff file to pandas df. Appends query and ref names, result file name, and comment field (used for info about analysis)
    :param gff_file nucdiff result gff_file
    :param id_dict dictionary containing ref, query ids (from detect_result_files)
    :param gff_pattern the pattern that is to remove from basename to obtain ref_query
    :param comment a string describing additional data to add to the table (or None)
    :return df if gff_file length >1 otherwise returns None
    """

    df = gffpd.read_gff3(gff_file)
    ref_gff, query_gff = get_ids(gff_file, gff_pattern)
    file_name = os.path.basename(gff_file)

    # Sanity - control detected ids are matching
    try:
        ref_gff == id_dict["ref"] and query_gff == id_dict["query"]
    except NameError:
        sys.exit("the detected reference and query id do not match. Review your command or debug")
    else:
        # dealing with empty gff (eg. query_additional): only one line
        with open(gff_file, "r") as f:
            file_len = len(f.readlines())
            f.close()
        if file_len <= 1:
            return None
        else:
            return df.attributes_to_columns().assign(_REF=id_dict["ref"],
                                                     _QUERY=id_dict["query"],
                                                     _RES_FILE=file_name,
                                                     _COMMENT=comment)
def wrapper_gff_to_db(gff_file, id_dict, gff_pattern, comment, db_file, table_name, all_keys, if_exists = 'append'):
    """
    transforms gff file to pandas df then appends to sqlite
    :param: gff_file nucdiff result gff_file
    :param: id_dict dictionary containing ref, query ids (from detect_result_files)
    :param: gff_pattern the pattern that is to remove from basename to obtain ref_query
    :param: comment a string describing additional data to add to the table (or None)
    :param: db_file sqlite database file
    :param: table_name name of table in database to use
    :param: all keys - list_ all the keys existing for this type of table
    :param if_exists pandas df.to_sql: if_exists 'replace','append','fail'
    """

    df = gff_to_df(gff_file = gff_file, id_dict = id_dict, gff_pattern = gff_pattern, comment = comment)

    if not df is None:
        col_to_add = list(set(all_keys) - set(list(df.columns)))
        for value_col in col_to_add:
            df[f'{value_col}']= None
        df_to_database(df = df, db_file = db_file, table_name = table_name, if_exists = if_exists)
    else:
        print(f"No data to add for {gff_file}")

## %% vcf
def annotated_vcf_to_df(file):
    """
    Read the annotated vcf and returns a pandas dataframe
    :param file: annotated vcf
    :return: pandas dataframe
    """
    # Helpers
    def row_to_dic_helper(row):
        """
        Returns a dictionary
        splitting columns at ; and =
        :param row: row
        :return: dictionary
        """
        list_row = re.split(';|=', row)
        # keys : values
        return dict(zip(list_row[::2], list_row[1::2]))

    # get position start table
    start_row = 0
    with open(file) as input:
        for line in input:
            if "#CHROM" in line:
                 break

            start_row += 1
    input.close()
    # get the body
    df = pd.read_table(file, sep="\t", skiprows= start_row, skip_blank_lines=True, index_col=None)
    # each row to dict
    df["INFO"] = df["INFO"].apply(lambda row: row_to_dic_helper(row))
    # normalize INFO
    df2 = pd.json_normalize(df['INFO'])
    # concatenate df
    return pd.concat([df.drop("INFO", axis=1).reset_index(drop=True), df2.reset_index(drop=True)], axis=1)


# Getting the unique keys previous to database creation
def unique_df_type_keys(list_data, type_data, append_col = ["_REF", "_QUERY", "_RES_FILE", "_COMMENT" ]):
    """
    finds the unique keys between a list of files of the same type
    :param: list_data : the list of files to find the keys in
    :param: type_data :'gff', 'vcf', 'stat'
    :param: append_col : list of column names to append to the datastructure (required for vcf)
    :return list of unique keys
    """
    # In case not all columns were there
    new_keys = append_col.copy()
    if type_data == "gff":
        for file in list_data:
            try:
                gffpd_df = gffpd.read_gff3(file)
                df = gffpd_df.attributes_to_columns()
                new_keys = list(set(new_keys + list(df.columns)))
            except:
                print(f"No data to add for {file}")
    elif type_data == "vcf":
        for file in list_data:
            try:
                df = annotated_vcf_to_df(file)
                new_keys = list(set(new_keys + list(df.columns)))
            except:
                print(f"No data to add for {file}")
    elif type_data == "stat":
        for file in list_data:
            try:
                df = pd.read_table(file, sep="\t", header=None, names=["param", "value"],
                                   skip_blank_lines=True, index_col=None)
                df = df[df.value.notnull()]
                new_keys = list(set(new_keys + list(df.columns)))
            except:
                print(f"No data to add for {file}")

    return new_keys

def wrapper_vcf_to_db(vcf_file, id_dict, vcf_pattern, comment, db_file, table_name, all_keys, if_exists = 'append'):
    """
    transforms annotated vcf file to pandas df, appends required columns then appends to sqlite databae
    :param vcf_file annotated result from vcf-annotator
    :param id_dict dictionary containing ref, query ids (from detect_result_files)
    :param vcf_pattern the pattern that is to remove from basename to obtain ref_query
    :param comment a string describing additional data to add to the table (or None)
    :param db_file sqlite database file
   :param: table_name name of table in database to use
    :param: all keys - list_ all the keys existing for this type of table
    :param if_exists pandas df.to_sql: if_exists 'replace','append','fail'
    """

    ref_vcf, query_vcf = get_ids(vcf_file, vcf_pattern)

    # Sanity check
    try:
        ref_vcf == id_dict["ref"] and query_vcf == id_dict["query"]
    except NameError:
        sys.exit("the detected reference and query id do not match. Review your command or debug")
    else:
        df = annotated_vcf_to_df(vcf_file)
        file_name = os.path.basename(vcf_file)
        df = df.assign(_REF=id_dict["ref"], _QUERY=id_dict["query"], _RES_FILE=file_name, _COMMENT=comment)

        if not df is None:
            col_to_add = list(set(all_keys) - set(list(df.columns)))
            for value_col in col_to_add:
                df[f'{value_col}'] = None
            df_to_database(df=df, db_file=db_file, table_name=table_name, if_exists=if_exists)
        else:
            print(f"No data to add for {vcf_file}")


## %% stat
def stats_to_df(stat_file, id_dict, stat_pattern, comment = None):
    """
    transforms stat file to pandas df. Appends query and ref names, result file name, and comment field (used for info about analysis)
    :param stat_file nucdiff result gff_file
    :param id_dict dictionary containing ref, query ids (from detect_result_files)
    :param stat_pattern the pattern that is to remove from basename to obtain ref_query
    :param comment a string describing additional data to add to the table (or None)
    :return df (long format)
    """

    df = pd.read_table(stat_file, sep="\t", header=None, names=["param", "value"], skip_blank_lines=True, index_col=None)
    ref_stat, query_stat = get_ids(stat_file, stat_pattern)
    file_name = os.path.basename(stat_file)

    # Sanity - control detected ids are matching
    try:
        ref_stat == id_dict["ref"] and query_stat == id_dict["query"]
    except NameError:
        sys.exit("the detected reference and query id do not match. Review your command or debug")
    else:
        # lines with empty info
        df = df[df.value.notnull()].assign(_REF=id_dict["ref"],
                                           _QUERY=id_dict["query"],
                                           _RES_FILE=file_name,
                                           _COMMENT=comment)
        return df


def wrapper_stat_to_db(stat_file, id_dict, stat_pattern, comment, db_file, table_name, if_exists = 'append'):
    """
    transforms stat file to pandas df then appends to sqlite
    :param stat_file nucdiff result _stat.out
    :param id_dict dictionary containing ref, query ids (from detect_result_files)
    :param stat_pattern the pattern that is to remove from basename to obtain ref_query
    :param comment a string describing additional data to add to the table (or None)
    :param db_file sqlite database file
    :param if_exists pandas df.to_sql: if_exists 'replace','append','fail'
    """
    df = stats_to_df(stat_file = stat_file, id_dict = id_dict,
                     stat_pattern = stat_pattern, comment = comment)
    if not df is None:
        df_to_database(df = df, db_file = db_file, table_name = table_name, if_exists = if_exists)
    else:
        print(f"No data to add for {stat_file}")

########################################################################################################################
# %% SCRIPT
if __name__ == '__main__':
    args = parse_args(sys.argv[1:])

    #%% Output version file - per default
    with open('results_to_db.version', 'w', newline='') as file:
        f.write("results_to_db.py version 0.1")
    file.close()

    # Get the different ref_query patterns
    all_ref_query_patterns = ref_query_patterns(args["resdir"])

    # list where each element is a list of files for each pattern that need to go in the db
    all_files_per_pattern = res_files_per_pattern(args["resdir"], all_ref_query_patterns)

    # flatten list of files containing the results files
    # We do not pair directly, in case order file is not same for each type
    all_files = functools.reduce(operator.iconcat, all_files_per_pattern, [])

    # Some keys might not be common for all results files
    # 1. Creating dictionary with all results files per type for the respective tables:
    res_files_dict = detect_result_files(all_files)
    # 2. Result files per type table - files organized in same order
    id_dict = res_files_dict["id"]
    query_files_dict = res_files_dict["query_files"]
    ref_files_dict = res_files_dict["ref_files"]
    stat_files_dict = res_files_dict["stat_files"]
    vcf_files_dict = res_files_dict["annotated_vcf_files"]

    # 3. Get all the keys for each type of table to create and create the tables using the complete set of keys
    ## %% the query_files to db
    for table in query_files_dict.keys():
        # list of keys
        list_files = query_files_dict.get(table)[0]
        key_list = unique_df_type_keys(list_files, "gff")
        gff_pattern = query_files_dict.get(table)[1]

        for i in range(0, len(list_files)):
            # because ordered previously
            each_id_dict = {"ref": id_dict.get("ref")[i], "query": id_dict.get("query")[i]}
            wrapper_gff_to_db(list_files[i],
                              each_id_dict,
                              gff_pattern,
                              comment=args["comment"],
                              db_file=args["database"],
                              table_name=table,
                              all_keys=key_list,
                              if_exists='append')
    ## %% the ref_files to db
    for table in ref_files_dict.keys():
        list_files = ref_files_dict.get(table)[0]
        key_list = unique_df_type_keys(list_files, "gff")
        gff_pattern = ref_files_dict.get(table)[1]

        # works because ordered previously
        for i in range(0, len(list_files)):
            each_id_dict = {"ref": id_dict.get("ref")[i], "query": id_dict.get("query")[i]}
            wrapper_gff_to_db(list_files[i],
                              each_id_dict,
                              gff_pattern,
                              comment=args["comment"],
                              db_file= args["database"],
                              table_name=table,
                              all_keys=key_list,
                              if_exists='append')

    ## %% the stat_file to db - no need key list (param on rows)
    for table in stat_files_dict.keys():
        list_files = stat_files_dict.get(table)[0]
        stat_pattern = stat_files_dict.get(table)[1]

        for i in range(0, len(list_files)):
            each_id_dict = {"ref": id_dict.get("ref")[i], "query": id_dict.get("query")[i]}
            wrapper_stat_to_db(stat_file=list_files[i],
                               id_dict=each_id_dict,
                               stat_pattern=stat_pattern,
                               comment=args["comment"],
                               db_file=args["database"],
                               table_name=table,
                               if_exists='append')

    ## %% the annotated_vcf to db
    for table in vcf_files_dict.keys():
        list_files = vcf_files_dict.get(table)[0]
        key_list = unique_df_type_keys(list_files, "vcf")
        vcf_pattern = vcf_files_dict.get(table)[1]



        for i in range(0, len(list_files)):
            each_id_dict = {"ref": id_dict.get("ref")[i], "query": id_dict.get("query")[i]}
            wrapper_vcf_to_db(vcf_file=list_files[i],
                              id_dict=each_id_dict,
                              vcf_pattern=vcf_pattern,
                              comment=args["comment"],
                              db_file=args["database"],
                              table_name=table,
                              all_keys=key_list,
                              if_exists='append')


