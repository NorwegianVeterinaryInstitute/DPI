// testing deterministic ordering of files in batches for bulk loading to Postgres
process POSTGRES_BATCH_TEST {
    tag "Batch ${batch_index}"
    echo true // Useful to see output in logs during dev

    input:
    // Takes a tuple: a unique index for the batch, and the list of files
    tuple val(batch_index), val(meta_list), path(json_files)

    script:
    """
    echo "Processing Batch ${batch_index} containing ${json_files.size()} files..."
    
    # Here you would run your python/groovy script to bulk load the JSONs
    # python db_loader.py --files ${json_files}
    
    # For now, listing them to prove deterministic order:
    ls -1 *.json
    """
}