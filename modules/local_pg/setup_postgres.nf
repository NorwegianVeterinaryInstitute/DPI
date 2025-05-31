// modules/local_pg/setup_postgres.nf
nextflow.enable.dsl=2
 
process SETUP_POSTGRES {
    label 'pg_server_host' // Label for targeting with 'withLabel' in nextflow.config
    tag "PG Server on ${pg_instance_path.name} port ${pg_port}" // Updated tag for clarity

    input:
    path pg_instance_path  // Path for PGDATA, e.g., work/pg_temp_instances/workflow_run_name
    val pg_port            // Integer for the PostgreSQL port
    path shutdown_signal_file_to_watch     // Path to a file that will signal the process to stop PostgreSQL server

    output:
    // Individual parameter files that will be used to construct the connection map later
    path "pg_host.txt", emit: host_file         // Will contain 'localhost' for clients on the same node
    path "pg_port.txt", emit: port_file         // Will contain the port number
    path "pg_user.txt", emit: user_file         // Will contain the database user
    path "pg_node.txt", emit: node_name_file    // Will contain the ACTUAL hostname of this node (for SLURM --nodelist)
    path "pg_dbname.txt", emit: dbname_file     // Will contain the database name
    path "pg_pgdata.txt", emit: pgdata_file     // Will contain the PGDATA path
    
    path "logfile.log", emit: server_log_file   // The PostgreSQL server log

    // This tuple output is what the subworkflow will primarily use.
    // It groups all parameter files and the log file.
    // We'll construct the map from these files in the subworkflow.
    tuple path("pg_host.txt"), path("pg_port.txt"), path("pg_user.txt"), \
          path("pg_node.txt"), path("pg_dbname.txt"), path("pg_pgdata.txt"), \
          path("logfile.log"), emit: pg_server_details


    script:
    // Groovy variable for initdb username, determined before shell script runs
    def pg_user_for_initdb = System.getProperty("user.name") ?: "nextflow_user"
    def db_name_to_use = pg_user_for_initdb // Or 'postgres' or a fixed name

    """
    # Exit immediately if a command exits with a non-zero status.
    set -e 
    
    echo "--- Starting SETUP_POSTGRES ---"
    echo "Target PGDATA directory: ${pg_instance_path}"
    echo "Target Port: ${pg_port}"
    echo "User for initdb: ${pg_user_for_initdb}"

    # 1. Determine Actual Node Hostname - the name SLURM clients will use to target this node
    ACTUAL_NODE_HOSTNAME=\$(hostname -f)
    # ... (Initial PGDATA prep, initdb, conf changes, pg_ctl start as before) ...
    # ... (Ensure listen_addresses = 'localhost' is set in postgresql.conf) ...
    # ... (Ensure parameter files like pg_host.txt, pg_node.txt are written) ...
    if [ -z "\${ACTUAL_NODE_HOSTNAME}" ]; then
        # Fallback if hostname -f fails (shouldn't usually happen on HPC)
        ACTUAL_NODE_HOSTNAME=\$(hostname)
    fi
    
    echo "This process is running on node: \${ACTUAL_NODE_HOSTNAME}"   
    echo "PostgreSQL server confirmed running. PID: \$(head -n 1 "${pg_instance_path}/postmaster.pid")"
    echo "Watching for shutdown signal file: ${shutdown_signal_file_to_watch}" 


    # 2. Prepare PGDATA directory
    if [ -d "${pg_instance_path}" ]; then
      echo "Warning: PGDATA directory ${pg_instance_path} already exists."
      echo "Attempting to stop any existing server and clean up..."
      # Use timeout for pg_ctl stop in case it hangs on a defunct instance
      timeout 30s pg_ctl -D "${pg_instance_path}" -o "-p ${pg_port}" stop || echo "INFO: PG stop command timed out, failed, or server was not running."
      rm -rf "${pg_instance_path}/*"
      echo "Cleaned inside ${pg_instance_path}."
    else
      mkdir -p "${pg_instance_path}"
      echo "Created PGDATA directory: ${pg_instance_path}"
    fi

    # 3. Initialize PostgreSQL Database Cluster
    initdb --username=${pg_user_for_initdb} --pgdata="${pg_instance_path}" --auth=trust --no-locale --encoding=UTF8
    echo "initdb complete."

    # 4. Configure PostgreSQL (postgresql.conf and pg_hba.conf)
    echo "port = ${pg_port}" >> "${pg_instance_path}/postgresql.conf"
    # Listen on 'localhost' because we aim for client processes to run on the SAME node.
    # If co-location fails and clients are on other nodes, this 'localhost' would prevent connection.
    # The robust co-location strategy makes 'localhost' the correct & secure choice here.
    echo "listen_addresses = 'localhost'" >> "${pg_instance_path}/postgresql.conf"
    echo "PostgreSQL configured to listen on localhost:${pg_port}"

    # 5. Start PostgreSQL Server
    pg_ctl -D "${pg_instance_path}" -l "${pg_instance_path}/logfile.log" -o "-p ${pg_port}" start
    echo "PostgreSQL server start command issued."
    # Add a small delay and check status to ensure it started cleanly
    sleep 5
    pg_ctl -D "${pg_instance_path}" status || (echo "ERROR: PostgreSQL server failed to start cleanly. Check logfile.log." && exit 1)
    echo "PostgreSQL server confirmed running."

    # 6. Write connection parameters to files for output
    # 'localhost' is the host clients on this same node will use
    echo "localhost" > pg_host.txt
    echo "${pg_port}" > pg_port.txt
    echo "${pg_user_for_initdb}" > pg_user.txt # User to connect as
    echo "\${ACTUAL_NODE_HOSTNAME}" > pg_node.txt   # Actual node (for SLURM --nodelist of clients)
    echo "${db_name_to_use}" > pg_dbname.txt   # Database to connect to
    echo "${pg_instance_path}" > pg_pgdata.txt # PGDATA path

    # Copy the server log to the current Nextflow task work directory for easy capture
    cp "${pg_instance_path}/logfile.log" "logfile.log"
    echo "Parameter files written. Server log copied."

    # 7. Wait for shutdown signal
    while true; do
        if [ -f "${shutdown_signal_file_to_watch}" ]; then # Check for the specific file passed as input
            echo "Shutdown signal '${shutdown_signal_file_to_watch}' received."
            echo "Stopping PostgreSQL server at PGDATA ${pg_instance_path}..."
            pg_ctl -D "${pg_instance_path}" -o "-p ${pg_port}" -m fast stop
            echo "PostgreSQL server stopped."

            rm -f "${shutdown_signal_file_to_watch}" # Clean up the signal file
            echo "Signal file removed."

            
            # Optional: Clean up the PGDATA directory itself by this process before exiting
            # This is good if pg_instance_path is an absolute path managed by the main workflow
            # If pg_instance_path is *inside* this task's workDir, SLURM/Nextflow will clean it eventually.
            # echo "Cleaning up PGDATA directory: ${pg_instance_path}..."
            # rm -rf "${pg_instance_path}"
            # echo "PGDATA directory removed."
            
            break # Exit the loop, allowing the script and SLURM job to finish
        fi
        sleep 15 # Check every 15 seconds
    done

    echo "--- SETUP_POSTGRES script finished ---"
    """
}



