import argparse
import os
import sys
import re
import pandas as pd
import gffpandas.gffpandas as gffpd
import sqlalchemy
import glob


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
def detect_result_files(res_files_element):
    """
    organize the detected result files for ONE ref_query pattern and create a dictionary so it can be wrangled correctly
    builds on res_files_per_pattern
    :res_files_element all the result files for one pattern (from res_files_per_pattern fun)
    :returns dictionary of list file paths to analyze in different categories id(ref,query), query_files, ref_files, stat_file
    """
    # should be better with case
    for f in res_files_element:
        if "_query_blocks.gff" in f:
            query_blocks_file = str(f)
        elif "_query_snps.gff" in f:
            query_snps_gff_file = str(f)
        elif "_query_struct.gff" in f:
            query_struct_file = str(f)
        elif "_query_additional.gff" in f:
            query_additional_file = str(f)
        elif "_query_snps_annotated.vcf" in f:
            query_snps_annotated_file = str(f)
        # ref
        elif "_ref_blocks.gff" in f:
            ref_blocks_file = str(f)
        elif "_ref_snps.gff" in f:
            ref_snps_gff_file = str(f)
        elif "_ref_struct.gff" in f:
            ref_struct_file = str(f)
        elif "_ref_additional.gff" in f:
            ref_additional_file = str(f)
        elif "_ref_snps_annotated.vcf" in f:
            ref_snps_annotated_file = str(f)
        # stat
        elif "_stat.out" in f:
            stat_file = str(f)
    stat_files = { 'stat_file': (stat_file, "_stat.out")}
    query_files = {'query_blocks' : (query_blocks_file, "_query_blocks.gff"),
                   'query_snps_gff': (query_snps_gff_file, "_query_snps.gff"),
                   'query_struct' : (query_struct_file, "_query_struct.gff"),
                   'query_additional': (query_additional_file, "_query_additional.gff")}
    ref_files = {'ref_blocks': (ref_blocks_file,"_ref_blocks.gff"),
                 'ref_snps_gff': (ref_snps_gff_file,"_ref_snps.gff"),
                 'ref_struct' : (ref_struct_file,"_ref_struct.gff"),
                 'ref_additional': (ref_additional_file,  "_ref_additional.gff")}

    annotated_vcf_files = {"ref_snps_annotated": (ref_snps_annotated_file,  "_ref_snps_annotated.vcf"),
                          "query_snps_annotated" : (query_snps_annotated_file, "_query_snps_annotated.vcf")}

    # guet the ref and query id
    prefix = re.sub("_stat.out", '', os.path.basename(stat_file))
    ref_id, query_id = re.split('_', prefix)
    id = {'ref': ref_id, 'query': query_id}

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

def wrapper_vcf_to_db(vcf_file, id_dict, vcf_pattern, comment, db_file, table_name, if_exists = 'append'):
    """
    transforms annotated vcf file to pandas df, appends required columns then appends to sqlite databae
    :param vcf_file annotated result from vcf-annotator
    :param id_dict dictionary containing ref, query ids (from detect_result_files)
    :param vcf_pattern the pattern that is to remove from basename to obtain ref_query
    :param comment a string describing additional data to add to the table (or None)
    :param db_file sqlite database file
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
            df_to_database(df = df, db_file = db_file, table_name = table_name, if_exists = if_exists)
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
## Testing
os.chdir("/home/vi2067/Documents/onedrive_sync/NEW_WORK/2_Projects/2023/1_2023_Lm_ost_er_ikke_ost/DPI/work/98/13b009471d56dd4a50ff859d89ae11")
args = {}
args["resdir"] = os.getcwd()
args["comment"] = "test comment"
args["database"] = "again2.sqlite"

# Get the different ref_query_patterns
all_ref_query_patterns = ref_query_patterns(args["resdir"])

# list where each element is a list of files for each pattern that need to go in the db
all_files_per_pattern = res_files_per_pattern(args["resdir"], all_ref_query_patterns)

# now we need for each element of list:
for file_set in all_files_per_pattern:
    ## %% getting results files to add to database for each file set
    res_files_dict = detect_result_files(file_set)
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



