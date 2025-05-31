// stops and cleans up a PostgreSQL temporary instance 
// I think the logs should be kept for debugging, so we won't delete them.


process STOP_CLEAN_POSTGRES {
    label 'with_postgres'
    tag "STOP PG at ${pg_instance_path} on port ${pg_port}"
    debug "${params.debug}"
    //    tag "${sample}" 

    input:



}