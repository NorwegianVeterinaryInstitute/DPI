# Relics
import sqlalchemy
# TEST
    query_files_test = all_files_per_pattern_set[0]
    print(query_files_test)
    type(query_files_test)
    list(query_files_test)
    if any("_query_additional.gff" in element for element in query_files_test):
        print("True")

    for f in all_files_per_pattern_set:
        #query
        if any("_query_blocks.gff" in element for element in f):
            query_blocks_files = list(f)
    detect_result_files(query_files_test)
    for file_set in all_files_per_pattern_set:
        print(file_set)
        #res_files_dict = detect_result_files(file_set)
# new writing using tuples
from more_itertools import batched
import numpy as np

#all_files_per_pattern_set = list(zip(*all_files_per_pattern))
    #print(all_files_per_pattern_set)


# old
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

## getting the unique keys per type of data that will go in same df


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

# Test
query_files_dict.keys()
test_query_files = query_files_dict.get("query_blocks")
test_vcf_files = vcf_files_dict.get("ref_snps_annotated")
test_stat_files = stat_files_dict.get("stat_file")

get("stat_files"]
print(test_query_files[0]) # list of files
test_query_files[0][0] # first element
extra_col = ["_REF", "_QUERY", "_RES_FILE", "_COMMENT" ]

unique_df_type_keys(test_query_files[0], "gff", extra_col)
unique_df_type_keys(test_vcf_files[0], "vcf", extra_col)
unique_df_type_keys(test_stat_files[0], "stat", extra_col)

# hum, wont work ...

# def create_tables(db, table_name, all_keys):
#     """
#     :param: db path data table
#     :param: table name : name of table to create
#     :param: all_keys (all the keys that are found in this type of table)
#     """
#     conn_string = f"sqlite:///{db}"
#     engine = sqlalchemy.create_engine(conn_string)
#
#     # from https://stackoverflow.com/questions/33053241/sqlalchemy-if-table-does-not-exist
#     if not sqlalchemy.inspect(engine).has_table(table_name):
#         metadata = sqlalchemy.MetaData(engine)
#         sqlalchemy.Table(table_name, metadata, all_keys)
#         metadata.create_all()
#create_tables("todays_test.sqlite", "query_blocks", test_keys_gff)
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
        for col in col_to_add:
            df.insert(cpl, None)
        df_to_database(df = df, db_file = db_file, table_name = table_name, if_exists = if_exists)
    else:
        print(f"No data to add for {gff_file}")

# test
test_keys_gff = unique_df_type_keys(test_query_files[0], "gff", extra_col)
        "query_blocks"

for i in range(0, len(test_query_files[0])):
    each_id_dict = {"ref": id_dict.get("ref")[i], "query": id_dict.get("query")[i]}
    file = test_query_files[0][i]
    gff_pattern = test_query_files[1]
    wrapper_gff_to_db(file, each_id_dict, gff_pattern,
                      comment = "TEST", db_file = "TODAY.sqlite", table_name = "query_blocks",
                      all_keys = test_keys_gff, if_exists='append')





print(id_dict)
    id_dict["ref"][0]
    id_dict[qye]
each_id = {"ref" : id_dict.get("ref")[0], "query" : id_dict.get("query")[0]}
print(each_id)
