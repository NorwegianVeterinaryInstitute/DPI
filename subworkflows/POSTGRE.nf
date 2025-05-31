// subworkflows/process_with_temp_pg.nf
nextflow.enable.dsl=2

// Import module processes
include { SETUP_POSTGRES } from '../modules/local_pg/setup_postgres.nf'
//include { IMPORT_SQLITE_TO_PG } from '../modules/local_pg/import_sqlite_to_pg.nf'
// include { EXPORT_PG_TO_DUCKDB } from '../modules/local_pg/export_pg_to_duckdb.nf'
// include { STOP_CLEAN_PG } from '../modules/local_pg/stop_clean_postgre.nf'


workflow POSTGRE {
    take:
        
        pg_instance_path        // Path for PGDATA (e.g., "$workDir/pg_temp/\$workflow.runName")
        pg_port                 // Integer for PostgreSQL port
        pg_shutdown_signal_file // path for the shutdown signal file
        //sqlite databases to be imported - we will need parallel processing 
        // we need to setup the max of the parallel processes for the sqlite import  (max 50 files)
        chunked_sqlite_dbs_ch // channel emitting: [ sqlite_file1, sqlite_file2, ... ]
        // sqlite_files_grouped_ch // Channel emitting: [ target_pg_table_name, [sqlite_file1, sqlite_file2, ...] ]


    main:

        // setup paths for temporary PostgreSQL instance and shutdown signal in nextflow.config


        // 1. Setup PostgreSQL
         // SETUP_POSTGRES now emits a map of connection parameters directly via 'connection_params'
        // and the server log file path via 'server_log_file'.
        setup_out_ch = SETUP_POSTGRES(
            params.pg_instance_path, params.pg_port, file(params.pg_shutdown_signal_file)
        )

        //This channel emits the connection parameters map
        // pg_params_ch = setup_out_ch.connection_params 

        pg_params_ch = setup_out_ch.pg_server_details
        pg_params_ch.view()

        

        // This channel emits the server log file
        setup_out_ch.server_log_file.view()

        // HERE IS WHAT HAPPENS with postgreSQL:

        // // 2. Create schema and import SQLite to PostgreSQL - incl. adding columns
        // // python script 
        // // sqlite_files_grouped_ch emits: [ pg_target_table, [list_of_files_for_that_table] ]
        // imported_acks_grouped_ch = sqlite_files_grouped_ch.flatMap { pg_target_name, list_of_sqlite_files ->
        //     // For each group, create a channel of its individual SQLite files
        //     individual_sqlite_file_ch = Channel.fromList(list_of_sqlite_files)

        //     // Map each SQLite file to an import process
        //     per_file_ack_ch = individual_sqlite_file_ch.combine(pg_params_ch).map { sqlite_file, pg_params_map ->
        //         IMPORT_SQLITE_TO_PG(
        //             pg_params_map,
        //             pg_target_name,
        //             sqlite_file,
        //             schemas_ready_signal_ch // Dependency: ensure schemas are created first
        //         )
        //     }
        //     // Collect all acknowledgements for the current pg_target_name
        //     // Output: [ pg_target_name, [ [pg_target_name, ack_file1], [pg_target_name, ack_file2], ... ] ]
        //     per_file_ack_ch.collect().map { collected_acks -> tuple(pg_target_name, collected_acks) }
        // }


        // // 3. Export from PostgreSQL to DuckDB
        // // imported_acks_grouped_ch emits: [ pg_target_name, list_of_import_ack_outputs ]
        // duckdb_files_ch = imported_acks_grouped_ch.combine(pg_params_ch).map { pg_table, import_acks, pg_params_map ->
        //     EXPORT_PG_TO_DUCKDB(
        //         pg_params_map,
        //         pg_table
        //         // The import_acks serves as the dependency signal implicitly by being an input
        //     )
        // }

        // 4. Creates a stop signal to stop the postgres server that is run in the SETUP_POSTGRES process
        //  It should remove removes the temporary pg database (maybe clean logs)

        // 3. Workflow Event Handlers to Create the Shutdown Signal File
    workflow.onComplete {
        println "[POSTGRE WORKFLOW COMPLETED] Creating PostgreSQL shutdown signal..."
        def signal_file = file(params.pg_shutdown_signal_file)
        // Ensure parent directory exists (might be needed if workDir structure is deep)
        if (!signal_file.getParentFile().exists()) {
            signal_file.getParentFile().mkdirs()
        }
        signal_file.text = "Shutdown triggered by POSTGRE workflow completion at ${new Date()}" // Create the file
        println "PostgreSQL shutdown signal created at: ${signal_file}"
        // The SETUP_POSTGRES process will see this file, stop PostgreSQL, and then exit its own SLURM job.
        // If pg_instance_path (PGDATA) was inside SETUP_POSTGRES's task workDir, SLURM + Nextflow handle its cleanup.
        // If pg_instance_path was an absolute path elsewhere (like in the main workDir),
        // you might add an explicit 'rm -rf ${current_pg_instance_path}' here, but ensure PG is stopped first.
        // For simplicity, it's often best if pg_instance_path is within what SETUP_POSTGRES "owns".
        // The current setup where current_pg_instance_path is passed to SETUP_POSTGRES means SETUP_POSTGRES
        // should ideally clean it up after stopping the server, before its script exits.
    }

    workflow.onError {
        println "[POSTGRE WORKFLOW ERROR] Creating PostgreSQL shutdown signal due to error..."
        def signal_file = file(params.pg_shutdown_signal_file)
        if (!signal_file.getParentFile().exists()) {
            signal_file.getParentFile().mkdirs()
        }
        signal_file.text = "Shutdown triggered by POSTGRE workflow error at ${new Date()}"
        println "PostgreSQL shutdown signal created at: ${signal_file}"
        // Similar considerations for cleaning up pg_instance_path if needed.
        }

    emit:
        //postgres_params      = pg_params_ch              // Emit PG params map (as a channel)
        //postgres_server_log  = setup_out_ch.server_log_file // Emit the main PG server log file path
        //final_duckdb_files   = duckdb_files_ch.collect() // Emit a list of all created DuckDB files
}