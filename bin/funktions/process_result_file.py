# Wrapper : processing each type of results files. A single file at the time
import os 
import json

import funktions
from funktions.json_to_df import prep_info_df as prep_info_df
from funktions.json_to_df import prep_features_df as prep_features_df
from funktions.json_to_df import prep_sequences_df as prep_sequences_df 
from funktions.gff_to_df import gff_to_df as gff_to_df
from funktions.vcf_to_df import vcf_to_df as vcf_to_df
from funktions.create_or_append_table import create_or_append_table as create_or_append_table
    
def process_result_file(file_path, result_type, identifier, db_conn, comment):
    """
    Processes a single result file, transforms it into a table\n
    If created, a new column will be created and appended to the database\n
    NaN will be used to fill the column for previous records.\n
    Then the result table will be inserted it into the database.

    Args:
        file_path (str): Path to the result file.
        result_type (str): The type of result (e.g., "json").
        identifier (str): The identifier (pair or sample_id).
        db_conn (sqlite3.Connection): The database connection.
        comment (str): Comment for the database entries. Please set to NULL if not used.
    """
    file_name = os.path.basename(file_path)
    print(f"Processing file: {file_name} for {identifier}")

    try:
        if result_type == "json":
            with open(file_path, "r") as f:
                data = json.load(f)

            # 3 types of data to extract for the json fil
            try:
                # Process info data
                info_df = prep_info_df(data, identifier)
                create_or_append_table(info_df, 'info', identifier, file_name, db_conn)
            except Exception as e:
                print(f"Error processing info_df for {identifier}: {e}")

            try:
                # Process features data
                features_df = prep_features_df(data, identifier)
                create_or_append_table(
                    features_df, 'features', identifier, file_name, db_conn
                )
            except Exception as e:
                print(f"Error processing features_df for {identifier}: {e}")
                
            try:
                # Process sequences data
                sequences_df = prep_sequences_df(data, identifier)
                create_or_append_table(
                    sequences_df, 'sequences', identifier, file_name, db_conn
                )
            except Exception as e:
                print(f"Error processing sequences_df for {identifier}: {e}")

        elif result_type == "gff":           
            # processing each subtype of gff file 
            df = gff_to_df(file_path)
            
            if "_query_blocks" in file_name: 
                create_or_append_table(df, 'query_blocks', identifier, file_path, db_conn)
            elif "_query_snps" in file_name:
                create_or_append_table(df, 'query_snps', identifier, file_path, db_conn)
            elif "_query_struct" in file_name:
                create_or_append_table(df, 'query_struct', identifier, file_path, db_conn)
            elif "_query_additional" in file_name:
                create_or_append_table(df, 'query_additional', identifier, file_path, db_conn)
            elif "_query_snps_annotated" in file_name:
                create_or_append_table(df, 'query_snps_annotated', identifier, file_path, db_conn)
            elif "_ref_blocks" in file_name:
                create_or_append_table(df, 'ref_blocks', identifier, file_path, db_conn)
            elif "_ref_snps" in file_name:
                create_or_append_table(df, 'ref_snps', identifier, file_path, db_conn)
            elif "_ref_struct" in file_name:
                create_or_append_table(df, 'ref_struct', identifier, file_path, db_conn)
            elif "ref_additional" in file_name:
                create_or_append_table(df, 'ref_additional', identifier, file_path, db_conn)
            else:
                print(f"Warning: Unknown GFF subtype for {result_type} for {identifier}. Skipping {file_path}.")
                return 
            
        elif result_type == "vcf":
            df = vcf_to_df(file_path)
            
            # processing each subtype of vcf file
            if "_ref_snps_annotated" in file_name:
                create_or_append_table(df, 'ref_snps_annotated', identifier, file_path, db_conn)
            elif "_query_snps_annotated" in file_name:
                create_or_append_table(df, 'query_snps_annotated', identifier, file_path, db_conn)
            else:
                print(f"Warning: Unknown VCF subtype for {result_type} for {identifier}. Skipping {file_path}.")
                return
            
        # elif result_type == "stat":
        #     df = stat_to_df(file_path)
        #     if "_stat.out in file_name":
        #         create_or_append_table(df, 'stat_file', identifier, file_path, db_conn)
        #     else: 
        #         print(f"Warning: Unknown stat subtype for for {result_type} for {identifier}. Skipping {file_path}.")
        #         pass 
                
        # TODO add a comment table for each indentifier / processing 
                
    
        db_conn.commit()
        print(f"Processed and inserted: {file_path} for identifier {identifier}")

    except Exception as e:
        print(f"Error processing {file_path} for identifier {identifier}: {e}")
        db_conn.rollback()



