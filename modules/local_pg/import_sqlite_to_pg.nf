// import individual sqlite files into a postgres database

process IMPORT_SQLITE_TO_PG {
    label 'pg_client'
    // tag "IMPORT PG at ${pg_instance_path} on port ${pg_port}"
    debug "${params.debug}"
    // ... other inputs like pg_params_map, sqlite_file, target_pg_table ...
    input:
    // ...
    path pg_node_info_file // This receives 'pg_node.txt' from SETUP_POSTGRES need in all client processes 

    script:
    // This script doesn't directly use pg_node_info_file,
    // but its presence as an input allows clusterOptions to use it.
    // ... your import logic ...
    """
    # ...
    """
}