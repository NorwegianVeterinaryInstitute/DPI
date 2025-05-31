// import individual sqlite files into a postgres database

process IMPORT_SQLITE_TO_PG {
    label 'with_postgres'
    tag "IMPORT PG at ${pg_instance_path} on port ${pg_port}"
    debug "${params.debug}"
    //    tag "${sample}" 

    input:



}