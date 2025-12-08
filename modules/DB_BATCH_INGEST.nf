// results to postgreSQL database - by chunks of xx files
// TODO review

process DB_BATCH_INGEST {
    executor 'local' 

    // Mount the socket directory so Python can find the DB
    containerOptions '-B $HOME/pg_run:/var/run/postgresql' 
    container 'postgres_python.sif' // Image with Python3 + psycopg2

    
    input:
    path json_files // This receives a LIST of xx files
    val ready_signal // ensure that the process does not start before the db is ready

    script:
    """
    python3  ${projectDir}/bin/ingest_batch.py ${json_files}
    """
}