#!/usr/bin/env python3
# Gemini PostgreSQL Ingestion Script 
# TODO Need to review and modify
import sys
import json
import psycopg2
from pathlib import Path

# Database connection params (Env vars or hardcoded)
DB_PARAMS = {
    "dbname": "postgres",
    "user": "postgres",
    "host": "/var/run/postgresql", # Connect via Unix Socket (fastest/secure)
}

def ingest_batch(file_list):
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()
    
    # Prepare a list of tuples for bulk insertion
    # Format: (sample_id, json_data_string)
    records_to_insert = []
    
    for file_path in file_list:
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                
                # Extract fixed ID if exists, or use filename
                sample_id = data.pop('sample_id', Path(file_path).stem)
                
                # The rest of the data (variable columns) goes into JSONB
                records_to_insert.append((sample_id, json.dumps(data)))
        except Exception as e:
            print(f"Error reading {file_path}: {e}", file=sys.stderr)

    # Bulk Insert using execute_values or simple executemany
    insert_query = """
    INSERT INTO pipeline_results (sample_id, data) 
    VALUES (%s, %s)
    """
    
    try:
        cur.executemany(insert_query, records_to_insert)
        conn.commit()
        print(f"Successfully inserted {len(records_to_insert)} records.")
    except Exception as e:
        conn.rollback()
        print(f"Transaction failed: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    # Nextflow passes file paths as arguments
    files = sys.argv[1:]
    ingest_batch(files)