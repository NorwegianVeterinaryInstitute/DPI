// Export temporary postgress database - all tables to duckdb

process EXPORT_PG_TO_DUCKDB  {
    label 'with_postgres'
    tag "EXPORT PG at ${pg_instance_path} on port ${pg_port}"
    debug "${params.debug}"
    //    tag "${sample}" 

    input:



}
